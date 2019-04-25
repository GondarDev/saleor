from typing import List

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now

from ..lang.order_events import display_order_event
from ..types import OrderEvents
from ...core.utils.json_serializer import CustomJsonEncoder
from ...payment.models import Payment
from ...checkout.models import CheckoutLine
from ...product.models import ProductVariant
from ...order.models import Order, Fulfillment

User = AbstractBaseUser


class OrderEvent(models.Model):
    """Model used to store events that happened during the order lifecycle.

        Args:
            parameters: Values needed to display the event on the storefront
            type: Type of an order
    """
    date = models.DateTimeField(default=now, editable=False)
    type = models.CharField(
        max_length=255,
        choices=((event.name, event.value) for event in OrderEvents))
    order = models.ForeignKey(
        Order, related_name='events', on_delete=models.CASCADE)
    parameters = JSONField(
        blank=True, default=dict, encoder=CustomJsonEncoder)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='+')

    class Meta:
        ordering = ('date', )
        db_table = 'order_orderevent'

    def __repr__(self):
        return 'OrderEvent(type=%r, user=%r)' % (self.type, self.user)

    def get_event_display(self):
        return display_order_event(self)

    @classmethod
    def draft_created_event(cls, *, order: Order, source: User) -> models.Model:
        pass

    @classmethod
    def draft_selected_shipping_method_event(
            cls, order: Order) -> models.Model:
        pass

    @classmethod
    def draft_added_products(
            cls, *,
            order: Order, source: User,
            products: List[ProductVariant]) -> models.Model:
        pass

    @classmethod
    def draft_removed_products(
            cls, *,
            order: Order, source: User,
            products: List[ProductVariant]) -> models.Model:
        pass

    @classmethod
    def placed_event(cls, order: Order) -> models.Model:
        # TODO: check if order is draft or not
        pass

    @classmethod
    def draft_oversold_items_event(
            cls, *,
            order: Order, source: User,
            oversold_items: List[CheckoutLine]) -> models.Model:
        pass

    @classmethod
    def cancelled_event(
            cls, *,
            order: Order, source: User) -> models.Model:
        pass

    @classmethod
    def manually_marked_as_paid_event(
            cls, *,
            order: Order, source: User) -> models.Model:
        pass

    @classmethod
    def fully_paid_event_event(
            cls, *,
            order: Order, source: User) -> models.Model:
        pass

    @classmethod
    def payment_captured_event(
            cls, *,
            order: Order, source: User, payment: Payment) -> models.Model:
        pass

    @classmethod
    def payment_refunded_event(
            cls, *,
            order: Order, source: User, payment: Payment) -> models.Model:
        pass

    @classmethod
    def payment_voided_event(
            cls, *,
            order: Order, source: User, payment: Payment) -> models.Model:
        pass

    @classmethod
    def payment_failed_event(
            cls, *,
            order: Order, source: User) -> models.Model:
        pass

    @classmethod
    def fulfillment_canceled_event(
            cls, *,
            order: Order, source: User,
            fulfillment: Fulfillment) -> models.Model:
        pass

    @classmethod
    def fulfillment_restocked_items_event(
            cls, *,
            order: Order, source: User,
            fulfillment: Fulfillment) -> models.Model:
        pass

    @classmethod
    def fulfillment_fulfilled_items_event(
            cls, *,
            order: Order, source: User,
            fulfillment: Fulfillment) -> models.Model:
        pass

    @classmethod
    def fulfillment_tracking_updated_event(
            cls, *,
            order: Order, source: User,
            fulfillment: Fulfillment) -> models.Model:
        pass

    @classmethod
    def note_added_event(
            cls, *,
            order: Order, source: User,
            fulfillment: Fulfillment) -> models.Model:
        pass
