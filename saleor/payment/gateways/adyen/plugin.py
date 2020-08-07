import json
from typing import List, Optional
from urllib.parse import urlencode

import Adyen
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseNotFound
from graphql_relay import from_global_id

from ....checkout.models import Checkout
from ....core.utils import build_absolute_uri
from ....core.utils.url import prepare_url
from ....plugins.base_plugin import BasePlugin, ConfigurationTypeField
from ... import PaymentError, TransactionKind
from ...interface import GatewayConfig, GatewayResponse, PaymentData, PaymentGateway
from ...models import Payment, Transaction
from ..utils import get_supported_currencies
from .utils import (
    api_call,
    call_capture,
    request_data_for_gateway_config,
    request_data_for_payment,
    request_for_payment_refund,
    update_payment_with_action_required_data,
)
from .webhooks import handle_additional_actions, handle_webhook

GATEWAY_NAME = "Adyen"
WEBHOOK_PATH = "/webhooks"
ADDITIONAL_ACTION_PATH = "/additional-actions"


def require_active_plugin(fn):
    def wrapped(self, *args, **kwargs):
        previous = kwargs.get("previous_value", None)
        if not self.active:
            return previous
        return fn(self, *args, **kwargs)

    return wrapped


# https://docs.adyen.com/checkout/payment-result-codes
FAILED_STATUSES = ["refused", "error", "cancelled"]
PENDING_STATUSES = ["pending", "received"]
AUTH_STATUS = "authorised"


class AdyenGatewayPlugin(BasePlugin):
    PLUGIN_ID = "mirumee.payments.adyen"
    PLUGIN_NAME = GATEWAY_NAME
    DEFAULT_CONFIGURATION = [
        {"name": "Merchant Account", "value": None},
        {"name": "API key", "value": None},
        {"name": "Supported currencies", "value": ""},
        {"name": "Origin Key", "value": ""},
        {"name": "Origin Url", "value": ""},
        {"name": "Live", "value": ""},
        {"name": "Automatically mark payment as a capture", "value": True},
        {"name": "Automatic payment capture", "value": False},
        {"name": "HMAC secret key", "value": ""},
        {"name": "Notification user", "value": ""},
        {"name": "Notification password", "value": ""},
    ]

    CONFIG_STRUCTURE = {
        "API key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": (
                "To submit payments to Adyen, you'll be making API requests that are "
                "authenticated with an API key. You can generate API keys on your "
                "Customer Area."
            ),
            "label": "API key",
        },
        "Merchant Account": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Yout merchant account name.",
            "label": "Merchant Account",
        },
        "Supported currencies": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Determines currencies supported by gateway."
            " Please enter currency codes separated by a comma.",
            "label": "Supported currencies",
        },
        "Origin Key": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "",  # FIXME define them as per channel
            "label": "Origin Key",
        },
        "Origin Url": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "",  # FIXME define them as per channel
            "label": "Origin Url",
        },
        "Live": {
            "type": ConfigurationTypeField.STRING,
            "help_text": (
                "Leave it blank when you want to use test env. To communicate with the"
                " Adyen API you should submit HTTP POST requests to corresponding "
                "endpoints. These endpoints differ for test and live accounts, and also"
                " depend on the data format (SOAP, JSON, or FORM) you use to submit "
                "data to the Adyen payments platform. "
                "https://docs.adyen.com/development-resources/live-endpoints"
            ),
            "label": "Live",
        },
        "Enable notifications": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": (
                "Enable the support for processing the Adyen's webhooks. The Saleor "
                "webhook url is "
                "http(s)://<your-backend-url>/plugins/mirumee.payments.adyen/webhooks/ "
                "https://docs.adyen.com/development-resources/webhooks"
            ),
            "label": "Enable notifications",
        },
        "Automatically mark payment as a capture": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": (
                "All authorized payments will be marked as paid. This should be enabled"
                " when Adyen uses automatically auto-capture. Saleor doesn't support "
                "delayed automatically capture."
            ),
            "label": "Automatically mark payment as a capture",
        },
        "Automatic payment capture": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should automaticaly capture payments.",
            "label": "Automatic payment capture",
        },
        "HMAC secret key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": (
                "Provide secret key generated on Adyen side."
                "https://docs.adyen.com/development-resources/webhooks#set-up-notificat"
                "ions-in-your-customer-area. The Saleor webhook url is "
                "http(s)://<your-backend-url>/plugins/mirumee.payments.adyen/webhooks/"
            ),
            "label": "HMAC secret key",
        },
        "Notification user": {
            "type": ConfigurationTypeField.STRING,
            "help_text": (
                "Base User provided on the Adyen side for authenticate incoming "
                "notifications. https://docs.adyen.com/development-resources/webhooks#"
                "set-up-notifications-in-your-customer-area "
                "The Saleor webhook url is "
                "http(s)://<your-backend-url>/plugins/mirumee.payments.adyen/webhooks/"
            ),
            "label": "Notification user",
        },
        "Notification password": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": (
                "User password provided on the Adyen side for authenticate incoming "
                "notifications. https://docs.adyen.com/development-resources/webhooks#"
                "set-up-notifications-in-your-customer-area "
                "The Saleor webhook url is "
                "http(s)://<your-backend-url>/plugins/mirumee.payments.adyen/webhooks/"
            ),
            "label": "Notification password",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=configuration["Automatic payment capture"],
            supported_currencies=configuration["Supported currencies"],
            connection_params={
                "api_key": configuration["API key"],
                "merchant_account": configuration["Merchant Account"],
                "origin_key": configuration["Origin Key"],
                "origin_url": configuration["Origin Url"],
                "live": configuration["Live"],
                "webhook_hmac": configuration["HMAC secret key"],
                "webhook_user": configuration["Notification user"],
                "webhook_user_password": configuration["Notification password"],
                "adyen_auto_capture": configuration[
                    "Automatically mark payment as a capture"
                ],
            },
        )
        api_key = self.config.connection_params["api_key"]

        live_endoint = self.config.connection_params["live"] or None
        platform = "live" if live_endoint else "test"
        self.adyen = Adyen.Adyen(
            xapikey=api_key, live_endpoint_prefix=live_endoint, platform=platform
        )

    def webhook(self, request: WSGIRequest, path: str, previous_value) -> HttpResponse:
        config = self._get_gateway_config()
        self.config.connection_params["adyen_auto_capture"]
        if path.startswith(WEBHOOK_PATH):
            return handle_webhook(request, config)
        elif path.startswith(ADDITIONAL_ACTION_PATH):
            return handle_additional_actions(
                request,
                self.adyen.checkout.payments_details,
                config.connection_params["adyen_auto_capture"],
                config.auto_capture,
            )
        return HttpResponseNotFound()

    def _get_gateway_config(self) -> GatewayConfig:
        return self.config

    @require_active_plugin
    def token_is_required_as_payment_input(self, previous_value):
        return False

    @require_active_plugin
    def get_payment_gateway_for_checkout(
        self, checkout: "Checkout", previous_value,
    ) -> Optional["PaymentGateway"]:

        config = self._get_gateway_config()
        request = request_data_for_gateway_config(
            checkout, config.connection_params["merchant_account"]
        )
        response = api_call(request, self.adyen.checkout.payment_methods)
        return PaymentGateway(
            id=self.PLUGIN_ID,
            name=self.PLUGIN_NAME,
            config=[
                {
                    "field": "origin_key",
                    "value": config.connection_params["origin_key"],
                },
                {"field": "config", "value": json.dumps(response.message)},
            ],
            currencies=self.get_supported_currencies([]),
        )

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        _type, payment_pk = from_global_id(payment_information.payment_id)
        try:
            payment = Payment.objects.get(pk=payment_pk)
        except ObjectDoesNotExist:
            raise PaymentError("Payment cannot be performed. Payment does not exists.")

        checkout = payment.checkout
        if checkout is None:
            raise PaymentError(
                "Payment cannot be performed. Checkout for this payment does not exist."
            )

        params = urlencode(
            {"payment": payment_information.payment_id, "checkout": checkout.pk}
        )
        return_url = prepare_url(
            params,
            build_absolute_uri(
                f"/plugins/{self.PLUGIN_ID}/additional-actions"
            ),  # type: ignore
        )
        request_data = request_data_for_payment(
            payment_information,
            return_url=return_url,
            merchant_account=self.config.connection_params["merchant_account"],
            origin_url=self.config.connection_params["origin_url"],
        )
        result = api_call(request_data, self.adyen.checkout.payments)
        result_code = result.message["resultCode"].strip().lower()
        is_success = result_code not in FAILED_STATUSES
        adyen_auto_capture = self.config.connection_params["adyen_auto_capture"]
        kind = TransactionKind.AUTH
        if adyen_auto_capture:
            kind = TransactionKind.CAPTURE
        elif result_code in PENDING_STATUSES:
            kind = TransactionKind.PENDING

        # If auto capture is enabled, let's make a capture the auth payment
        if self.config.auto_capture and result_code == AUTH_STATUS:
            kind = TransactionKind.CAPTURE
            result = call_capture(
                payment_information=payment_information,
                merchant_account=self.config.connection_params["merchant_account"],
                token=result.message.get("pspReference"),
                adyen_client=self.adyen,
            )

        action = result.message.get("action")
        error_message = result.message.get("refusalReason")
        if action:
            update_payment_with_action_required_data(
                payment, action, result.message.get("details", []),
            )

        return GatewayResponse(
            is_success=is_success,
            action_required="action" in result.message,
            kind=kind,
            amount=payment_information.amount,
            currency=payment_information.currency,
            transaction_id=result.message.get("pspReference", ""),
            error=error_message,
            raw_response=result.message,
            action_required_data=action,
        )

    @classmethod
    def _update_config_items(
        cls, configuration_to_update: List[dict], current_config: List[dict]
    ):
        super()._update_config_items(configuration_to_update, current_config)
        for item in current_config:
            if item.get("name") == "Notification password" and item["value"]:
                item["value"] = make_password(item["value"])

    @require_active_plugin
    def get_payment_config(self, previous_value):
        return []

    @require_active_plugin
    def get_supported_currencies(self, previous_value):
        config = self._get_gateway_config()
        return get_supported_currencies(config, GATEWAY_NAME)

    @require_active_plugin
    def confirm_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":

        _type, payment_id = from_global_id(payment_information.payment_id)

        # The additional checks are proceed asynchronously so we try to confirm that
        # the payment is already processed
        payment = Payment.objects.filter(id=payment_id).first()
        if not payment:
            raise PaymentError("Unable to find the payment.")

        transaction = (
            payment.transactions.filter(
                payment__id=payment_id,
                kind__in=[TransactionKind.AUTH, TransactionKind.CAPTURE],
                is_success=True,
            )
            .exclude(token__isnull=True, token__exact="")
            .last()
        )
        if not transaction:
            raise PaymentError(
                "Unable to finish the payment. Payment needs to be confirm by external "
                "source."
            )
        return GatewayResponse(
            is_success=transaction.is_success,
            action_required=False,
            kind=TransactionKind.CONFIRM,
            amount=transaction.amount,
            currency=transaction.currency,
            transaction_id=transaction.token,
            error=None,
            raw_response={},
        )

    @require_active_plugin
    def refund_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":

        _type, payment_id = from_global_id(payment_information.payment_id)
        # we take Auth kind because it contains the transaction id that we need
        transaction = (
            Transaction.objects.filter(
                payment__id=payment_id, kind=TransactionKind.AUTH, is_success=True
            )
            .exclude(token__isnull=True, token__exact="")
            .last()
        )

        if not transaction:
            raise PaymentError("Cannot find a payment reference to refund.")

        request = request_for_payment_refund(
            payment_information=payment_information,
            merchant_account=self.config.connection_params["merchant_account"],
            token=transaction.token,
        )
        result = api_call(request, self.adyen.payment.refund)

        return GatewayResponse(
            is_success=True,
            action_required=False,
            kind=TransactionKind.REFUND_ONGOING,
            amount=payment_information.amount,
            currency=payment_information.currency,
            transaction_id=result.message.get("pspReference", ""),
            error="",
            raw_response=result.message,
        )

    @require_active_plugin
    def capture_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        _type, payment_id = from_global_id(payment_information.payment_id)
        transaction = (
            Transaction.objects.filter(
                payment__id=payment_id, kind=TransactionKind.AUTH, is_success=True
            )
            .exclude(token__isnull=True, token__exact="")
            .last()
        )
        if not transaction:
            raise PaymentError("Cannot find a payment reference to capture.")

        result = call_capture(
            payment_information=payment_information,
            merchant_account=self.config.connection_params["merchant_account"],
            token=transaction.token,
            adyen_client=self.adyen,
        )
        return GatewayResponse(
            is_success=True,
            action_required=False,
            kind=TransactionKind.CAPTURE,
            amount=payment_information.amount,
            currency=payment_information.currency,
            transaction_id=result.message.get("pspReference", ""),
            error="",
            raw_response=result.message,
        )
