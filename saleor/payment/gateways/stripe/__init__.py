from typing import Dict

import stripe

from ... import TransactionKind
from ...interface import GatewayResponse, PaymentData
from .forms import StripePaymentModalForm
from .utils import (
    get_amount_for_stripe, get_amount_from_stripe, get_currency_for_stripe,
    get_currency_from_stripe, get_payment_billing_fullname,
    shipping_to_stripe_dict)

TEMPLATE_PATH = 'order/payment/stripe.html'


def get_client_token(**_):
    """Not implemented for stripe gateway currently. The client token can be
    generated by Stripe's checkout.js or stripe.js automatically.
    """
    return


def authorize(
        payment_information: PaymentData, connection_params: Dict
) -> GatewayResponse:
    client, error = _get_client(**connection_params), None

    try:
        # Authorize without capture
        response = _create_stripe_charge(
            client=client, payment_information=payment_information,
            should_capture=False)
    except stripe.error.StripeError as exc:
        response = _get_error_response_from_exc(exc)
        error = exc.user_message

    # Create response
    return _create_response(
        payment_information=payment_information,
        kind=TransactionKind.AUTH, response=response, error=error)


def capture(
        payment_information: PaymentData, connection_params: Dict
) -> GatewayResponse:
    client, error = _get_client(**connection_params), None

    # Get amount from argument or payment, and convert to stripe's amount
    amount = payment_information.amount
    stripe_amount = get_amount_for_stripe(
        amount, payment_information.currency)

    try:
        # Retrieve stripe charge and capture specific amount
        stripe_charge = client.Charge.retrieve(payment_information.token)
        response = stripe_charge.capture(amount=stripe_amount)
    except stripe.error.StripeError as exc:
        response = _get_error_response_from_exc(exc)
        error = exc.user_message

    # Create response
    return _create_response(
        payment_information=payment_information,
        kind=TransactionKind.CAPTURE, response=response, error=error)


def refund(
        payment_information: PaymentData, connection_params: Dict
) -> GatewayResponse:
    client, error = _get_client(**connection_params), None

    # Get amount from payment, and convert to stripe's amount
    amount = payment_information.amount
    stripe_amount = get_amount_for_stripe(
        amount, payment_information.currency)

    try:
        # Retrieve stripe charge and refund specific amount
        stripe_charge = client.Charge.retrieve(payment_information.token)
        response = client.Refund.create(
            charge=stripe_charge.id, amount=stripe_amount)
    except stripe.error.StripeError as exc:
        response = _get_error_response_from_exc(exc)
        error = exc.user_message

    # Create response
    return _create_response(
        payment_information=payment_information,
        kind=TransactionKind.REFUND, response=response, error=error)


def void(
        payment_information: PaymentData, connection_params: Dict
) -> GatewayResponse:
    client, error = _get_client(**connection_params), None

    try:
        # Retrieve stripe charge and refund all
        stripe_charge = client.Charge.retrieve(payment_information.token)
        response = client.Refund.create(charge=stripe_charge.id)
    except stripe.error.StripeError as exc:
        response = _get_error_response_from_exc(exc)
        error = exc.user_message

    # Create response
    return _create_response(
        payment_information=payment_information,
        kind=TransactionKind.VOID, response=response, error=error)


def process_payment(
        payment_information: PaymentData, connection_params: Dict
) -> GatewayResponse:
    return charge(payment_information, connection_params)


def create_form(
        data: Dict, payment_information: PaymentData,
        connection_params: Dict) -> StripePaymentModalForm:
    return StripePaymentModalForm(
        data=data, payment_information=payment_information,
        gateway_params=connection_params)


def _get_client(**connection_params):
    stripe.api_key = connection_params.get('secret_key')
    return stripe


def _get_stripe_charge_payload(
        payment_information: PaymentData, should_capture: bool) -> Dict:
    shipping = payment_information.shipping

    # Get currency
    currency = get_currency_for_stripe(payment_information.currency)

    # Get appropriate amount for stripe
    stripe_amount = get_amount_for_stripe(
        payment_information.amount, currency)

    # Get billing name from payment
    name = get_payment_billing_fullname(payment_information)

    # Construct the charge payload from the data
    charge_payload = {
        'capture': should_capture,
        'amount': stripe_amount,
        'currency': currency,
        'source': payment_information.token,
        'description': name}

    if shipping:
        # Update shipping address to prevent fraud in Stripe
        charge_payload['shipping'] = {
            'name': name,
            'address': shipping_to_stripe_dict(shipping)}

    return charge_payload


def _create_stripe_charge(client, payment_information, should_capture: bool):
    """Create a charge with specific amount, ignoring payment's total."""
    charge_payload = _get_stripe_charge_payload(
        payment_information, should_capture)
    return client.Charge.create(**charge_payload)


def _create_response(
        payment_information: PaymentData, kind: str, response: Dict,
        error: str) -> GatewayResponse:
    # Get currency from response or payment
    currency = get_currency_from_stripe(
        response.get('currency', payment_information.currency))

    amount = payment_information.amount
    # Get amount from response or payment
    if 'amount' in response:
        stripe_amount = response.get('amount')
        if 'amount_refunded' in response:
            # This happens for partial catpure which will refund the left
            # Then the actual amount should minus refunded amount
            stripe_amount -= response.get('amount_refunded')
        amount = get_amount_from_stripe(stripe_amount, currency)

    # Get token from response or use provided one
    token = response.get('id', payment_information.token)

    # Check if the response's status is flagged as succeeded
    is_success = (response.get('status') == 'succeeded')
    return GatewayResponse(
        is_success=is_success,
        transaction_id=token,
        kind=kind,
        amount=amount,
        currency=currency,
        error=error,
        raw_response=response
    )


def _get_error_response_from_exc(exc):
    response = exc.json_body

    # Some errors from stripe don't json_body as None
    # such as stripe.error.InvalidRequestError
    if response is None:
        response = dict()

    return response
