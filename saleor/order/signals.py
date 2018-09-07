import logging

from ..core import analytics
from .emails import send_payment_confirmation
from . import OrderEvents, EventsEmailType

logger = logging.getLogger(__name__)


def order_status_change(sender, instance, **kwargs):
    """Handle payment status change and set suitable order status."""
    order = instance.order
    if order.is_fully_paid():
        order.history.create(event=OrderEvents.ORDER_FULLY_PAID.value)
        if order.get_user_current_email():
            send_payment_confirmation.delay(order.pk)
            order.history.create(
                event=OrderEvents.EMAIL_SENT.value,
                parameters={
                    'email': order.get_user_current_email(),
                    'email_type': EventsEmailType.PAYMENT})
        try:
            analytics.report_order(order.tracking_client_id, order)
        except Exception:
            # Analytics failing should not abort the checkout flow
            logger.exception('Recording order in analytics failed')
