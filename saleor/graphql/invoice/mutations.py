import graphene
from django.core.exceptions import ValidationError

from ...core import JobStatus
from ...core.permissions import OrderPermissions
from ...invoice import events, models
from ...invoice.emails import send_invoice
from ...invoice.error_codes import InvoiceErrorCode
from ...order import OrderStatus
from ..core.mutations import ModelDeleteMutation, ModelMutation
from ..core.types.common import InvoiceError
from ..invoice.types import Invoice
from ..order.types import Order


class RequestInvoice(ModelMutation):
    class Meta:
        description = "Request an invoice for the order using plugin."
        model = models.Invoice
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = InvoiceError
        error_type_field = "invoice_errors"

    class Arguments:
        order_id = graphene.ID(
            required=True, description="ID of the order related to invoice."
        )
        number = graphene.String(
            required=False,
            description="Invoice number, if not provided it will be generated.",
        )

    @staticmethod
    def clean_order(order):
        if order.status == OrderStatus.DRAFT:
            raise ValidationError(
                {
                    "orderId": ValidationError(
                        "Cannot request an invoice for draft order.",
                        code=InvoiceErrorCode.INVALID_STATUS,
                    )
                }
            )

        if not order.billing_address:
            raise ValidationError(
                {
                    "orderId": ValidationError(
                        "Cannot request an invoice for order without billing address.",
                        code=InvoiceErrorCode.NOT_READY,
                    )
                }
            )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        order = cls.get_node_or_error(
            info, data["order_id"], only_type=Order, field="orderId"
        )
        cls.clean_order(order)

        invoice = models.Invoice.objects.create(order=order, number=data.get("number"),)

        info.context.plugins.invoice_request(
            order=order, invoice=invoice, number=data.get("number")
        )
        events.invoice_requested_event(
            user=info.context.user, order=order, number=data.get("number")
        )
        invoice.refresh_from_db()
        return RequestInvoice(invoice=invoice)


class CreateInvoiceInput(graphene.InputObjectType):
    number = graphene.String(required=True, description="Invoice number.")
    url = graphene.String(required=True, description="URL of an invoice to download.")


class CreateInvoice(ModelMutation):
    class Arguments:
        order_id = graphene.ID(
            required=True, description="ID of the order related to invoice."
        )
        input = CreateInvoiceInput(
            required=True, description="Fields required when creating an invoice."
        )

    class Meta:
        description = "Creates a ready to send invoice."
        model = models.Invoice
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = InvoiceError
        error_type_field = "invoice_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        validation_errors = {}
        for field in ["url", "number"]:
            if data["input"][field] == "":
                validation_errors[field] = ValidationError(
                    f"{field} cannot be empty.", code=InvoiceErrorCode.REQUIRED,
                )
        if validation_errors:
            raise ValidationError(validation_errors)
        return data["input"]

    @classmethod
    def clean_order(cls, info, order):
        if order.status == OrderStatus.DRAFT:
            raise ValidationError(
                {
                    "orderId": ValidationError(
                        "Cannot request an invoice for draft order.",
                        code=InvoiceErrorCode.INVALID_STATUS,
                    )
                }
            )

        if not order.billing_address:
            raise ValidationError(
                {
                    "orderId": ValidationError(
                        "Cannot request an invoice for order without billing address.",
                        code=InvoiceErrorCode.NOT_READY,
                    )
                }
            )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        order = cls.get_node_or_error(
            info, data["order_id"], only_type=Order, field="orderId"
        )
        cls.clean_order(info, order)
        cleaned_input = cls.clean_input(info, order, data)
        invoice = models.Invoice(**cleaned_input)
        invoice.order = order
        invoice.status = JobStatus.SUCCESS
        invoice.save()
        events.invoice_created_event(
            user=info.context.user,
            invoice=invoice,
            number=cleaned_input["number"],
            url=cleaned_input["url"],
        )
        return CreateInvoice(invoice=invoice)


class RequestDeleteInvoice(ModelMutation):
    class Arguments:
        id = graphene.ID(
            required=True, description="ID of an invoice to request the deletion."
        )

    class Meta:
        description = "Requests deletion of an invoice."
        model = models.Invoice
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = InvoiceError
        error_type_field = "invoice_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        invoice = cls.get_node_or_error(info, data["id"], only_type=Invoice)
        invoice.status = JobStatus.PENDING
        invoice.save(update_fields=["status", "updated_at"])
        info.context.plugins.invoice_delete(invoice)
        events.invoice_requested_deletion_event(user=info.context.user, invoice=invoice)
        return RequestDeleteInvoice(invoice=invoice)


class DeleteInvoice(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of an invoice to delete.")

    class Meta:
        description = "Deletes an invoice."
        model = models.Invoice
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = InvoiceError
        error_type_field = "invoice_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        invoice = cls.get_instance(info, **data)
        response = super().perform_mutation(_root, info, **data)
        events.invoice_deleted_event(user=info.context.user, invoice_id=invoice.pk)
        return response


class UpdateInvoiceInput(graphene.InputObjectType):
    number = graphene.String(description="Invoice number")
    url = graphene.String(description="URL of an invoice to download.")


class UpdateInvoice(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of an invoice to update.")
        input = UpdateInvoiceInput(
            required=True, description="Fields to use when updating an invoice."
        )

    class Meta:
        description = "Updates an invoice."
        model = models.Invoice
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = InvoiceError
        error_type_field = "invoice_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        number = instance.number or data["input"].get("number")
        url = instance.external_url or data["input"].get("url")

        validation_errors = {}
        if not number:
            validation_errors["number"] = ValidationError(
                "Number need to be set after update operation.",
                code=InvoiceErrorCode.NUMBER_NOT_SET,
            )
        if not url:
            validation_errors["url"] = ValidationError(
                "URL need to be set after update operation.",
                code=InvoiceErrorCode.URL_NOT_SET,
            )

        if validation_errors:
            raise ValidationError(validation_errors)

        return data["input"]

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        instance = cls.get_instance(info, **data)
        cleaned_input = cls.clean_input(info, instance, data)
        instance.update_invoice(
            number=cleaned_input.get("number"), url=cleaned_input.get("url")
        )
        instance.status = JobStatus.SUCCESS
        instance.save(update_fields=["external_url", "number", "updated_at", "status"])
        return UpdateInvoice(invoice=instance)


class SendInvoiceEmail(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of an invoice to be sent.")

    class Meta:
        description = "Send an invoice by email."
        model = models.Invoice
        permissions = (OrderPermissions.MANAGE_ORDERS,)
        error_type_class = InvoiceError
        error_type_field = "invoice_errors"

    @classmethod
    def clean_instance(cls, info, instance):
        validation_errors = {}
        if instance.status != JobStatus.SUCCESS:
            validation_errors["invoice"] = ValidationError(
                "Provided invoice is not ready to be sent.",
                code=InvoiceErrorCode.NOT_READY,
            )
        if not instance.url:
            validation_errors["url"] = ValidationError(
                "Provided invoice needs to have an URL.",
                code=InvoiceErrorCode.URL_NOT_SET,
            )
        if not instance.number:
            validation_errors["number"] = ValidationError(
                "Provided invoice needs to have an invoice number.",
                code=InvoiceErrorCode.NUMBER_NOT_SET,
            )
        if not instance.order.get_customer_email():
            validation_errors["order"] = ValidationError(
                "Provided invoice order needs an email address.",
                code=InvoiceErrorCode.EMAIL_NOT_SET,
            )

        if validation_errors:
            raise ValidationError(validation_errors)

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        instance = cls.get_instance(info, **data)
        cls.clean_instance(info, instance)
        send_invoice.delay(instance.pk, info.context.user.pk)
        return SendInvoiceEmail(invoice=instance)
