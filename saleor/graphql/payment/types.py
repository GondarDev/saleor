import graphene
from graphene import relay

from ...payment import models
from ..core.connection import CountableDjangoObjectType
from ..core.types import Money
from .enums import OrderAction, PaymentChargeStatusEnum


class Transaction(CountableDjangoObjectType):
    amount = graphene.Field(Money, description="Total amount of the transaction.")

    class Meta:
        description = "An object representing a single payment."
        interfaces = [relay.Node]
        model = models.Transaction
        filter_fields = ["id"]
        only_fields = [
            "id",
            "created",
            "payment",
            "token",
            "kind",
            "is_success",
            "error",
        ]

    @staticmethod
    def resolve_amount(root: models.Transaction, _info):
        return root.get_amount()


class CreditCard(graphene.ObjectType):
    brand = graphene.String(description="Card brand.", required=True)
    first_digits = graphene.String(
        description="The host name of the domain.", required=True
    )
    last_digits = graphene.String(
        description="Last 4 digits of the card number.", required=True
    )
    exp_month = graphene.Int(
        description=("Two-digit number representing the card’s expiration month."),
        required=True,
    )
    exp_year = graphene.Int(
        description=("Four-digit number representing the card’s expiration year."),
        required=True,
    )


class PaymentSource(graphene.ObjectType):
    class Meta:
        description = (
            "Represents a payment source stored "
            "for user in payment gateway, such as credit card."
        )

    gateway = graphene.String(description="Payment gateway name.", required=True)
    credit_card_info = graphene.Field(
        CreditCard, description="Stored credit card details if available."
    )


class Payment(CountableDjangoObjectType):
    charge_status = PaymentChargeStatusEnum(
        description="Internal payment status.", required=True
    )
    actions = graphene.List(
        OrderAction,
        description=(
            "List of actions that can be performed in the current state of a payment."
        ),
        required=True,
    )
    total = graphene.Field(Money, description="Total amount of the payment.")
    captured_amount = graphene.Field(
        Money, description="Total amount captured for this payment."
    )
    transactions = graphene.List(
        Transaction, description="List of all transactions within this payment."
    )
    available_capture_amount = graphene.Field(
        Money, description="Maximum amount of money that can be captured."
    )
    available_refund_amount = graphene.Field(
        Money, description="Maximum amount of money that can be refunded."
    )

    class Meta:
        description = "Represents a payment of a given type."
        interfaces = [relay.Node]
        model = models.Payment
        filter_fields = ["id"]
        only_fields = [
            "id",
            "gateway",
            "is_active",
            "created",
            "modified",
            "token",
            "checkout",
            "order",
            "customer_ip_address",
        ]

    @staticmethod
    def resolve_actions(root: models.Payment, _info):
        actions = []
        if root.can_capture():
            actions.append(OrderAction.CAPTURE)
        if root.can_refund():
            actions.append(OrderAction.REFUND)
        if root.can_void():
            actions.append(OrderAction.VOID)
        return actions

    @staticmethod
    def resolve_total(root: models.Payment, _info):
        return root.get_total()

    @staticmethod
    def resolve_captured_amount(root: models.Payment, _info):
        return root.get_captured_amount()

    @staticmethod
    def resolve_transactions(root: models.Payment, _info):
        return root.transactions.all()

    @staticmethod
    def resolve_available_refund_amount(root: models.Payment, _info):
        # FIXME TESTME
        if not root.can_refund():
            return None
        return root.get_captured_amount()

    @staticmethod
    def resolve_available_capture_amount(root: models.Payment, _info):
        # FIXME TESTME
        if not root.can_capture():
            return None
        return root.get_charge_amount()
