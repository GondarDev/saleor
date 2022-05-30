from typing import Iterable

import graphene
from django.core.exceptions import ValidationError

from ....checkout import AddressType, models
from ....checkout.error_codes import CheckoutErrorCode
from ....checkout.fetch import (
    CheckoutLineInfo,
    fetch_checkout_info,
    fetch_checkout_lines,
)
from ....checkout.utils import (
    change_shipping_address_in_checkout,
    is_shipping_required,
    recalculate_checkout_discount,
)
from ....core.tracing import traced_atomic_transaction
from ....product import models as product_models
from ....warehouse.reservations import is_reservation_enabled
from ...account.i18n import I18nMixin
from ...account.types import AddressInput
from ...core.descriptions import ADDED_IN_34, DEPRECATED_IN_3X_INPUT
from ...core.mutations import BaseMutation
from ...core.scalars import UUID
from ...core.types import CheckoutError
from ..types import Checkout
from .utils import (
    ERROR_DOES_NOT_SHIP,
    check_lines_quantity,
    get_checkout,
    update_checkout_shipping_method_if_invalid,
)


class CheckoutShippingAddressUpdate(BaseMutation, I18nMixin):
    checkout = graphene.Field(Checkout, description="An updated checkout.")

    class Arguments:
        id = graphene.ID(
            description="The checkout's ID." + ADDED_IN_34,
            required=False,
        )
        token = UUID(
            description=f"Checkout token.{DEPRECATED_IN_3X_INPUT} Use `id` instead.",
            required=False,
        )
        checkout_id = graphene.ID(
            required=False,
            description=(
                f"The ID of the checkout. {DEPRECATED_IN_3X_INPUT} Use `id` instead."
            ),
        )
        shipping_address = AddressInput(
            required=True,
            description="The mailing address to where the checkout will be shipped.",
        )

    class Meta:
        description = "Update shipping address in the existing checkout."
        error_type_class = CheckoutError
        error_type_field = "checkout_errors"

    @classmethod
    def process_checkout_lines(
        cls,
        info,
        lines: Iterable["CheckoutLineInfo"],
        country: str,
        channel_slug: str,
    ) -> None:
        variant_ids = [line_info.variant.id for line_info in lines]
        variants = list(
            product_models.ProductVariant.objects.filter(
                id__in=variant_ids
            ).prefetch_related("product__product_type")
        )  # FIXME: is this prefetch needed?
        quantities = [line_info.line.quantity for line_info in lines]
        check_lines_quantity(
            variants,
            quantities,
            country,
            channel_slug,
            info.context.site.settings.limit_quantity_per_checkout,
            # Set replace=True to avoid existing_lines and quantities from
            # being counted twice by the check_stock_quantity_bulk
            replace=True,
            existing_lines=lines,
            check_reservations=is_reservation_enabled(info.context.site.settings),
        )

    @classmethod
    def perform_mutation(
        cls, _root, info, shipping_address, checkout_id=None, token=None, id=None
    ):
        checkout = get_checkout(
            cls,
            info,
            checkout_id=checkout_id,
            token=token,
            id=id,
            error_class=CheckoutErrorCode,
            qs=models.Checkout.objects.prefetch_related(
                "lines__variant__product__product_type"
            ),
        )

        lines, _ = fetch_checkout_lines(checkout)
        if not is_shipping_required(lines):
            raise ValidationError(
                {
                    "shipping_address": ValidationError(
                        ERROR_DOES_NOT_SHIP,
                        code=CheckoutErrorCode.SHIPPING_NOT_REQUIRED,
                    )
                }
            )

        shipping_address = cls.validate_address(
            shipping_address,
            address_type=AddressType.SHIPPING,
            instance=checkout.shipping_address,
            info=info,
        )

        discounts = info.context.discounts
        manager = info.context.plugins
        shipping_channel_listings = checkout.channel.shipping_method_listings.all()
        checkout_info = fetch_checkout_info(
            checkout, lines, discounts, manager, shipping_channel_listings
        )

        country = shipping_address.country.code
        checkout.set_country(country, commit=True)

        # Resolve and process the lines, validating variants quantities
        if lines:
            cls.process_checkout_lines(info, lines, country, checkout_info.channel.slug)

        update_checkout_shipping_method_if_invalid(checkout_info, lines)

        with traced_atomic_transaction():
            shipping_address.save()
            change_shipping_address_in_checkout(
                checkout_info,
                shipping_address,
                lines,
                discounts,
                manager,
                shipping_channel_listings,
            )
        recalculate_checkout_discount(manager, checkout_info, lines, discounts)

        manager.checkout_updated(checkout)
        return CheckoutShippingAddressUpdate(checkout=checkout)
