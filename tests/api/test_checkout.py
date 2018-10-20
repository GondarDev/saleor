import uuid
from unittest.mock import patch, ANY

import graphene
import pytest
from tests.api.utils import get_graphql_content

from saleor.checkout.models import Cart
from saleor.order.models import Order
from saleor.payment import TransactionType


def test_checkout_create(user_api_client, variant, graphql_address_data):
    """Create checkout object using GraphQL API."""
    query = """
    mutation createCheckout($checkoutInput: CheckoutCreateInput!) {
        checkoutCreate(input: $checkoutInput) {
            checkout {
                token,
                id
            }
        }
    }
    """
    variant_id = graphene.Node.to_global_id('ProductVariant', variant.id)
    test_email = 'test@example.com'
    shipping_address = graphql_address_data
    variables = {
        'checkoutInput': {
            'lines': [{
                'quantity': 1,
                'variantId': variant_id}],
            'email': test_email,
            'shippingAddress': shipping_address}}
    assert not Cart.objects.exists()
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)

    new_cart = Cart.objects.first()
    assert new_cart is not None
    checkout_data = content['data']['checkoutCreate']['checkout']
    assert checkout_data['token'] == str(new_cart.token)
    assert new_cart.lines.count() == 1
    cart_line = new_cart.lines.first()
    assert cart_line.variant == variant
    assert cart_line.quantity == 1
    assert new_cart.shipping_address is not None
    assert new_cart.shipping_address.first_name == shipping_address[
        'firstName']
    assert new_cart.shipping_address.last_name == shipping_address['lastName']
    assert new_cart.shipping_address.street_address_1 == shipping_address[
        'streetAddress1']
    assert new_cart.shipping_address.street_address_2 == shipping_address[
        'streetAddress2']
    assert new_cart.shipping_address.postal_code == shipping_address[
        'postalCode']
    assert new_cart.shipping_address.country == shipping_address['country']
    assert new_cart.shipping_address.city == shipping_address['city']


def test_checkout_lines_add(user_api_client, cart_with_item, variant):
    """
    Create checkout object using GraphQL API
    """
    cart = cart_with_item
    line = cart.lines.first()
    assert line.quantity == 3
    query = """
        mutation checkoutLinesAdd($checkoutId: ID!, $lines: [CheckoutLineInput!]!) {
            checkoutLinesAdd(checkoutId: $checkoutId, lines: $lines) {
                checkout {
                    token
                    lines {
                        quantity
                        variant {
                            id
                        }
                    }
                }
                errors {
                    field
                    message
                }
            }
        }
    """
    variant_id = graphene.Node.to_global_id('ProductVariant', variant.pk)
    checkout_id = graphene.Node.to_global_id('Checkout', cart.pk)

    variables = {
        'checkoutId': checkout_id,
        'lines': [{
            'variantId': variant_id,
            'quantity': 1}]}
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkoutLinesAdd']
    assert not data['errors']
    cart.refresh_from_db()
    line = cart.lines.latest('pk')
    assert line.variant == variant
    assert line.quantity == 1


def test_checkout_lines_update(user_api_client, cart_with_item):
    cart = cart_with_item
    assert cart.lines.count() == 1
    line = cart.lines.first()
    variant = line.variant
    assert line.quantity == 3
    query = """
        mutation checkoutLinesUpdate($checkoutId: ID!, $lines: [CheckoutLineInput!]!) {
            checkoutLinesUpdate(checkoutId: $checkoutId, lines: $lines) {
                checkout {
                    token
                    lines {
                        quantity
                        variant {
                            id
                        }
                    }
                }
                errors {
                    field
                    message
                }
            }
        }
    """
    variant_id = graphene.Node.to_global_id('ProductVariant', variant.pk)
    checkout_id = graphene.Node.to_global_id('Checkout', cart.pk)

    variables = {
        'checkoutId': checkout_id,
        'lines': [{
            'variantId': variant_id,
            'quantity': 1}]}
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)

    data = content['data']['checkoutLinesUpdate']
    assert not data['errors']
    cart.refresh_from_db()
    assert cart.lines.count() == 1
    line = cart.lines.first()
    assert line.variant == variant
    assert line.quantity == 1


def test_checkout_line_delete(user_api_client, cart_with_item):
    cart = cart_with_item
    assert cart.lines.count() == 1
    line = cart.lines.first()
    assert line.quantity == 3
    query = """
        mutation checkoutLineDelete($checkoutId: ID!, $lineId: ID!) {
            checkoutLineDelete(checkoutId: $checkoutId, lineId: $lineId) {
                checkout {
                    token
                    lines {
                        quantity
                        variant {
                            id
                        }
                    }
                }
                errors {
                    field
                    message
                }
            }
        }
    """
    checkout_id = graphene.Node.to_global_id('Checkout', cart.pk)
    line_id = graphene.Node.to_global_id('CheckoutLine', line.pk)

    variables = {'checkoutId': checkout_id, 'lineId': line_id}
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)

    data = content['data']['checkoutLineDelete']
    assert not data['errors']
    cart.refresh_from_db()
    assert cart.lines.count() == 0


def test_checkout_customer_attach(
        user_api_client, cart_with_item, customer_user):
    cart = cart_with_item
    assert cart.user is None

    query = """
        mutation checkoutCustomerAttach($checkoutId: ID!, $customerId: ID!) {
            checkoutCustomerAttach(checkoutId: $checkoutId, customerId: $customerId) {
                checkout {
                    token
                }
                errors {
                    field
                    message
                }
            }
        }
    """
    checkout_id = graphene.Node.to_global_id('Checkout', cart.pk)
    customer_id = graphene.Node.to_global_id('User', customer_user.pk)

    variables = {'checkoutId': checkout_id, 'customerId': customer_id}
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)

    data = content['data']['checkoutCustomerAttach']
    assert not data['errors']
    cart.refresh_from_db()
    assert cart.user == customer_user


def test_checkout_customer_detach(
        user_api_client, cart_with_item, customer_user):
    cart = cart_with_item
    cart.user = customer_user
    cart.save(update_fields=['user'])

    query = """
        mutation checkoutCustomerDetach($checkoutId: ID!) {
            checkoutCustomerDetach(checkoutId: $checkoutId) {
                checkout {
                    token
                }
                errors {
                    field
                    message
                }
            }
        }
    """
    checkout_id = graphene.Node.to_global_id('Checkout', cart.pk)
    variables = {
        'checkoutId': checkout_id, }
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)

    data = content['data']['checkoutCustomerDetach']
    assert not data['errors']
    cart.refresh_from_db()
    assert cart.user is None


def test_checkout_shipping_address_update(
        user_api_client, cart_with_item, graphql_address_data):
    cart = cart_with_item
    assert cart.shipping_address is None
    checkout_id = graphene.Node.to_global_id('Checkout', cart.pk)

    query = """
    mutation checkoutShippingAddressUpdate($checkoutId: ID!, $shippingAddress: AddressInput!) {
        checkoutShippingAddressUpdate(checkoutId: $checkoutId, shippingAddress: $shippingAddress) {
            checkout {
                token,
                id
            },
            errors {
                field,
                message
            }
        }
    }
    """
    shipping_address = graphql_address_data
    variables = {
        'checkoutId': checkout_id, 'shippingAddress': shipping_address}

    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkoutShippingAddressUpdate']
    assert not data['errors']
    cart.refresh_from_db()
    assert cart.shipping_address is not None
    assert cart.shipping_address.first_name == shipping_address['firstName']
    assert cart.shipping_address.last_name == shipping_address['lastName']
    assert cart.shipping_address.street_address_1 == shipping_address[
        'streetAddress1']
    assert cart.shipping_address.street_address_2 == shipping_address[
        'streetAddress2']
    assert cart.shipping_address.postal_code == shipping_address['postalCode']
    assert cart.shipping_address.country == shipping_address['country']
    assert cart.shipping_address.city == shipping_address['city']


def test_checkout_billing_address_update(
        user_api_client, cart_with_item, graphql_address_data):
    cart = cart_with_item
    assert cart.shipping_address is None
    checkout_id = graphene.Node.to_global_id('Checkout', cart.pk)

    query = """
    mutation checkoutBillingAddressUpdate($checkoutId: ID!, $billingAddress: AddressInput!) {
        checkoutBillingAddressUpdate(checkoutId: $checkoutId, billingAddress: $billingAddress) {
            checkout {
                token,
                id
            },
            errors {
                field,
                message
            }
        }
    }
    """
    billing_address = graphql_address_data

    variables = {'checkoutId': checkout_id, 'billingAddress': billing_address}

    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkoutBillingAddressUpdate']
    assert not data['errors']
    cart.refresh_from_db()
    assert cart.billing_address is not None
    assert cart.billing_address.first_name == billing_address['firstName']
    assert cart.billing_address.last_name == billing_address['lastName']
    assert cart.billing_address.street_address_1 == billing_address[
        'streetAddress1']
    assert cart.billing_address.street_address_2 == billing_address[
        'streetAddress2']
    assert cart.billing_address.postal_code == billing_address['postalCode']
    assert cart.billing_address.country == billing_address['country']
    assert cart.billing_address.city == billing_address['city']

def test_checkout_email_update(user_api_client, cart_with_item):
    cart = cart_with_item
    assert not cart.email
    checkout_id = graphene.Node.to_global_id('Checkout', cart.pk)

    query = """
    mutation checkoutEmailUpdate($checkoutId: ID!, $email: String!) {
        checkoutEmailUpdate(checkoutId: $checkoutId, email: $email) {
            checkout {
                id,
                email
            },
            errors {
                field,
                message
            }
        }
    }
    """
    email = 'test@example.com'
    variables = {'checkoutId': checkout_id, 'email': email}

    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkoutEmailUpdate']
    assert not data['errors']
    cart.refresh_from_db()
    assert cart.email == email


@pytest.mark.integration
def test_checkout_complete(
        user_api_client, cart_with_item, payment_method_dummy, address,
        shipping_method):
    checkout = cart_with_item
    checkout.shipping_address = address
    checkout.shipping_method = shipping_method
    checkout.save()
    total = checkout.get_total()
    payment_method = payment_method_dummy
    payment_method.is_active = True
    payment_method.order = None
    payment_method.total = total.gross
    payment_method.captured_amount = total.gross
    payment_method.checkout = checkout
    payment_method.save()
    payment_method.transactions.create(
        transaction_type=TransactionType.AUTH,
        is_success=True,
        gateway_response={},
        amount=total.gross.amount)
    checkout_id = graphene.Node.to_global_id('Checkout', checkout.pk)

    query = """
    mutation checkoutComplete($checkoutId: ID!) {
        checkoutComplete(checkoutId: $checkoutId) {
            order {
                id,
                token
            },
            errors {
                field,
                message
            }
        }
    }
    """
    variables = {'checkoutId': checkout_id}
    orders_count = Order.objects.count()
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkoutComplete']
    assert not data['errors']
    order_token = data['order']['token']
    assert Order.objects.count() == orders_count + 1
    order = Order.objects.first()
    assert order.token == order_token
    assert order.total.gross == total.gross
    checkout_line = checkout.lines.first()
    order_line = order.lines.first()
    assert checkout_line.quantity == order_line.quantity
    assert checkout_line.variant == order_line.variant
    assert order.shipping_address == address
    assert order.shipping_method == checkout.shipping_method
    assert order.payment_methods.exists()
    order_payment_method = order.payment_methods.first()
    assert order_payment_method == payment_method


def test_fetch_checkout_by_token(user_api_client, cart_with_item):
    query = """
    query getCheckout($token: UUID!) {
        checkout(token: $token) {
           token,
           lines {
                variant {
                    product {
                        name
                    }
                }
           }
        }
    }
    """
    variables = {'token': str(cart_with_item.token)}
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkout']
    assert data['token'] == str(cart_with_item.token)
    assert len(data['lines']) == cart_with_item.lines.count()


def test_fetch_checkout_invalid_token(user_api_client):
    query = """
        query getCheckout($token: UUID!) {
            checkout(token: $token) {
                token
            }
        }
    """
    variables = {'token': str(uuid.uuid4())}
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkout']
    assert data is None


def test_checkout_prices(user_api_client, cart_with_item):
    query = """
    query getCheckout($token: UUID!) {
        checkout(token: $token) {
           token,
           totalPrice {
                currency
                gross {
                    amount
                }
            }
            subtotalPrice {
                currency
                gross {
                    amount
                }
            }
           lines {
                totalPrice {
                    currency
                    gross {
                        amount
                    }
                }
           }
        }
    }
    """
    variables = {'token': str(cart_with_item.token)}
    response = user_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkout']
    assert data['token'] == str(cart_with_item.token)
    assert len(data['lines']) == cart_with_item.lines.count()
    assert data['totalPrice']['gross']['amount'] == (
        cart_with_item.get_total().gross.amount)
    assert data['subtotalPrice']['gross']['amount'] == (
        cart_with_item.get_subtotal().gross.amount)


@patch('saleor.graphql.checkout.mutations.clean_shipping_method')
def test_checkout_shipping_method_update(
        mock_clean_shipping, staff_api_client, shipping_method,
        cart_with_item, sale, vatlayer):
    query = """
    mutation checkoutShippingMethodUpdate($checkoutId:ID!, $shippingMethodId:ID!){
        checkoutShippingMethodUpdate(
            checkoutId:$checkoutId, shippingMethodId:$shippingMethodId) {
            errors {
                field
                message
            }
            checkout {
                id
            }
        }
    }
    """
    checkout = cart_with_item
    checkout_id = graphene.Node.to_global_id('Checkout', checkout.pk)
    method_id = graphene.Node.to_global_id(
        'ShippingMethod', shipping_method.id)
    variables = {'checkoutId': checkout_id, 'shippingMethodId': method_id}
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content['data']['checkoutShippingMethodUpdate']
    assert not data['errors']
    assert data['checkout']['id'] == checkout_id

    checkout.refresh_from_db()
    assert checkout.shipping_method == shipping_method
    mock_clean_shipping.assert_called_once_with(
        checkout, shipping_method, [], ANY, ANY)
