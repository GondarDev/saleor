from django import forms
from django.utils.translation import pgettext_lazy

from ...core.weight import WeightField
from ...shipping import ShippingMethodType
from ...shipping.models import ShippingMethod, ShippingZone


def currently_used_countries(shipping_zone_pk=None):
    shipping_zones = ShippingZone.objects.exclude(pk=shipping_zone_pk)
    used_countries = {
        (country.code, country.name)
        for shipping_zone in shipping_zones
        for country in shipping_zone.countries}
    return used_countries


class ShippingZoneForm(forms.ModelForm):

    class Meta:
        model = ShippingZone
        exclude = ['shipping_methods']
        labels = {
            'name': pgettext_lazy('Shippment Zone field name', 'Zone Name'),
            'countries': pgettext_lazy(
                'List of countries to pick from', 'Countries')}
        help_texts = {
            'countries': pgettext_lazy(
                'Countries field help text',
                'Each country might be included in only one shipping zone.'),
            'name': pgettext_lazy(
                'Help text for ShippingZone name',
                'Name is for internal use only, it won\'t '
                'be displayed to your customers')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['countries'].choices = (
            set(self.fields['countries'].choices) - currently_used_countries(
                self.instance.pk if self.instance else None))

    def clean_countries(self):
        countries = self.cleaned_data.get('countries')
        if not countries:
            return
        duplicated_countries = set(countries).intersection(
            currently_used_countries())
        if duplicated_countries:
            self.add_error(
                'countries',
                'Countries already exists in another '
                'shipping zone: %(list_of_countries)s' % {
                    'list_of_countries': ', '.join(duplicated_countries)})
        return countries


class ShippingMethodForm(forms.ModelForm):
    class Meta:
        model = ShippingMethod
        fields = ['name', 'price']
        labels = {
            'name': pgettext_lazy('Shipping Method name', 'Name'),
            'price': pgettext_lazy('Currency amount', 'Price')}
        help_texts = {
            'name': pgettext_lazy(
                'Shipping method name help text',
                'Customers will see this at the checkout.')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PriceShippingMethodForm(forms.ModelForm):
    class Meta(ShippingMethodForm.Meta):
        labels = {
            'minimum_order_price': pgettext_lazy(
                'Minimum order price to use this shipping method',
                'Minimum order price'),
            'maximum_order_price': pgettext_lazy(
                'Maximum order price to use this order',
                'Maximum order price')}
        labels.update(ShippingMethodForm.Meta.labels)
        fields = [
            'name', 'price', 'minimum_order_price', 'maximum_order_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['maximum_order_price'].widget.attrs['placeholder'] = (
            pgettext_lazy(
                'Placeholder for maximum order price set to unlimited',
                'No limit'))
        self.fields['minimum_order_price'].widget.attrs['placeholder'] = '0'

    def clean_minimum_order_price(self):
        return self.cleaned_data['minimum_order_price'] or 0

    def clean(self):
        data = super().clean()
        min_price = data.get('minimum_order_price')
        max_price = data.get('maximum_order_price')
        if min_price and max_price is not None and max_price <= min_price:
            self.add_error('maximum_order_price', pgettext_lazy(
                'Price shipping method form error',
                'Maximum order price should be larger'
                ' than the minimum order price.'))
        return data


class WeightShippingMethodForm(forms.ModelForm):
    minimum_order_weight = WeightField(
        required=False, label=pgettext_lazy(
            'Minimum order weight to use this shipping method',
            'Minimum order weight'))
    maximum_order_weight = WeightField(
        required=False, label=pgettext_lazy(
            'Maximum order weight to use this shipping method',
            'Maximum order weight'))

    class Meta(ShippingMethodForm.Meta):
        fields = [
            'name', 'price', 'minimum_order_weight', 'maximum_order_weight']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['maximum_order_weight'].widget.attrs['placeholder'] = (
            pgettext_lazy(
                'Placeholder for maximum order weight set to unlimited',
                'No limit'))
        self.fields['minimum_order_weight'].widget.attrs['placeholder'] = '0'

    def clean_minimum_order_weight(self):
        return self.cleaned_data['minimum_order_weight'] or 0

    def clean(self):
        data = super().clean()
        min_weight = data.get('minimum_order_weight')
        max_weight = data.get('maximum_order_weight')
        if min_weight and max_weight is not None and max_weight <= min_weight:
            self.add_error('maximum_order_weight', pgettext_lazy(
                'Price shipping method form error',
                'Maximum order price should be larger'
                ' than the minimum order price.'))
        return data


def get_shipping_form(type):
    if type == ShippingMethodType.WEIGHT_BASED:
        return WeightShippingMethodForm
    elif type == ShippingMethodType.PRICE_BASED:
        return PriceShippingMethodForm
    raise TypeError('Unknown form type: %s' % type)
