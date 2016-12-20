from __future__ import unicode_literals
from functools import wraps

from django.utils.timezone import now

from .core import set_cart_cookie
from .models import Cart


def find_and_assign_anonymous_cart(request, queryset=Cart.objects.all()):
    """Assign cart from cookie to request user
    :type request: django.http.HttpRequest
    """
    token = request.get_signed_cookie(Cart.COOKIE_NAME, default=None)
    if not token:
        return
    cart = get_anonymous_cart_from_token(token=token, cart_queryset=queryset)
    if cart is None:
        return
    cart.change_user(request.user)
    carts_to_close = Cart.objects.open().filter(user=request.user)
    carts_to_close = carts_to_close.exclude(token=token)
    carts_to_close.update(status=Cart.CANCELED, last_status_change=now())


def get_or_create_anonymous_cart_from_token(token,
                                            cart_queryset=Cart.objects.all()):
    """Returns open anonymous cart with given token or creates new.
    :type cart_queryset: saleor.cart.models.CartQueryset
    :type token: string
    :rtype: Cart
    """

    return cart_queryset.open().filter(token=token, user=None).get_or_create(
        defaults={'user': None})[0]


def get_or_create_user_cart(user, cart_queryset=Cart.objects.all()):
    """Returns open cart for given user or creates one.
    :type cart_queryset: saleor.cart.models.CartQueryset
    :type user: User
    :rtype: Cart
    """
    return cart_queryset.open().get_or_create(user=user)[0]


def get_anonymous_cart_from_token(token, cart_queryset=Cart.objects.all()):
    """Returns open anonymous cart with given token or None if not found.
    :rtype: Cart | None
    """
    return cart_queryset.open().filter(token=token, user=None).first()


def get_user_cart(user, cart_queryset=Cart.objects.all()):
    """Returns open cart for given user or None if not found.
    :type cart_queryset: saleor.cart.models.CartQueryset
    :type user: User
    :rtype: Cart | None
    """
    return cart_queryset.open().filter(user=user).first()


def get_or_create_cart_from_request(request, cart_queryset=Cart.objects.all()):
    """Get cart from database or create new Cart if not found
    :type cart_queryset: saleor.cart.models.CartQueryset
    :type request: django.http.HttpRequest
    :rtype: Cart
    """
    if request.user.is_authenticated():
        return get_or_create_user_cart(request.user, cart_queryset)
    else:
        token = request.get_signed_cookie(Cart.COOKIE_NAME, default=None)
        return get_or_create_anonymous_cart_from_token(token, cart_queryset)


def get_cart_from_request(request, cart_queryset=Cart.objects.all()):
    """Get cart from database or return unsaved Cart
    :type cart_queryset: saleor.cart.models.CartQueryset
    :type request: django.http.HttpRequest
    :rtype: Cart
    """
    if request.user.is_authenticated():
        cart = get_user_cart(request.user, cart_queryset)
        user = request.user
    else:
        token = request.get_signed_cookie(Cart.COOKIE_NAME, default=None)
        cart = get_anonymous_cart_from_token(token, cart_queryset)
        user = None
    if cart is not None:
        return cart
    else:
        return Cart(user=user)


def get_or_create_db_cart(cart_queryset=Cart.objects.all()):
    """Get cart or create if necessary. Example: adding items to cart
    :type cart_queryset: saleor.cart.models.CartQueryset
    """
    def get_cart(view):
        @wraps(view)
        def func(request, *args, **kwargs):
            cart = get_or_create_cart_from_request(request, cart_queryset)
            response = view(request, cart, *args, **kwargs)
            if not request.user.is_authenticated():
                set_cart_cookie(cart, response)
            return response
        return func
    return get_cart


def get_or_empty_db_cart(cart_queryset=Cart.objects.all()):
    """Get cart if exists. Prevents creating empty carts in views which not
    need it
    :type cart_queryset: saleor.cart.models.CartQueryset
    """
    def get_cart(view):
        @wraps(view)
        def func(request, *args, **kwargs):
            cart = get_cart_from_request(request, cart_queryset)
            return view(request, cart, *args, **kwargs)
        return func
    return get_cart
