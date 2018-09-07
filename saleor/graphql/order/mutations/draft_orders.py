import graphene
from django.utils.translation import pgettext_lazy
from graphene.types import InputObjectType
from graphql_jwt.decorators import permission_required

from ....account.models import Address
from ....core.exceptions import InsufficientStock
from ....core.utils.taxes import ZERO_TAXED_MONEY
from ....order import OrderEvents, OrderStatus, models
from ....order.utils import add_variant_to_order, recalculate_order
from ...account.types import AddressInput
from ...core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from ...core.types.common import Decimal, Error
from ...product.types import ProductVariant
from ..types import Order


class OrderLineInput(graphene.InputObjectType):
    variant_id = graphene.ID(
        description='Product variant ID.', name='variantId')
    quantity = graphene.Int(
        description='Number of variant items ordered.')


class DraftOrderInput(InputObjectType):
    billing_address = AddressInput(
        description='Billing address of the customer.')
    user = graphene.ID(
        descripton='Customer associated with the draft order.', name='user')
    user_email = graphene.String(description='Email address of the customer.')
    discount = Decimal(description='Discount amount for the order.')
    lines = graphene.List(
        OrderLineInput,
        description="""Variant line input consisting of variant ID
        and quantity of products.""")
    shipping_address = AddressInput(
        description='Shipping address of the customer.')
    shipping_method = graphene.ID(
        description='ID of a selected shipping method.', name='shippingMethod')
    voucher = graphene.ID(
        description='ID of the voucher associated with the order',
        name='voucher')


def check_lines_quantity(variants, quantities):
    """Check if stock is sufficient for each line in the list of dicts.

    Return list of errors.
    """
    errors = []

    for variant, quantity in zip(variants, quantities):
        try:
            variant.check_quantity(quantity)
        except InsufficientStock as e:
            message = pgettext_lazy(
                'Add line mutation error',
                'Could not add item. Only %(remaining)d remaining in stock.' %
                {'remaining': e.item.quantity_available})
            errors.append((variant.name, message))
    return errors


class DraftOrderCreate(ModelMutation):
    class Arguments:
        input = DraftOrderInput(
            required=True,
            description='Fields required to create an order.')

    class Meta:
        description = 'Creates a new draft order.'
        model = models.Order

    @classmethod
    def clean_input(cls, info, instance, input, errors):
        shipping_address = input.pop('shipping_address', None)
        billing_address = input.pop('billing_address', None)
        cleaned_input = super().clean_input(info, instance, input, errors)
        lines = input.pop('lines', None)
        if lines:
            variant_ids = [line.get('variant_id') for line in lines]
            variants = cls.get_nodes_or_error(
                ids=variant_ids, only_type=ProductVariant, errors=errors,
                field='variants')
            quantities = [line.get('quantity') for line in lines]
            line_errors = check_lines_quantity(variants, quantities)
            if line_errors:
                for err in line_errors:
                    cls.add_error(errors, field=err[0], message=err[1])
            else:
                cleaned_input['variants'] = variants
                cleaned_input['quantities'] = quantities
        cleaned_input['status'] = OrderStatus.DRAFT
        display_gross_prices = info.context.site.settings.display_gross_prices
        cleaned_input['display_gross_prices'] = display_gross_prices

        # Set up default addresses if possible
        user = cleaned_input.get('user')
        if user and not shipping_address:
            cleaned_input[
                'shipping_address'] = user.default_shipping_address
        if user and not billing_address:
            cleaned_input[
                'billing_address'] = user.default_billing_address

        if shipping_address:
            shipping_address = Address(**shipping_address)
            cls.clean_instance(shipping_address, errors)
            cleaned_input['shipping_address'] = shipping_address
        if billing_address:
            billing_address = Address(**billing_address)
            cls.clean_instance(billing_address, errors)
            cleaned_input['billing_address'] = billing_address

        return cleaned_input

    @classmethod
    def user_is_allowed(cls, user, input):
        return user.has_perm('order.manage_orders')

    @classmethod
    def save(cls, info, instance, cleaned_input):
        shipping_address = cleaned_input.get('shipping_address')
        if shipping_address:
            shipping_address.save()
            instance.shipping_address = shipping_address
        billing_address = cleaned_input.get('billing_address')
        if billing_address:
            billing_address.save()
            instance.billing_address = billing_address
        super().save(info, instance, cleaned_input)
        instance.save(update_fields=['billing_address', 'shipping_address'])
        variants = cleaned_input.get('variants')
        quantities = cleaned_input.get('quantities')
        if variants and quantities:
            for variant, quantity in zip(variants, quantities):
                add_variant_to_order(instance, variant, quantity)
        recalculate_order(instance)


class DraftOrderUpdate(DraftOrderCreate):
    class Arguments:
        id = graphene.ID(
            required=True, description='ID of an order to update.')
        input = DraftOrderInput(
            required=True,
            description='Fields required to update an order.')

    class Meta:
        description = 'Updates a draft order.'
        model = models.Order


class DraftOrderDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(
            required=True, description='ID of a draft order to delete.')

    class Meta:
        description = 'Deletes a draft order.'
        model = models.Order

    @classmethod
    def user_is_allowed(cls, user, input):
        return user.has_perm('order.manage_orders')


def check_for_draft_order_errors(order, errors):
    """Return a list of errors associated with the order.

    Checks, if given order has a proper shipping address and method
    set up and return list of errors if not.
    """
    if order.get_total_quantity() == 0:
        errors.append(
            Error(
                field='lines',
                message='Could not create order without any products.'))
    if order.is_shipping_required():
        method = order.shipping_method
        shipping_address = order.shipping_address
        shipping_not_valid = (
            method and shipping_address and
            shipping_address.country.code not in method.shipping_zone.countries)  # noqa
        if shipping_not_valid:
            errors.append(
                Error(
                    field='shipping',
                    message='Shipping method is not valid for chosen shipping '
                            'address'))
    return errors


class DraftOrderComplete(BaseMutation):
    class Arguments:
        id = graphene.ID(
            required=True,
            description='ID of the order that will be completed.')

    class Meta:
        description = 'Completes creating an order.'

    order = graphene.Field(
        Order, description='Completed order.')

    @classmethod
    @permission_required('order.manage_orders')
    def mutate(cls, root, info, id):
        errors = []
        order = cls.get_node_or_error(info, id, errors, 'id', Order)
        errors = check_for_draft_order_errors(order, errors)
        if errors:
            return cls(errors=errors)

        order.status = OrderStatus.UNFULFILLED
        if order.user:
            order.user_email = order.user.email
        if not order.is_shipping_required():
            order.shipping_method_name = None
            order.shipping_price = ZERO_TAXED_MONEY
            if order.shipping_address:
                order.shipping_address.delete()
        order.save()
        order.history.create(
            event=OrderEvents.ORDER_DRAFT_PLACED,
            change_author=info.context.user)
        return DraftOrderComplete(order=order)
