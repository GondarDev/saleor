# Generated by Django 3.2.12 on 2022-04-06 17:13

# Same migration as 0020_auto_20220214_1027 but this one fixes the queryset ordering to
# use order_by("pk"). We're adding a new migration as the previous one was already
# applied in some envs.

from collections import defaultdict

from django.db import migrations
from django.db.models import Exists, OuterRef


def fetch_reference_id_from_slug(slug):
    ref_id = slug.split("_")[1]
    return int(ref_id)


def import_attribute_values(attr_values_qs, Model):
    attr_values_to_update = []
    attr_values_to_delete = set()

    attr_value_map = defaultdict(list)

    for attr_value in attr_values_qs:
        ref_id = fetch_reference_id_from_slug(attr_value.slug)
        attr_value_map[ref_id].append(attr_value)

    model_queryset = Model.objects.filter(pk__in=attr_value_map.keys())
    model_in_bulk = model_queryset.in_bulk()

    for attr_value in attr_values_qs:
        model_id = fetch_reference_id_from_slug(attr_value.slug)
        model_instance = model_in_bulk.get(model_id, None)
        if model_instance:
            if Model.__name__ == "Page":
                attr_value.reference_page = model_instance
            if Model.__name__ == "Product":
                attr_value.reference_product = model_instance
            attr_values_to_update.append(attr_value)
        else:
            attr_values_to_delete.add(attr_value.id)

    return attr_values_to_update, attr_values_to_delete


def import_page_attributes_values(AttributeValue, Attribute, Page):
    queryset = AttributeValue.objects.filter(
        Exists(
            Attribute.objects.filter(
                id=OuterRef("attribute_id"), input_type="reference", entity_type="Page"
            )
        )
    )
    for batch_pks in queryset_in_batches(queryset):
        batch = AttributeValue.objects.filter(pk__in=batch_pks)
        attr_values_to_update, attr_values_to_delete = import_attribute_values(
            batch, Page
        )
        AttributeValue.objects.bulk_update(attr_values_to_update, ["reference_page"])
        AttributeValue.objects.filter(pk__in=attr_values_to_delete).delete()


def import_product_attributes_values(AttributeValue, Attribute, Product):
    queryset = AttributeValue.objects.filter(
        Exists(
            Attribute.objects.filter(
                id=OuterRef("attribute_id"),
                input_type="reference",
                entity_type="Product",
            )
        )
    )
    for batch_pks in queryset_in_batches(queryset):
        batch = AttributeValue.objects.filter(pk__in=batch_pks)
        attr_values_to_update, attr_values_to_delete = import_attribute_values(
            batch, Product
        )
        AttributeValue.objects.bulk_update(attr_values_to_update, ["reference_product"])
        AttributeValue.objects.filter(pk__in=attr_values_to_delete).delete()


def migrate_model_field_data(apps, schema):
    AttributeValue = apps.get_model("attribute", "AttributeValue")
    Attribute = apps.get_model("attribute", "Attribute")
    Page = apps.get_model("page", "Page")
    Product = apps.get_model("product", "Product")

    import_page_attributes_values(AttributeValue, Attribute, Page)
    import_product_attributes_values(AttributeValue, Attribute, Product)


def queryset_in_batches(queryset):
    """Slice a queryset into batches.

    Input queryset should be sorted be pk.
    """
    start_pk = 0

    while True:
        qs = queryset.order_by("pk").filter(pk__gt=start_pk)[:2000]
        pks = list(qs.values_list("pk", flat=True))

        if not pks:
            break

        yield pks

        start_pk = pks[-1]


class Migration(migrations.Migration):

    dependencies = [
        ("attribute", "0020_auto_20220214_1027"),
    ]

    operations = [
        migrations.RunPython(
            migrate_model_field_data,
            migrations.RunPython.noop,
        )
    ]
