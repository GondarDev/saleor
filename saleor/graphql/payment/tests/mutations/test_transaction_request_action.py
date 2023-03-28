from decimal import Decimal

import graphene
import pytest
from mock import patch

from .....app.models import App
from .....order import OrderEvents
from .....payment import TransactionAction, TransactionEventType
from .....payment.interface import TransactionActionData
from .....payment.models import TransactionEvent, TransactionItem
from .....webhook.event_types import WebhookEventSyncType
from ....core.enums import TransactionRequestActionErrorCode
from ....tests.utils import assert_no_permission, get_graphql_content
from ...enums import TransactionActionEnum

MUTATION_TRANSACTION_REQUEST_ACTION = """
mutation TransactionRequestAction(
    $id: ID!,
    $action_type: TransactionActionEnum!,
    $amount: PositiveDecimal
    ){
    transactionRequestAction(
            id: $id,
            actionType: $action_type,
            amount: $amount
        ){
        transaction{
                id
                actions
                reference
                pspReference
                type
                status
                modifiedAt
                createdAt
                authorizedAmount{
                    amount
                    currency
                }
                voidedAmount{
                    currency
                    amount
                }
                chargedAmount{
                    currency
                    amount
                }
                refundedAmount{
                    currency
                    amount
                }
        }
        errors{
            field
            message
            code
        }
    }
}
"""


@pytest.mark.parametrize(
    "charge_amount, expected_called_charge_amount",
    [
        (Decimal("8.00"), Decimal("8.00")),
        (None, Decimal("10.00")),
        (Decimal("100"), Decimal("10.00")),
    ],
)
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_action_request")
def test_transaction_request_charge_action_for_order(
    mocked_payment_action_request,
    mocked_is_active,
    charge_amount,
    expected_called_charge_amount,
    order_with_lines,
    app_api_client,
    permission_manage_payments,
):
    # given
    mocked_is_active.side_effect = [True, False]

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        order_id=order_with_lines.pk,
        authorized_value=Decimal("10"),
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.CHARGE.name,
        "amount": charge_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.CHARGE_REQUEST
    ).first()

    assert mocked_is_active.called
    assert request_event
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.CHARGE,
            action_value=expected_called_charge_amount,
            event=request_event,
            transaction_app_owner=None,
        ),
        channel_slug=order_with_lines.channel.slug,
    )

    event = order_with_lines.events.first()
    assert event.type == OrderEvents.TRANSACTION_CHARGE_REQUESTED
    assert Decimal(event.parameters["amount"]) == expected_called_charge_amount
    assert event.parameters["reference"] == transaction.psp_reference

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.CHARGE_REQUEST,
        amount_value=expected_called_charge_amount,
    )


@pytest.mark.parametrize(
    "refund_amount, expected_called_refund_amount",
    [
        (Decimal("8.00"), Decimal("8.00")),
        (None, Decimal("10.00")),
        (Decimal("100"), Decimal("10.00")),
    ],
)
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_action_request")
def test_transaction_request_refund_action_for_order(
    mocked_payment_action_request,
    mocked_is_active,
    refund_amount,
    expected_called_refund_amount,
    order_with_lines,
    app_api_client,
    permission_manage_payments,
):
    # given
    mocked_is_active.side_effect = [True, False]

    transaction = TransactionItem.objects.create(
        status="Captured",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["refund"],
        currency="USD",
        order_id=order_with_lines.pk,
        charged_value=Decimal("10"),
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.REFUND.name,
        "amount": refund_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.REFUND_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.REFUND,
            action_value=expected_called_refund_amount,
            event=request_event,
            transaction_app_owner=None,
        ),
        channel_slug=order_with_lines.channel.slug,
    )

    event = order_with_lines.events.first()
    assert event.type == OrderEvents.TRANSACTION_REFUND_REQUESTED
    assert Decimal(event.parameters["amount"]) == expected_called_refund_amount
    assert event.parameters["reference"] == transaction.psp_reference

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.REFUND_REQUEST,
        amount_value=expected_called_refund_amount,
    )


@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_action_request")
def test_transaction_request_void_action_for_order(
    mocked_payment_action_request,
    mocked_is_active,
    order_with_lines,
    app_api_client,
    permission_manage_payments,
):
    # given
    mocked_is_active.side_effect = [True, False]

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        order_id=order_with_lines.pk,
        authorized_value=Decimal("10"),
    )
    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.VOID.name,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.CANCEL_REQUEST,
    ).first()
    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.VOID,
            action_value=None,
            event=request_event,
            transaction_app_owner=None,
        ),
        channel_slug=order_with_lines.channel.slug,
    )

    event = order_with_lines.events.first()
    assert event.type == OrderEvents.TRANSACTION_CANCEL_REQUESTED
    assert event.parameters["reference"] == transaction.psp_reference

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.CANCEL_REQUEST,
        amount_value=0,
    )


@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_action_request")
def test_transaction_request_void_action_for_checkout(
    mocked_payment_action_request,
    mocked_is_active,
    checkout,
    app_api_client,
    permission_manage_payments,
):
    # given
    mocked_is_active.side_effect = [True, False]

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        checkout_id=checkout.pk,
        authorized_value=Decimal("10"),
    )
    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.VOID.name,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.CANCEL_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.VOID,
            action_value=None,
            event=request_event,
            transaction_app_owner=None,
        ),
        channel_slug=checkout.channel.slug,
    )

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.CANCEL_REQUEST,
        amount_value=0,
    )


@pytest.mark.parametrize(
    "charge_amount, expected_called_charge_amount",
    [
        (Decimal("8.00"), Decimal("8.00")),
        (None, Decimal("10.00")),
        (Decimal("100"), Decimal("10.00")),
    ],
)
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_action_request")
def test_transaction_request_charge_action_for_checkout(
    mocked_payment_action_request,
    mocked_is_active,
    charge_amount,
    expected_called_charge_amount,
    checkout,
    app_api_client,
    permission_manage_payments,
):
    # given
    mocked_is_active.side_effect = [True, False]

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        checkout_id=checkout.pk,
        authorized_value=Decimal("10"),
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.CHARGE.name,
        "amount": charge_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.CHARGE_REQUEST
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.CHARGE,
            action_value=expected_called_charge_amount,
            event=request_event,
            transaction_app_owner=None,
        ),
        channel_slug=checkout.channel.slug,
    )

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.CHARGE_REQUEST,
        amount_value=expected_called_charge_amount,
    )


@pytest.mark.parametrize(
    "refund_amount, expected_called_refund_amount",
    [
        (Decimal("8.00"), Decimal("8.00")),
        (None, Decimal("10.00")),
        (Decimal("100"), Decimal("10.00")),
    ],
)
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_action_request")
def test_transaction_request_refund_action_for_checkout(
    mocked_payment_action_request,
    mocked_is_active,
    refund_amount,
    expected_called_refund_amount,
    checkout,
    app_api_client,
    permission_manage_payments,
):
    # given
    mocked_is_active.side_effect = [True, False]

    transaction = TransactionItem.objects.create(
        status="Captured",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["refund"],
        currency="USD",
        checkout_id=checkout.pk,
        charged_value=Decimal("10"),
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.REFUND.name,
        "amount": refund_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.REFUND_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.REFUND,
            action_value=expected_called_refund_amount,
            event=request_event,
            transaction_app_owner=None,
        ),
        channel_slug=checkout.channel.slug,
    )

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.REFUND_REQUEST,
        amount_value=expected_called_refund_amount,
    )


@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_action_request")
def test_transaction_action_request_uses_handle_payment_permission(
    mocked_payment_action_request,
    mocked_is_active,
    checkout,
    app_api_client,
    permission_manage_payments,
):
    # given
    mocked_is_active.side_effect = [True, False]

    transaction = TransactionItem.objects.create(
        status="Captured",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["refund"],
        currency="USD",
        checkout_id=checkout.pk,
        charged_value=Decimal("10"),
    )
    refund_amount = Decimal("1")
    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.REFUND.name,
        "amount": refund_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.REFUND_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.REFUND,
            action_value=refund_amount,
            event=request_event,
            transaction_app_owner=None,
        ),
        channel_slug=checkout.channel.slug,
    )


def test_transaction_request_action_missing_permission(
    app_api_client, order_with_lines
):
    # given

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        order_id=order_with_lines.pk,
        authorized_value=Decimal("10"),
    )
    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.VOID.name,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION, variables, permissions=[]
    )

    # then
    assert_no_permission(response)


@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
def test_transaction_request_action_missing_event(
    mocked_is_active, staff_api_client, permission_manage_payments, order
):
    # given
    authorization_value = Decimal("10")
    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        order_id=order.pk,
        authorized_value=authorization_value,
    )
    mocked_is_active.side_effect = [False, False]

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.VOID.name,
    }

    # when
    response = staff_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[
            permission_manage_payments,
        ],
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["transactionRequestAction"]
    assert len(data["errors"]) == 1
    assert data["errors"][0]["message"] == (
        "No app or plugin is configured to handle payment action requests."
    )
    code_enum = TransactionRequestActionErrorCode
    assert data["errors"][0]["code"] == (
        code_enum.MISSING_TRANSACTION_ACTION_REQUEST_WEBHOOK.name
    )

    assert mocked_is_active.called


@pytest.fixture
def transaction_request_webhook(permission_manage_payments):
    app = App.objects.create(
        name="Sample app objects",
        is_active=True,
        identifier="saleor.app.payment",
    )
    app.permissions.set([permission_manage_payments])
    webhook = app.webhooks.create(
        name="Request", is_active=True, target_url="http://localhost:8000/endpoint/"
    )

    return webhook


@pytest.mark.parametrize(
    "charge_amount, expected_called_charge_amount",
    [
        (Decimal("8.00"), Decimal("8.00")),
        (None, Decimal("10.00")),
        (Decimal("100"), Decimal("10.00")),
    ],
)
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_charge_requested")
def test_transaction_request_charge_for_order(
    mocked_payment_action_request,
    mocked_is_active,
    charge_amount,
    expected_called_charge_amount,
    order_with_lines,
    app_api_client,
    permission_manage_payments,
    transaction_request_webhook,
    app,
):
    # given
    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_CHARGE_REQUESTED
    )
    mocked_is_active.return_value = False

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        order_id=order_with_lines.pk,
        authorized_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=transaction_request_webhook.app,
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.CHARGE.name,
        "amount": charge_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.CHARGE_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.CHARGE,
            action_value=expected_called_charge_amount,
            event=request_event,
            transaction_app_owner=transaction_request_webhook.app,
        ),
        order_with_lines.channel.slug,
    )

    event = order_with_lines.events.first()
    assert event.type == OrderEvents.TRANSACTION_CHARGE_REQUESTED
    assert Decimal(event.parameters["amount"]) == expected_called_charge_amount
    assert event.parameters["reference"] == transaction.psp_reference

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.CHARGE_REQUEST,
        amount_value=expected_called_charge_amount,
    )


@pytest.mark.parametrize(
    "refund_amount, expected_called_refund_amount",
    [
        (Decimal("8.00"), Decimal("8.00")),
        (None, Decimal("10.00")),
        (Decimal("100"), Decimal("10.00")),
    ],
)
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_refund_requested")
def test_transaction_request_refund_for_order(
    mocked_payment_action_request,
    mocked_is_active,
    refund_amount,
    expected_called_refund_amount,
    order_with_lines,
    app_api_client,
    permission_manage_payments,
    transaction_request_webhook,
):
    # given
    mocked_is_active.return_value = False

    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_REFUND_REQUESTED
    )

    transaction = TransactionItem.objects.create(
        status="Captured",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["refund"],
        currency="USD",
        order_id=order_with_lines.pk,
        charged_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=transaction_request_webhook.app,
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.REFUND.name,
        "amount": refund_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)
    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.REFUND_REQUEST,
    ).first()
    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.REFUND,
            action_value=expected_called_refund_amount,
            event=request_event,
            transaction_app_owner=transaction_request_webhook.app,
        ),
        order_with_lines.channel.slug,
    )

    event = order_with_lines.events.first()
    assert event.type == OrderEvents.TRANSACTION_REFUND_REQUESTED
    assert Decimal(event.parameters["amount"]) == expected_called_refund_amount
    assert event.parameters["reference"] == transaction.psp_reference

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.REFUND_REQUEST,
        amount_value=expected_called_refund_amount,
    )


@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_cancelation_requested")
def test_transaction_request_cancelation_for_order(
    mocked_payment_action_request,
    mocked_is_active,
    order_with_lines,
    app_api_client,
    permission_manage_payments,
    transaction_request_webhook,
):
    # given
    mocked_is_active.return_value = False

    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_CANCELATION_REQUESTED
    )

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        order_id=order_with_lines.pk,
        authorized_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=transaction_request_webhook.app,
    )
    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.VOID.name,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.CANCEL_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.CANCEL,
            action_value=None,
            event=request_event,
            transaction_app_owner=transaction_request_webhook.app,
        ),
        order_with_lines.channel.slug,
    )

    event = order_with_lines.events.first()
    assert event.type == OrderEvents.TRANSACTION_CANCEL_REQUESTED
    assert event.parameters["reference"] == transaction.psp_reference

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.CANCEL_REQUEST,
        amount_value=0,
    )


@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_cancelation_requested")
def test_transaction_request_cancelation_for_checkout(
    mocked_payment_action_request,
    mocked_is_active,
    checkout,
    app_api_client,
    permission_manage_payments,
    transaction_request_webhook,
):
    # given
    mocked_is_active.return_value = False

    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_CANCELATION_REQUESTED
    )

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        checkout_id=checkout.pk,
        authorized_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=transaction_request_webhook.app,
    )
    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.VOID.name,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.CANCEL_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.CANCEL,
            action_value=None,
            event=request_event,
            transaction_app_owner=transaction_request_webhook.app,
        ),
        checkout.channel.slug,
    )

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.CANCEL_REQUEST,
        amount_value=0,
    )


@pytest.mark.parametrize(
    "charge_amount, expected_called_charge_amount",
    [
        (Decimal("8.00"), Decimal("8.00")),
        (None, Decimal("10.00")),
        (Decimal("100"), Decimal("10.00")),
    ],
)
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_charge_requested")
def test_transaction_request_charge_for_checkout(
    mocked_payment_action_request,
    mocked_is_active,
    charge_amount,
    expected_called_charge_amount,
    checkout,
    app_api_client,
    permission_manage_payments,
    transaction_request_webhook,
):
    # given
    mocked_is_active.side_effect = [True, False]

    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_CHARGE_REQUESTED
    )

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        checkout_id=checkout.pk,
        authorized_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=transaction_request_webhook.app,
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.CHARGE.name,
        "amount": charge_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)
    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.CHARGE_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.CHARGE,
            action_value=expected_called_charge_amount,
            event=request_event,
            transaction_app_owner=transaction_request_webhook.app,
        ),
        checkout.channel.slug,
    )

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.CHARGE_REQUEST,
        amount_value=expected_called_charge_amount,
    )


@pytest.mark.parametrize(
    "refund_amount, expected_called_refund_amount",
    [
        (Decimal("8.00"), Decimal("8.00")),
        (None, Decimal("10.00")),
        (Decimal("100"), Decimal("10.00")),
    ],
)
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_refund_requested")
def test_transaction_request_refund_for_checkout(
    mocked_payment_action_request,
    mocked_is_active,
    refund_amount,
    expected_called_refund_amount,
    checkout,
    app_api_client,
    permission_manage_payments,
    transaction_request_webhook,
):
    # given
    mocked_is_active.return_value = False

    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_REFUND_REQUESTED
    )

    transaction = TransactionItem.objects.create(
        status="Captured",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["refund"],
        currency="USD",
        checkout_id=checkout.pk,
        charged_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=transaction_request_webhook.app,
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.REFUND.name,
        "amount": refund_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)
    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.REFUND_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.REFUND,
            action_value=expected_called_refund_amount,
            event=request_event,
            transaction_app_owner=transaction_request_webhook.app,
        ),
        checkout.channel.slug,
    )

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.REFUND_REQUEST,
        amount_value=expected_called_refund_amount,
    )


@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_refund_requested")
def test_transaction_request_refund_when_app_reinstalled(
    mocked_payment_action_request,
    mocked_is_active,
    checkout,
    app_api_client,
    permission_manage_payments,
    transaction_request_webhook,
):
    # given
    refund_amount = Decimal("8.00")
    expected_called_refund_amount = Decimal("8.00")
    mocked_is_active.return_value = False

    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_REFUND_REQUESTED
    )

    transaction = TransactionItem.objects.create(
        status="Captured",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["refund"],
        currency="USD",
        checkout_id=checkout.pk,
        charged_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=None,
    )

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.REFUND.name,
        "amount": refund_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)
    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.REFUND_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.REFUND,
            action_value=expected_called_refund_amount,
            event=request_event,
            transaction_app_owner=transaction_request_webhook.app,
        ),
        checkout.channel.slug,
    )

    assert TransactionEvent.objects.get(
        transaction=transaction,
        type=TransactionEventType.REFUND_REQUEST,
        amount_value=expected_called_refund_amount,
    )


@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
@patch("saleor.plugins.manager.PluginsManager.transaction_refund_requested")
def test_transaction_request_uses_handle_payment_permission(
    mocked_payment_action_request,
    mocked_is_active,
    checkout,
    app_api_client,
    permission_manage_payments,
    transaction_request_webhook,
):
    # given
    mocked_is_active.return_value = False

    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_REFUND_REQUESTED
    )

    transaction = TransactionItem.objects.create(
        status="Captured",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["refund"],
        currency="USD",
        checkout_id=checkout.pk,
        charged_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=transaction_request_webhook.app,
    )
    refund_amount = Decimal("1")
    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.REFUND.name,
        "amount": refund_amount,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[permission_manage_payments],
    )

    # then
    get_graphql_content(response)

    request_event = TransactionEvent.objects.filter(
        type=TransactionEventType.REFUND_REQUEST,
    ).first()

    assert request_event
    assert mocked_is_active.called
    mocked_payment_action_request.assert_called_once_with(
        TransactionActionData(
            transaction=transaction,
            action_type=TransactionAction.REFUND,
            action_value=refund_amount,
            event=request_event,
            transaction_app_owner=transaction_request_webhook.app,
        ),
        checkout.channel.slug,
    )


def test_transaction_request_missing_permission(
    app_api_client, order_with_lines, transaction_request_webhook
):
    # given

    transaction_request_webhook.events.create(
        event_type=WebhookEventSyncType.TRANSACTION_CANCELATION_REQUESTED
    )

    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        order_id=order_with_lines.pk,
        authorized_value=Decimal("10"),
        app_identifier=transaction_request_webhook.app.identifier,
        app=transaction_request_webhook.app,
    )
    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.VOID.name,
    }

    # when
    response = app_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION, variables, permissions=[]
    )

    # then
    assert_no_permission(response)


@patch("saleor.payment.gateway.get_webhooks_for_event")
@patch("saleor.plugins.manager.PluginsManager.is_event_active_for_any_plugin")
def test_transaction_request_missing_event(
    mocked_is_active,
    mocked_get_webhooks,
    staff_api_client,
    permission_manage_payments,
    order,
    app,
):
    # given
    authorization_value = Decimal("10")
    transaction = TransactionItem.objects.create(
        status="Authorized",
        name="Credit card",
        psp_reference="PSP ref",
        available_actions=["charge", "void"],
        currency="USD",
        order_id=order.pk,
        authorized_value=authorization_value,
        app_identifier=app.identifier,
        app=app,
    )

    mocked_get_webhooks.return_value = []
    mocked_is_active.return_value = False

    variables = {
        "id": graphene.Node.to_global_id("TransactionItem", transaction.pk),
        "action_type": TransactionActionEnum.VOID.name,
    }

    # when
    response = staff_api_client.post_graphql(
        MUTATION_TRANSACTION_REQUEST_ACTION,
        variables,
        permissions=[
            permission_manage_payments,
        ],
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["transactionRequestAction"]
    assert len(data["errors"]) == 1
    assert data["errors"][0]["message"] == (
        "No app or plugin is configured to handle payment action requests."
    )
    code_enum = TransactionRequestActionErrorCode
    assert data["errors"][0]["code"] == (
        code_enum.MISSING_TRANSACTION_ACTION_REQUEST_WEBHOOK.name
    )

    assert mocked_is_active.called
    assert mocked_get_webhooks.called
    mocked_get_webhooks.assert_called_once_with(
        event_type=WebhookEventSyncType.TRANSACTION_CANCELATION_REQUESTED,
        apps_ids=[app.id],
    )
