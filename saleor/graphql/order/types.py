import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from ...order import models
from ..core.types import CountableDjangoObjectType


class Order(CountableDjangoObjectType):
    is_paid = graphene.Boolean(
        description='Informs if an order is fully paid.')
    order_id = graphene.Int(
        description='User-friendly ID of an order.')
    payment_status = graphene.String(description='Internal payment status.')
    payment_status_display = graphene.String(
        description='User-friendly payment status.')
    status_display = graphene.String(
        description='User-friendly order status.')

    class Meta:
        description = 'Represents an order in the shop.'
        interfaces = [relay.Node]
        model = models.Order
        exclude_fields = [
            'shipping_price_gross', 'shipping_price_net', 'total_gross',
            'total_net']

    def resolve_is_paid(self, info):
        return self.is_fully_paid()

    def resolve_order_id(self, info):
        return self.pk

    def resolve_payment_status(self, info):
        return self.get_last_payment_status()

    def resolve_payment_status_display(self, info):
        return self.get_last_payment_status_display()

    def resolve_status_display(self, info):
        return self.get_status_display()


class OrderHistoryEntry(DjangoObjectType):
    class Meta:
        description = 'History log of the order.'
        model = models.OrderHistoryEntry
        exclude_fields = ['order']


class OrderLine(DjangoObjectType):
    class Meta:
        description = 'Represents order line of particular order.'
        model = models.OrderLine
        exclude_fields = [
            'variant', 'unit_price_gross', 'unit_price_net', 'order']


class OrderNote(DjangoObjectType):
    class Meta:
        description = 'Note from customer or staff user.'
        model = models.OrderNote
        exclude_fields = ['order']


class Fulfillment(DjangoObjectType):
    status_display = graphene.String(
        description='User-friendly fulfillment status.')

    class Meta:
        description = 'Represents order fulfillment.'
        model = models.Fulfillment
        exclude_fields = ['order']

    def resolve_status_display(self, info):
        return self.get_status_display()


class FulfillmentLine(DjangoObjectType):
    class Meta:
        description = 'Represents line of the fulfillment.'
        model = models.FulfillmentLine
        exclude_fields = ['fulfillment']
