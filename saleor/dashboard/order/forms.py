from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator
from django.urls import reverse, reverse_lazy
from django.utils.translation import npgettext_lazy, pgettext_lazy
from django_prices.forms import MoneyField
from payments import PaymentError, PaymentStatus

from ...account.i18n import (
    AddressForm as StorefrontAddressForm, PossiblePhoneNumberFormField)
from ...cart.forms import QuantityField
from ...core.exceptions import InsufficientStock
from ...core.utils import ZERO_TAXED_MONEY
from ...discount.utils import decrease_voucher_usage
from ...order import OrderStatus
from ...order.emails import send_note_confirmation, send_order_confirmation
from ...order.models import (
    Fulfillment, FulfillmentLine, Order, OrderLine, OrderNote)
from ...order.utils import (
    add_variant_to_order, cancel_fulfillment, cancel_order,
    change_order_line_quantity, merge_duplicates_into_order_line,
    recalculate_order)
from ...product.models import Product, ProductVariant, Stock
from ...product.utils import allocate_stock, deallocate_stock
from ...shipping.models import ANY_COUNTRY, ShippingMethodCountry
from ..forms import AjaxSelect2ChoiceField
from ..widgets import PhonePrefixWidget
from .utils import fulfill_order_line, update_order_with_user_addresses


class ConfirmDraftOrderForm(forms.ModelForm):
    """Save draft order as a ready to fulfill."""
    notify_customer = forms.BooleanField(
        label=pgettext_lazy(
            'Send email to customer about order created by staff users',
            'Notify customer'),
        required=False, initial=True)

    class Meta:
        model = Order
        fields = []

    def clean(self):
        super().clean()
        errors = []
        if self.instance.get_total_quantity() == 0:
            errors.append(forms.ValidationError(pgettext_lazy(
                'Confirm draft order form error',
                'Could not confirm order without any products')))
        if not self.instance.billing_address:
            errors.append(forms.ValidationError(pgettext_lazy(
                'Confirm draft order form error',
                'Billing address is required to handle payment')))
        if self.instance.is_shipping_required():
            if not self.instance.shipping_address:
                errors.append(forms.ValidationError(pgettext_lazy(
                    'Confirm draft order form error',
                    'Shipping address is required to handle shipping')))
            if not self.instance.shipping_method_name:
                errors.append(forms.ValidationError(pgettext_lazy(
                    'Confirm draft order form error',
                    'Shipping method is required to handle shipping')))
            method = self.instance.shipping_method
            shipping_address = self.instance.shipping_address
            if (
                method and shipping_address and
                method.country_code != ANY_COUNTRY and
                shipping_address.country.code != method.country_code
            ):
                errors.append(forms.ValidationError(pgettext_lazy(
                    'Confirm draft order form error',
                    'Shipping method is not valid for chosen shipping '
                    'address')))
        if errors:
            raise forms.ValidationError(errors)
        return self.cleaned_data

    def save(self, commit=True):
        self.instance.status = OrderStatus.UNFULFILLED
        if self.instance.user:
            self.instance.user_email = self.instance.user.email
        if not self.instance.is_shipping_required():
            if self.instance.shipping_address:
                self.instance.shipping_address.delete()
            self.instance.shipping_method_name = None
            self.instance.shipping_price = ZERO_TAXED_MONEY
        if self.cleaned_data.get('notify_customer'):
            email = self.instance.get_user_current_email()
            if email:
                send_order_confirmation.delay(self.instance.pk)
        return super().save(commit)


class OrderCustomerForm(forms.ModelForm):
    """Set customer details in an order."""

    update_addresses = forms.BooleanField(
        label=pgettext_lazy(
            'Update an order with user default addresses',
            'Update billing and shipping address'),
        initial=True, required=False)

    class Meta:
        model = Order
        fields = ['user', 'user_email']
        labels = {
            'update_addresses': pgettext_lazy(
                'Update an order with user default addresses',
                'Update billing and shipping address'),
            'user': pgettext_lazy('Order customer', 'User'),
            'user_email': pgettext_lazy(
                'Order customer email',
                'Email')}

    def clean(self):
        cleaned_data = super().clean()
        user_email = cleaned_data.get('user_email')
        user = cleaned_data.get('user')
        if user and user_email:
            raise forms.ValidationError(pgettext_lazy(
                'Edit customer details in order form error',
                'An order can be related either with an email or an existing '
                'user account'))
        return self.cleaned_data

    def save(self, commit=True):
        if self.cleaned_data.get('update_addresses'):
            update_order_with_user_addresses(self.instance)
        return super().save(commit)


class OrderShippingForm(forms.ModelForm):
    """Set shipping name and shipping price in an order."""

    shipping_method = AjaxSelect2ChoiceField(
        queryset=ShippingMethodCountry.objects.all(),
        required=False, min_input=0)

    class Meta:
        model = Order
        fields = ['shipping_method']
        labels = {
            'shipping_method': pgettext_lazy(
                'Shipping method form field label', 'Shipping method')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        method_field = self.fields['shipping_method']
        fetch_data_url = reverse(
            'dashboard:ajax-order-shipping-methods',
            kwargs={'order_pk': self.instance.id})
        method_field.set_fetch_data_url(fetch_data_url)

        method = self.instance.shipping_method
        if method:
            method_field.set_initial(method, label=method.label)
        else:
            method_field.set_initial(None, obj_id='', label='----')

        if self.instance.shipping_address:
            country_code = self.instance.shipping_address.country.code
            queryset = method_field.queryset.unique_for_country_code(
                country_code)
            method_field.queryset = queryset

    def save(self, commit=True):
        method = self.instance.shipping_method
        if method:
            self.instance.shipping_method_name = method.shipping_method.name
            self.instance.shipping_price = method.get_total_price()
        else:
            self.instance.shipping_method_name = None
            self.instance.shipping_price = ZERO_TAXED_MONEY
        return super().save(commit)


class OrderNoteForm(forms.ModelForm):
    class Meta:
        model = OrderNote
        fields = ['content', 'is_public']
        widgets = {
            'content': forms.Textarea()}
        labels = {
            'content': pgettext_lazy('Order note', 'Note'),
            'is_public': pgettext_lazy(
                'Allow customers to see note toggle',
                'Customer can see this note')}

    def send_confirmation_email(self):
        order = self.instance.order
        send_note_confirmation.delay(order.pk)


class ManagePaymentForm(forms.Form):
    amount = MoneyField(
        label=pgettext_lazy(
            'Payment management form (capture, refund, release)', 'Amount'),
        max_digits=12,
        decimal_places=2,
        currency=settings.DEFAULT_CURRENCY)

    def __init__(self, *args, **kwargs):
        self.payment = kwargs.pop('payment')
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.payment.status != self.clean_status:
            raise forms.ValidationError(self.clean_error)

    def payment_error(self, message):
        self.add_error(
            None, pgettext_lazy(
                'Payment form error', 'Payment gateway error: %s') % message)

    def try_payment_action(self, action):
        money = self.cleaned_data['amount']
        try:
            action(money.amount)
        except (PaymentError, ValueError) as e:
            self.payment_error(str(e))
            return False
        return True


class CapturePaymentForm(ManagePaymentForm):

    clean_status = PaymentStatus.PREAUTH
    clean_error = pgettext_lazy('Payment form error',
                                'Only pre-authorized payments can be captured')

    def capture(self):
        return self.try_payment_action(self.payment.capture)


class RefundPaymentForm(ManagePaymentForm):

    clean_status = PaymentStatus.CONFIRMED
    clean_error = pgettext_lazy('Payment form error',
                                'Only confirmed payments can be refunded')

    def refund(self):
        return self.try_payment_action(self.payment.refund)


class ReleasePaymentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.payment = kwargs.pop('payment')
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.payment.status != PaymentStatus.PREAUTH:
            raise forms.ValidationError(
                pgettext_lazy(
                    'Payment form error',
                    'Only pre-authorized payments can be released'))

    def payment_error(self, message):
        self.add_error(
            None, pgettext_lazy(
                'Payment form error', 'Payment gateway error: %s') % message)

    def release(self):
        try:
            self.payment.release()
        except (PaymentError, ValueError) as e:
            self.payment_error(str(e))
            return False
        return True


class CancelOrderLineForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.line = kwargs.pop('line')
        super().__init__(*args, **kwargs)

    def cancel_line(self):
        if self.line.stock:
            deallocate_stock(self.line.stock, self.line.quantity)
        order = self.line.order
        self.line.delete()
        recalculate_order(order)


class ChangeQuantityForm(forms.ModelForm):
    quantity = QuantityField(
        validators=[MinValueValidator(1)])

    class Meta:
        model = OrderLine
        fields = ['quantity']
        labels = {
            'quantity': pgettext_lazy(
                'Integer number', 'Quantity')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_quantity = self.instance.quantity
        self.fields['quantity'].initial = self.initial_quantity

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        delta = quantity - self.initial_quantity
        stock = self.instance.stock
        if stock and delta > stock.quantity_available:
            raise forms.ValidationError(
                npgettext_lazy(
                    'Change quantity form error',
                    'Only %(remaining)d remaining in stock.',
                    'Only %(remaining)d remaining in stock.',
                    'remaining') % {
                        'remaining': (
                            self.initial_quantity + stock.quantity_available)})
        return quantity

    def save(self):
        quantity = self.cleaned_data['quantity']
        stock = self.instance.stock
        if stock is not None:
            # update stock allocation
            delta = quantity - self.initial_quantity
            allocate_stock(stock, delta)
        change_order_line_quantity(self.instance, quantity)
        recalculate_order(self.instance.order)
        return self.instance


class CancelOrderForm(forms.Form):
    """Allow canceling an entire order.

    Deallocate or increase corresponding stocks for each order line.
    """

    restock = forms.BooleanField(initial=True, required=False)

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order')
        super().__init__(*args, **kwargs)
        self.fields['restock'].label = npgettext_lazy(
            'Cancel order form action',
            'Restock %(quantity)d item',
            'Restock %(quantity)d items',
            'quantity') % {'quantity': self.order.get_total_quantity()}

    def clean(self):
        data = super().clean()
        if not self.order.can_cancel():
            raise forms.ValidationError(
                pgettext_lazy(
                    'Cancel order form error',
                    "This order can't be cancelled"))
        return data

    def cancel_order(self):
        cancel_order(self.order, self.cleaned_data.get('restock'))


class CancelFulfillmentForm(forms.Form):
    """Allow canceling an entire fulfillment.

    Increase corresponding stocks for each fulfillment line.
    """

    restock = forms.BooleanField(initial=True, required=False)

    def __init__(self, *args, **kwargs):
        self.fulfillment = kwargs.pop('fulfillment')
        super().__init__(*args, **kwargs)
        self.fields['restock'].label = npgettext_lazy(
            'Cancel fulfillment form action',
            'Restock %(quantity)d item',
            'Restock %(quantity)d items',
            'quantity') % {'quantity': self.fulfillment.get_total_quantity()}

    def clean(self):
        data = super().clean()
        if not self.fulfillment.can_edit():
            raise forms.ValidationError(
                pgettext_lazy(
                    'Cancel fulfillment form error',
                    'This fulfillment can\'t be canceled'))
        return data

    def cancel_fulfillment(self):
        cancel_fulfillment(self.fulfillment, self.cleaned_data.get('restock'))


class FulfillmentTrackingNumberForm(forms.ModelForm):
    """Update tracking number in fulfillment group."""

    send_mail = forms.BooleanField(
        initial=True, required=False, label=pgettext_lazy(
            'Send mail to customer',
            'Send notification email to customer'))

    class Meta:
        model = Fulfillment
        fields = ['tracking_number']
        labels = {
            'tracking_number': pgettext_lazy(
                'Fulfillment record', 'Tracking number')}


class RemoveVoucherForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order')
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        if not self.order.voucher:
            raise forms.ValidationError(
                pgettext_lazy(
                    'Remove voucher form error',
                    'This order has no voucher'))
        return data

    def remove_voucher(self):
        self.order.discount_amount = 0
        self.order.discount_name = ''
        decrease_voucher_usage(self.order.voucher)
        self.order.voucher = None
        recalculate_order(self.order)


PAYMENT_STATUS_CHOICES = (
    [('', pgettext_lazy('Payment status field value', 'All'))] +
    PaymentStatus.CHOICES)


class PaymentFilterForm(forms.Form):
    status = forms.ChoiceField(choices=PAYMENT_STATUS_CHOICES)


class StockChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.location.name


class ChangeStockForm(forms.ModelForm):
    stock = StockChoiceField(queryset=Stock.objects.none())

    class Meta:
        model = OrderLine
        fields = ['stock']
        labels = {
            'stock': pgettext_lazy(
                'Stock record', 'Stock')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sku = self.instance.product_sku
        self.fields['stock'].queryset = Stock.objects.filter(variant__sku=sku)
        self.old_stock = self.instance.stock

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock and stock.quantity_available < self.instance.quantity:
            raise forms.ValidationError(
                pgettext_lazy(
                    'Change stock form error',
                    'Only %(remaining)d remaining in this stock.') % {
                        'remaining': stock.quantity_available})
        return stock

    def save(self, commit=True):
        quantity = self.instance.quantity
        stock = self.instance.stock
        self.instance.stock_location = (
            stock.location.name if stock.location else '')
        if self.old_stock:
            deallocate_stock(self.old_stock, quantity)
        allocate_stock(stock, quantity)
        super().save(commit)
        merge_duplicates_into_order_line(self.instance)
        return self.instance


class AddVariantToOrderForm(forms.Form):
    """Allow adding lines with given quantity to an order."""

    variant = AjaxSelect2ChoiceField(
        queryset=ProductVariant.objects.filter(
            product__in=Product.objects.available_products()),
        fetch_data_url=reverse_lazy('dashboard:ajax-available-variants'))
    quantity = QuantityField(
        label=pgettext_lazy(
            'Add variant to order form label', 'Quantity'),
        validators=[MinValueValidator(1)])

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order')
        self.discounts = kwargs.pop('discounts')
        super().__init__(*args, **kwargs)

    def clean(self):
        """Check if given quantity is available in stocks."""
        cleaned_data = super().clean()
        variant = cleaned_data.get('variant')
        quantity = cleaned_data.get('quantity')
        if variant and quantity is not None:
            try:
                variant.check_quantity(quantity)
            except InsufficientStock as e:
                error = forms.ValidationError(
                    pgettext_lazy(
                        'Add item form error',
                        'Could not add item. '
                        'Only %(remaining)d remaining in stock.' %
                        {'remaining': e.item.get_stock_quantity()}))
                self.add_error('quantity', error)
        return cleaned_data

    def save(self):
        """Add variant to order.

        Updates stocks and order.
        """
        variant = self.cleaned_data.get('variant')
        quantity = self.cleaned_data.get('quantity')
        add_variant_to_order(
            self.order, variant, quantity, self.discounts)
        recalculate_order(self.order)


class AddressForm(StorefrontAddressForm):
    phone = PossiblePhoneNumberFormField(
        widget=PhonePrefixWidget, required=False)


class FulfillmentForm(forms.ModelForm):
    """Create fulfillment group for a given order."""

    send_mail = forms.BooleanField(
        initial=True, required=False, label=pgettext_lazy(
            'Send mail to customer',
            'Send shipment details to your customer now'))

    class Meta:
        model = Fulfillment
        fields = ['tracking_number']
        labels = {
            'tracking_number': pgettext_lazy(
                'Order tracking number',
                'Tracking number')}

    def __init__(self, *args, **kwargs):
        order = kwargs.pop('order')
        super().__init__(*args, **kwargs)
        self.instance.order = order


class BaseFulfillmentLineFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class FulfillmentLineForm(forms.ModelForm):
    """Fulfill order line with given quantity by decreasing stock."""

    class Meta:
        model = FulfillmentLine
        fields = ['order_line', 'quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        order_line = self.cleaned_data.get('order_line')
        if quantity > order_line.quantity_unfulfilled:
            raise forms.ValidationError(npgettext_lazy(
                'Fulfill order line form error',
                '%(quantity)d item remaining to fulfill.',
                '%(quantity)d items remaining to fulfill.',
                'quantity') % {
                    'quantity': order_line.quantity_unfulfilled,
                    'order_line': order_line})
        return quantity

    def save(self, commit=True):
        fulfill_order_line(self.instance.order_line, self.instance.quantity)
        return super().save(commit)
