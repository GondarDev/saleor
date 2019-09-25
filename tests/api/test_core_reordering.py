import pytest

from saleor.graphql.core.utils.reordering import perform_reordering
from saleor.product import models

SortedModel = models.AttributeValue


def _sorted_by_order(items):
    return sorted(items, key=lambda o: o[1])


def _get_sorted_map():
    return list(
        SortedModel.objects.values_list("pk", "sort_order").order_by("sort_order")
    )


@pytest.fixture
def dummy_attribute():
    return models.Attribute.objects.create(name="Dummy")


@pytest.fixture
def sorted_entries_seq(dummy_attribute):
    attribute = dummy_attribute
    values = SortedModel.objects.bulk_create(
        [
            SortedModel(
                attribute=attribute, slug=f"value-{i}", name=f"Value-{i}", sort_order=i
            )
            for i in range(6)
        ]
    )
    return list(values)


@pytest.fixture
def sorted_entries_gaps(dummy_attribute):
    attribute = dummy_attribute
    values = SortedModel.objects.bulk_create(
        [
            SortedModel(
                attribute=attribute, slug=f"value-{i}", name=f"Value-{i}", sort_order=i
            )
            for i in range(0, 12, 2)
        ]
    )
    return list(values)


def test_reordering_sequential(sorted_entries_seq):
    """
    Ensures the reordering logic works as expected. This test simply provides
    sequential sort order values and try to reorder them.
    """
    qs = SortedModel.objects
    nodes = sorted_entries_seq

    operations = {nodes[5].pk: -1, nodes[2].pk: +3}

    expected = _sorted_by_order(
        [
            (nodes[0].pk, 0),
            (nodes[1].pk, 1),
            (nodes[2].pk, 2 + 3),
            (nodes[3].pk, 3 - 1),
            (nodes[4].pk, 4 + 1 - 1),
            (nodes[5].pk, 5 - 1 - 1),
        ]
    )

    perform_reordering(qs, operations)

    actual = _get_sorted_map()
    assert actual == expected


def test_reordering_non_sequential(sorted_entries_gaps):
    """
    Ensures that reordering non-sequential sort order values is properly
    handled. This case happens when an item gets deleted, creating gaps between values.
    """
    qs = SortedModel.objects
    nodes = sorted_entries_gaps

    operations = {nodes[5].pk: -1, nodes[2].pk: +3}

    expected = _sorted_by_order(
        [
            (nodes[0].pk, 0),
            (nodes[1].pk, 2),
            (nodes[2].pk, 4 + (3 * 2) - 1),
            (nodes[3].pk, 6 - 1),
            (nodes[4].pk, 8 + 1 - 1),
            (nodes[5].pk, 10 - (1 * 2) - 1),
        ]
    )

    perform_reordering(qs, operations)

    actual = _get_sorted_map()
    assert actual == expected


@pytest.mark.parametrize(
    "operation, expected_operations",
    [((0, +5), (+5, -1, -1, -1, -1, -1)), ((5, -5), (+1, +1, +1, +1, +1, -5))],
)
def test_inserting_at_the_edges(sorted_entries_seq, operation, expected_operations):
    """
    Ensures it is possible to move an item at the top and bottom of the list.
    """
    qs = SortedModel.objects
    nodes = sorted_entries_seq

    target_node_pos, new_rel_sort_order = operation

    operations = {nodes[target_node_pos].pk: new_rel_sort_order}

    expected = _sorted_by_order(
        [
            (node.pk, node.sort_order + op)
            for node, op in zip(nodes, expected_operations)
        ]
    )

    perform_reordering(qs, operations)

    actual = _get_sorted_map()
    assert actual == expected


def test_reordering_out_of_bound(sorted_entries_seq):
    """
    Ensures it is not possible to manually create gaps or for the users
    to insert anywhere they want, e.g. -1000, which could create a mess
    into the database.
    """
    qs = SortedModel.objects
    nodes = sorted_entries_seq

    operations = {nodes[5].pk: -100, nodes[0].pk: +100}

    expected = _sorted_by_order(
        [
            (nodes[0].pk, 0 + 5),
            (nodes[1].pk, 1),
            (nodes[2].pk, 2),
            (nodes[3].pk, 3),
            (nodes[4].pk, 4),
            (nodes[5].pk, 5 - 5),
        ]
    )

    perform_reordering(qs, operations)

    actual = _get_sorted_map()
    assert actual == expected


def test_reordering_null_sort_orders(dummy_attribute):
    """
    Ensures null sort orders values are getting properly ordered (by ID sorting).
    """
    attribute = dummy_attribute
    qs = SortedModel.objects

    non_null_sorted_entries = list(
        qs.bulk_create(
            [
                SortedModel(
                    pk=1, attribute=attribute, slug="1", name="1", sort_order=1
                ),
                SortedModel(
                    pk=2, attribute=attribute, slug="2", name="2", sort_order=0
                ),
            ]
        )
    )

    null_sorted_entries = list(
        qs.bulk_create(
            [
                SortedModel(
                    pk=5, attribute=attribute, slug="5", name="5", sort_order=None
                ),
                SortedModel(
                    pk=4, attribute=attribute, slug="4", name="4", sort_order=None
                ),
                SortedModel(
                    pk=3, attribute=attribute, slug="3", name="3", sort_order=None
                ),
            ]
        )
    )

    operations = {null_sorted_entries[0].pk: -2}

    expected = [
        (non_null_sorted_entries[1].pk, 0),
        (non_null_sorted_entries[0].pk, 1),
        (null_sorted_entries[0].pk, 2),
        (null_sorted_entries[2].pk, 3),
        (null_sorted_entries[1].pk, 4),
    ]

    perform_reordering(qs, operations)

    actual = _get_sorted_map()
    assert actual == expected


def test_reordering_nothing(sorted_entries_seq, django_assert_num_queries):
    """
    Ensures giving operations that does nothing, are skipped. Thus only one query should
    have been made: fetching the nodes.
    """
    qs = SortedModel.objects
    pk = sorted_entries_seq[0].pk
    operations = {pk: 0}

    with django_assert_num_queries(1) as ctx:
        perform_reordering(qs, operations)

    assert ctx[0]["sql"].startswith("SELECT "), "Should only have done a SELECT"


def test_giving_no_operation_does_no_query(
    sorted_entries_seq, django_assert_num_queries
):
    """Ensures giving no operations runs no queries at all."""

    qs = SortedModel.objects

    with django_assert_num_queries(0):
        perform_reordering(qs, {})


def test_reordering_concurrently(dummy_attribute, django_assert_num_queries):
    """
    Ensures users cannot concurrently reorder, they need to wait for the other one
    to achieve.

    This must be the first thing done before doing anything. For that, we ensure
    the first SQL query is acquiring the lock.
    """

    qs = SortedModel.objects
    attribute = dummy_attribute

    entries = list(
        qs.bulk_create(
            [
                SortedModel(
                    pk=1, attribute=attribute, slug="1", name="1", sort_order=0
                ),
                SortedModel(
                    pk=2, attribute=attribute, slug="2", name="2", sort_order=1
                ),
            ]
        )
    )

    operations = {entries[0].pk: +1}

    with django_assert_num_queries(2) as ctx:
        perform_reordering(qs, operations)

    assert ctx[0]["sql"] == (
        'SELECT "product_attributevalue"."id", "product_attributevalue"."sort_order" '
        'FROM "product_attributevalue" '
        "ORDER BY "
        '"product_attributevalue"."sort_order" ASC NULLS LAST, '
        '"product_attributevalue"."id" ASC FOR UPDATE'
    )
    assert ctx[1]["sql"] == (
        'UPDATE "product_attributevalue" '
        'SET "sort_order" = (CASE WHEN ("product_attributevalue"."id" = 1) '
        'THEN 1 WHEN ("product_attributevalue"."id" = 2) '
        "THEN 0 ELSE NULL END)::integer "
        'WHERE "product_attributevalue"."id" IN (1, 2)'
    )


def test_reordering_deleted_node_from_concurrent(
    dummy_attribute, django_assert_num_queries
):
    """
    Ensures if a node was deleted before locking, it just skip it instead of
    raising an error.
    """

    qs = SortedModel.objects
    attribute = dummy_attribute

    entries = list(
        qs.bulk_create(
            [
                SortedModel(
                    pk=1, attribute=attribute, slug="1", name="1", sort_order=0
                ),
                SortedModel(
                    pk=2, attribute=attribute, slug="2", name="2", sort_order=1
                ),
            ]
        )
    )

    operations = {-1: +1, entries[0].pk: +1}

    with django_assert_num_queries(2) as ctx:
        perform_reordering(qs, operations)

    assert ctx[1]["sql"] == (
        'UPDATE "product_attributevalue" '
        'SET "sort_order" = (CASE WHEN ("product_attributevalue"."id" = 1) '
        'THEN 1 WHEN ("product_attributevalue"."id" = 2) '
        "THEN 0 ELSE NULL END)::integer "
        'WHERE "product_attributevalue"."id" IN (1, 2)'
    )
