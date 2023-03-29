import json
from decimal import Decimal

import graphene

from .....channel import TransactionFlowStrategy
from .....payment.interface import (
    PaymentGatewayData,
    TransactionProcessActionData,
    TransactionSessionData,
)
from .....webhook.event_types import WebhookEventSyncType
from .....webhook.models import Webhook
from ...tasks import create_deliveries_for_subscriptions

TRANSACTION_PROCESS_SESSION = """
subscription {
  event{
    ...on TransactionProcessSession{
      merchantReference
      action{
        amount
        currency
        actionType
      }
      data
      sourceObject{
        __typename
        ... on Checkout{
          id
          totalPrice{
            gross{
              amount
            }
          }
        }
        ... on Order{
          id
        }
      }
    }
  }
}
"""


def test_transaction_process_session_checkout_with_data(
    checkout, webhook_app, permission_manage_payments, transaction_item_generator
):
    # given
    webhook_app.permissions.add(permission_manage_payments)
    webhook = Webhook.objects.create(
        name="Webhook",
        app=webhook_app,
        subscription_query=TRANSACTION_PROCESS_SESSION,
    )
    event_type = WebhookEventSyncType.TRANSACTION_PROCESS_SESSION
    webhook.events.create(event_type=event_type)
    payload_data = {"some": "json data"}
    amount = Decimal("10")
    transaction = transaction_item_generator(
        checkout_id=checkout.pk,
        app=webhook_app,
        psp_reference=None,
        name=None,
        message=None,
    )
    action_type = TransactionFlowStrategy.CHARGE

    subscribable_object = TransactionSessionData(
        transaction=transaction,
        source_object=checkout,
        action=TransactionProcessActionData(
            amount=amount,
            currency=transaction.currency,
            action_type=action_type,
        ),
        payment_gateway=PaymentGatewayData(
            app_identifier=webhook_app.identifier, data=payload_data, error=None
        ),
    )

    # when
    delivery = create_deliveries_for_subscriptions(
        event_type, subscribable_object, [webhook]
    )[0]

    # then

    checkout_id = graphene.Node.to_global_id("Checkout", checkout.pk)
    assert delivery.payload
    assert delivery.payload.payload
    assert json.loads(delivery.payload.payload) == {
        "merchantReference": graphene.Node.to_global_id(
            "TransactionItem", transaction.token
        ),
        "action": {
            "amount": amount,
            "currency": "USD",
            "actionType": action_type.upper(),
        },
        "data": payload_data,
        "sourceObject": {
            "__typename": "Checkout",
            "id": checkout_id,
            "totalPrice": {"gross": {"amount": 0.0}},
        },
    }


def test_transaction_process_session_checkout_without_data(
    checkout, webhook_app, permission_manage_payments, transaction_item_generator
):
    # given
    webhook_app.permissions.add(permission_manage_payments)
    webhook = Webhook.objects.create(
        name="Webhook",
        app=webhook_app,
        subscription_query=TRANSACTION_PROCESS_SESSION,
    )
    event_type = WebhookEventSyncType.TRANSACTION_PROCESS_SESSION
    webhook.events.create(event_type=event_type)
    payload_data = None
    amount = Decimal("10")

    transaction = transaction_item_generator(
        checkout_id=checkout.pk,
        app=webhook_app,
        psp_reference=None,
        name=None,
        message=None,
    )
    action_type = TransactionFlowStrategy.CHARGE

    subscribable_object = TransactionSessionData(
        transaction=transaction,
        source_object=checkout,
        action=TransactionProcessActionData(
            amount=amount,
            currency=transaction.currency,
            action_type=action_type,
        ),
        payment_gateway=PaymentGatewayData(
            app_identifier=webhook_app.identifier, data=payload_data, error=None
        ),
    )

    # when
    delivery = create_deliveries_for_subscriptions(
        event_type, subscribable_object, [webhook]
    )[0]

    # then
    checkout_id = graphene.Node.to_global_id("Checkout", checkout.pk)
    assert delivery.payload
    assert delivery.payload.payload
    assert json.loads(delivery.payload.payload) == {
        "merchantReference": graphene.Node.to_global_id(
            "TransactionItem", transaction.token
        ),
        "action": {
            "amount": amount,
            "currency": "USD",
            "actionType": action_type.upper(),
        },
        "data": payload_data,
        "sourceObject": {
            "__typename": "Checkout",
            "id": checkout_id,
            "totalPrice": {"gross": {"amount": 0.0}},
        },
    }


def test_transaction_process_session_order_with_data(
    order, webhook_app, permission_manage_payments, transaction_item_generator
):
    # given
    webhook_app.permissions.add(permission_manage_payments)
    webhook = Webhook.objects.create(
        name="Webhook",
        app=webhook_app,
        subscription_query=TRANSACTION_PROCESS_SESSION,
    )
    event_type = WebhookEventSyncType.TRANSACTION_PROCESS_SESSION
    webhook.events.create(event_type=event_type)
    payload_data = {"some": "json data"}
    amount = Decimal("10")

    transaction = transaction_item_generator(
        order_id=order.pk,
        app=webhook_app,
        psp_reference=None,
        name=None,
        message=None,
    )
    action_type = TransactionFlowStrategy.CHARGE

    subscribable_object = TransactionSessionData(
        transaction=transaction,
        source_object=order,
        action=TransactionProcessActionData(
            amount=amount,
            currency=transaction.currency,
            action_type=action_type,
        ),
        payment_gateway=PaymentGatewayData(
            app_identifier=webhook_app.identifier, data=payload_data, error=None
        ),
    )

    # when
    delivery = create_deliveries_for_subscriptions(
        event_type, subscribable_object, [webhook]
    )[0]

    # then

    order_id = graphene.Node.to_global_id("Order", order.pk)
    assert delivery.payload
    assert delivery.payload.payload
    assert json.loads(delivery.payload.payload) == {
        "merchantReference": graphene.Node.to_global_id(
            "TransactionItem", transaction.token
        ),
        "action": {
            "amount": amount,
            "currency": "USD",
            "actionType": action_type.upper(),
        },
        "data": payload_data,
        "sourceObject": {
            "__typename": "Order",
            "id": order_id,
        },
    }


def test_transaction_process_session_order_without_data(
    order, webhook_app, permission_manage_payments, transaction_item_generator
):
    # given
    webhook_app.permissions.add(permission_manage_payments)
    webhook = Webhook.objects.create(
        name="Webhook",
        app=webhook_app,
        subscription_query=TRANSACTION_PROCESS_SESSION,
    )
    event_type = WebhookEventSyncType.TRANSACTION_PROCESS_SESSION
    webhook.events.create(event_type=event_type)
    payload_data = None
    amount = Decimal("10")

    transaction = transaction_item_generator(
        order_id=order.pk,
        app=webhook_app,
        psp_reference=None,
        name=None,
        message=None,
    )
    action_type = TransactionFlowStrategy.CHARGE

    subscribable_object = TransactionSessionData(
        transaction=transaction,
        source_object=order,
        action=TransactionProcessActionData(
            amount=amount,
            currency=transaction.currency,
            action_type=action_type,
        ),
        payment_gateway=PaymentGatewayData(
            app_identifier=webhook_app.identifier, data=payload_data, error=None
        ),
    )

    # when
    delivery = create_deliveries_for_subscriptions(
        event_type, subscribable_object, [webhook]
    )[0]

    # then
    order_id = graphene.Node.to_global_id("Order", order.pk)
    assert delivery.payload
    assert delivery.payload.payload
    assert json.loads(delivery.payload.payload) == {
        "merchantReference": graphene.Node.to_global_id(
            "TransactionItem", transaction.token
        ),
        "action": {
            "amount": amount,
            "currency": "USD",
            "actionType": action_type.upper(),
        },
        "data": payload_data,
        "sourceObject": {
            "__typename": "Order",
            "id": order_id,
        },
    }
