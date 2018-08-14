import logging

from django.utils.translation import pgettext_lazy

logger = logging.getLogger(__name__)


class AddressType:
    BILLING = 'billing'
    SHIPPING = 'shipping'

    CHOICES = [(
        BILLING,
        pgettext_lazy('Type of address used to fulfill order', 'Billing')), (
            SHIPPING,
            pgettext_lazy('Type of address used to fulfill order',
                          'Shipping'))]


class TransactionType:
    AUTH = 'auth'
    CHARGE = 'charge'
    VOID = 'void'
    REFUND = 'refund'

    CHOICES = [(AUTH, pgettext_lazy('transaction type', 'Authorization')),
               (CHARGE, pgettext_lazy('transaction type', 'Charge')),
               (REFUND, pgettext_lazy('transaction type', 'Refund')),
               (VOID, pgettext_lazy('transaction type', 'Void'))]


class PaymentMethodChargeStatus:
    CHARGED = 'charged'
    NOT_CHARGED = 'not-charged'
    FULLY_REFUNDED = 'fully-refunded'

    CHOICES = [
        (CHARGED, pgettext_lazy('payment method status', 'Charged')),
        (NOT_CHARGED, pgettext_lazy('payment method status', 'Not charged')), (
            FULLY_REFUNDED,
            pgettext_lazy('payment method status', 'Fully refunded'))]
