from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import is_possible_number

from ..graphql.core.utils.error_codes import AccountErrorCode


def validate_possible_number(phone, country=None):
    phone_number = to_python(phone, country)
    if (
        phone_number
        and not is_possible_number(phone_number)
        or not phone_number.is_valid()
    ):
        raise ValidationError(
            _("The phone number entered is not valid."), code=AccountErrorCode.INVALID
        )
    return phone_number
