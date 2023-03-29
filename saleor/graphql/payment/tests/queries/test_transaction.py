from decimal import Decimal

import graphene
import pytest

from .....payment import TransactionEventStatus, TransactionEventType
from .....payment.models import TransactionEvent
from ....core.utils import to_global_id_or_none
from ....tests.utils import assert_no_permission, get_graphql_content

TEST_SERVER_DOMAIN = "testserver.com"

TRANSACTION_QUERY = """
    query transaction($id: ID!){
        transaction(id: $id) {
            id
            createdAt
            actions
            authorizedAmount{
                currency
                amount
            }
            refundedAmount{
                currency
                amount
            }
            canceledAmount{
                currency
                amount
            }
            voidedAmount{
                currency
                amount
            }
            chargedAmount{
                currency
                amount
            }
            authorizePendingAmount{
                currency
                amount
            }
            chargePendingAmount{
                currency
                amount
            }
            refundPendingAmount{
                currency
                amount
            }
            cancelPendingAmount{
                currency
                amount
            }
            events{
                id
                createdAt
                status
                pspReference
                name
                message
                externalUrl
                amount{
                    currency
                    amount
                }
                type
                createdBy{
                    ... on User {
                        id
                    }
                    ... on App {
                        id
                    }
                }
            }
            status
            type
            name
            message
            reference
            order {
                id
            }
            createdBy{
                ... on User {
                    id
                }
                ... on App {
                    id
                }
            }
        }
    }
"""


def _assert_transaction_fields(content, transaction_item, event):
    data = content["data"]["transaction"]
    assert data["id"] == graphene.Node.to_global_id(
        "TransactionItem", transaction_item.token
    )
    assert data["createdAt"] == transaction_item.created_at.isoformat()
    assert data["actions"] == [
        action.upper() for action in transaction_item.available_actions
    ]
    assert (
        data["authorizedAmount"]["amount"] == transaction_item.amount_authorized.amount
    )
    assert data["refundedAmount"]["amount"] == transaction_item.amount_refunded.amount
    assert data["voidedAmount"]["amount"] == transaction_item.amount_canceled.amount
    assert data["canceledAmount"]["amount"] == transaction_item.amount_canceled.amount
    assert data["chargedAmount"]["amount"] == transaction_item.amount_charged.amount
    events_data = [e for e in data["events"] if e["type"] == event.type.upper()]
    assert len(events_data) == 1
    assert events_data[0]["id"] == to_global_id_or_none(event)
    assert data["status"] == transaction_item.status
    assert data["type"] == transaction_item.name
    assert data["name"] == transaction_item.name
    assert data["message"] == transaction_item.message
    if transaction_item.order_id:
        assert data["order"]["id"] == to_global_id_or_none(transaction_item.order)
    else:
        assert data["order"] is None


def _assert_transaction_fields_created_by(content, transaction_item, event, created_by):
    _assert_transaction_fields(content, transaction_item, event)
    data = content["data"]["transaction"]
    assert data["createdBy"]["id"] == to_global_id_or_none(created_by)


def test_transaction_created_by_app_query_by_app(
    app_api_client, transaction_item_created_by_app, permission_manage_payments, app
):
    # given
    event = transaction_item_created_by_app.events.filter(
        type=TransactionEventType.CHARGE_SUCCESS
    ).get()

    variables = {"id": to_global_id_or_none(transaction_item_created_by_app)}

    # when
    response = app_api_client.post_graphql(
        TRANSACTION_QUERY, variables, permissions=[permission_manage_payments]
    )

    # then
    content = get_graphql_content(response)
    _assert_transaction_fields_created_by(
        content,
        transaction_item_created_by_app,
        event,
        app,
    )


def test_transaction_creted_by_app_query_no_order(
    app_api_client, transaction_item_created_by_app, permission_manage_payments, app
):
    # given
    transaction_item_created_by_app.order = None
    transaction_item_created_by_app.save(update_fields=["order"])

    event = transaction_item_created_by_app.events.filter(
        type=TransactionEventType.CHARGE_SUCCESS
    ).get()

    variables = {"id": to_global_id_or_none(transaction_item_created_by_app)}

    # when
    response = app_api_client.post_graphql(
        TRANSACTION_QUERY, variables, permissions=[permission_manage_payments]
    )

    # then
    content = get_graphql_content(response)
    _assert_transaction_fields_created_by(
        content,
        transaction_item_created_by_app,
        event,
        app,
    )


def test_transaction_created_by_app_query_by_staff(
    staff_api_client, transaction_item_created_by_app, permission_manage_payments, app
):
    # given
    event = transaction_item_created_by_app.events.filter(
        type=TransactionEventType.CHARGE_SUCCESS
    ).get()

    variables = {"id": to_global_id_or_none(transaction_item_created_by_app)}

    # when
    response = staff_api_client.post_graphql(
        TRANSACTION_QUERY, variables, permissions=[permission_manage_payments]
    )

    # then
    content = get_graphql_content(response)
    _assert_transaction_fields_created_by(
        content,
        transaction_item_created_by_app,
        event,
        app,
    )


def test_transaction_create_by_app_query_no_permission(
    app_api_client, transaction_item_created_by_app
):
    # given
    variables = {"id": to_global_id_or_none(transaction_item_created_by_app)}

    # when
    response = app_api_client.post_graphql(TRANSACTION_QUERY, variables)

    # then
    assert_no_permission(response)


def test_transaction_created_by_user_query_by_app(
    app_api_client,
    transaction_item_created_by_user,
    permission_manage_payments,
    permission_manage_staff,
):
    # given
    event = transaction_item_created_by_user.events.filter(
        type=TransactionEventType.CHARGE_SUCCESS
    ).get()

    variables = {"id": to_global_id_or_none(transaction_item_created_by_user)}

    # when
    response = app_api_client.post_graphql(
        TRANSACTION_QUERY,
        variables,
        permissions=[permission_manage_payments, permission_manage_staff],
    )

    # then
    content = get_graphql_content(response)
    _assert_transaction_fields_created_by(
        content,
        transaction_item_created_by_user,
        event,
        transaction_item_created_by_user.user,
    )


def test_transaction_creted_by_user_query_no_order(
    app_api_client,
    transaction_item_created_by_user,
    permission_manage_payments,
    permission_manage_staff,
):
    # given
    transaction_item_created_by_user.order = None
    transaction_item_created_by_user.save(update_fields=["order"])

    event = transaction_item_created_by_user.events.filter(
        type=TransactionEventType.CHARGE_SUCCESS
    ).get()

    variables = {"id": to_global_id_or_none(transaction_item_created_by_user)}

    # when
    response = app_api_client.post_graphql(
        TRANSACTION_QUERY,
        variables,
        permissions=[permission_manage_payments, permission_manage_staff],
    )

    # then
    content = get_graphql_content(response)
    _assert_transaction_fields_created_by(
        content,
        transaction_item_created_by_user,
        event,
        transaction_item_created_by_user.user,
    )


def test_transaction_created_by_user_query_by_staff(
    staff_api_client,
    transaction_item_created_by_user,
    permission_manage_payments,
    permission_manage_staff,
):
    # given
    event = transaction_item_created_by_user.events.filter(
        type=TransactionEventType.CHARGE_SUCCESS
    ).get()

    variables = {"id": to_global_id_or_none(transaction_item_created_by_user)}

    # when
    response = staff_api_client.post_graphql(
        TRANSACTION_QUERY,
        variables,
        permissions=[permission_manage_payments, permission_manage_staff],
    )

    # then
    content = get_graphql_content(response)
    _assert_transaction_fields_created_by(
        content,
        transaction_item_created_by_user,
        event,
        transaction_item_created_by_user.user,
    )


def test_transaction_create_by_user_query_no_permission(
    app_api_client, transaction_item_created_by_user
):
    # given
    variables = {"id": to_global_id_or_none(transaction_item_created_by_user)}

    # when
    response = app_api_client.post_graphql(TRANSACTION_QUERY, variables)

    # then
    assert_no_permission(response)


@pytest.mark.parametrize(
    "db_field, api_field",
    [
        ("authorize_pending_value", "authorizePendingAmount"),
        ("charge_pending_value", "chargePendingAmount"),
        ("refund_pending_value", "refundPendingAmount"),
        ("cancel_pending_value", "cancelPendingAmount"),
    ],
)
def test_transaction_with_pending_amount(
    db_field,
    api_field,
    staff_api_client,
    transaction_item_created_by_user,
    permission_manage_payments,
    permission_manage_staff,
):
    # given
    expected_value = Decimal("10.00")

    setattr(transaction_item_created_by_user, db_field, expected_value)
    transaction_item_created_by_user.save(update_fields=[db_field])

    variables = {"id": to_global_id_or_none(transaction_item_created_by_user)}

    # when
    response = staff_api_client.post_graphql(
        TRANSACTION_QUERY,
        variables,
        permissions=[permission_manage_payments, permission_manage_staff],
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["transaction"]
    pending_money = data[api_field]
    assert pending_money["amount"] == expected_value


def test_transaction_event_by_user(
    transaction_item_created_by_user,
    permission_manage_payments,
    permission_manage_staff,
    staff_api_client,
):
    # given
    psp_reference = "psp-ref-123"
    event = TransactionEvent.objects.create(
        transaction=transaction_item_created_by_user,
        psp_reference=psp_reference,
        message="Sucesfull charge",
        currency="USD",
        type=TransactionEventType.CHARGE_SUCCESS,
        amount_value=Decimal("10.00"),
        external_url=f"http://`{TEST_SERVER_DOMAIN}/test",
        user=staff_api_client.user,
    )

    variables = {"id": to_global_id_or_none(transaction_item_created_by_user)}

    # when
    response = staff_api_client.post_graphql(
        TRANSACTION_QUERY,
        variables,
        permissions=[permission_manage_payments, permission_manage_staff],
    )

    # then
    content = get_graphql_content(response)
    events = content["data"]["transaction"]["events"]
    assert len(events) == 2
    event_data = [event for event in events if event["pspReference"] == psp_reference][
        0
    ]
    assert event_data["id"] == to_global_id_or_none(event)
    assert event_data["createdAt"] == event.created_at.isoformat()
    assert event_data["status"] == event.status.upper()
    assert event_data["pspReference"] == event.psp_reference
    assert event_data["name"] == event.message
    assert event_data["message"] == event.message
    assert event_data["externalUrl"] == event.external_url
    assert event_data["amount"]["amount"] == event.amount_value
    assert event_data["amount"]["currency"] == event.currency
    assert event_data["type"] == event.type.upper()
    assert event_data["createdBy"]["id"] == to_global_id_or_none(staff_api_client.user)


def test_transaction_event_by_app(
    transaction_item_created_by_app,
    permission_manage_payments,
    permission_manage_staff,
    app_api_client,
):
    # given
    psp_reference = "psp-ref-123"
    event = TransactionEvent.objects.create(
        transaction=transaction_item_created_by_app,
        status=TransactionEventStatus.SUCCESS,
        psp_reference=psp_reference,
        message="Sucesfull charge",
        currency="USD",
        type=TransactionEventType.CHARGE_SUCCESS,
        amount_value=Decimal("10.00"),
        external_url=f"http://`{TEST_SERVER_DOMAIN}/test",
        app_identifier=app_api_client.app.identifier,
        app=app_api_client.app,
    )

    variables = {"id": to_global_id_or_none(transaction_item_created_by_app)}

    # when
    response = app_api_client.post_graphql(
        TRANSACTION_QUERY,
        variables,
        permissions=[permission_manage_payments, permission_manage_staff],
    )

    # then
    content = get_graphql_content(response)
    events = content["data"]["transaction"]["events"]
    assert len(events) == 2
    event_data = [event for event in events if event["pspReference"] == psp_reference][
        0
    ]
    assert event_data["id"] == to_global_id_or_none(event)
    assert event_data["createdAt"] == event.created_at.isoformat()
    assert event_data["status"] == event.status.upper()
    assert event_data["pspReference"] == event.psp_reference
    assert event_data["name"] == event.message
    assert event_data["message"] == event.message
    assert event_data["externalUrl"] == event.external_url
    assert event_data["amount"]["amount"] == event.amount_value
    assert event_data["amount"]["currency"] == event.currency
    assert event_data["type"] == event.type.upper()
    assert event_data["createdBy"]["id"] == to_global_id_or_none(app_api_client.app)


def test_transaction_event_by_reinstalled_app(
    transaction_item_created_by_app,
    permission_manage_payments,
    permission_manage_staff,
    app_api_client,
):
    # given
    psp_reference = "psp-ref-123"
    event = TransactionEvent.objects.create(
        transaction=transaction_item_created_by_app,
        status=TransactionEventStatus.SUCCESS,
        psp_reference=psp_reference,
        message="Sucesfull charge",
        currency="USD",
        type=TransactionEventType.CHARGE_SUCCESS,
        amount_value=Decimal("10.00"),
        external_url=f"http://`{TEST_SERVER_DOMAIN}/test",
        app_identifier=app_api_client.app.identifier,
        app=None,
    )

    variables = {"id": to_global_id_or_none(transaction_item_created_by_app)}

    # when
    response = app_api_client.post_graphql(
        TRANSACTION_QUERY,
        variables,
        permissions=[permission_manage_payments, permission_manage_staff],
    )

    # then
    content = get_graphql_content(response)
    events = content["data"]["transaction"]["events"]
    assert len(events) == 2
    event_data = [event for event in events if event["pspReference"] == psp_reference][
        0
    ]
    assert event_data["id"] == to_global_id_or_none(event)
    assert event_data["createdAt"] == event.created_at.isoformat()
    assert event_data["status"] == event.status.upper()
    assert event_data["pspReference"] == event.psp_reference
    assert event_data["name"] == event.message
    assert event_data["message"] == event.message
    assert event_data["externalUrl"] == event.external_url
    assert event_data["amount"]["amount"] == event.amount_value
    assert event_data["amount"]["currency"] == event.currency
    assert event_data["type"] == event.type.upper()
    assert event_data["createdBy"]["id"] == to_global_id_or_none(app_api_client.app)
