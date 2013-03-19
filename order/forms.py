from .models import DigitalDeliveryGroup
from django import forms
from django.core.exceptions import ValidationError
from userprofile.forms import AddressForm
from django.utils.translation import ugettext_lazy as _


class ShippingForm(AddressForm):

    use_billing = forms.BooleanField(initial=True)


class ManagementForm(forms.Form):

    CHOICES = (
        ('select', 'Select address'),
        ('new', 'Complete address')
    )

    choice_method = forms.ChoiceField(choices=CHOICES, initial=CHOICES[0][0])

    def __init__(self, is_user_authenticated, *args, **kwargs):
        super(ManagementForm, self).__init__(*args, **kwargs)
        if not is_user_authenticated:
            choice_method = self.fields['choice_method']
            choice_method.initial = self.CHOICES[1][0]
            choice_method.widget = choice_method.hidden_widget()


class DigitalDeliveryForm(forms.ModelForm):

    class Meta:
        model = DigitalDeliveryGroup
        exclude = ['order', 'price']

    def __init__(self, *args, **kwargs):
        super(DigitalDeliveryForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True


class DeliveryField(forms.ChoiceField):

    def __init__(self, methods, *args, **kwargs):
        self.methods = list(methods)
        choices = [(index, unicode(method)) for index, method in
                   enumerate(self.methods)]
        super(DeliveryField, self).__init__(choices, *args, **kwargs)

    def to_python(self, value):
        try:
            return self.methods[int(value)]
        except (IndexError, ValueError):
            raise ValidationError(
                self.error_messages['invalid_choice'] % value)

    def valid_value(self, value):
        return value in self.methods


class DeliveryForm(forms.Form):

    def __init__(self, group, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)
        self.fields['method'] = DeliveryField(group.get_delivery_methods())
