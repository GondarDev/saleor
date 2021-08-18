from datetime import date, timedelta
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from ...core import TimePeriodType
from ...core.utils.promo_code import InvalidPromoCode
from ...plugins.manager import get_plugins_manager
from ...site import GiftCardSettingsExpiryType
from .. import GiftCardEvents
from ..models import GiftCardEvent
from ..utils import (
    add_gift_card_code_to_checkout,
    calculate_expiry_date,
    gift_cards_create,
    remove_gift_card_code_from_checkout,
)


def test_add_gift_card_code_to_checkout(checkout, gift_card):
    # given
    assert checkout.gift_cards.count() == 0

    # when
    add_gift_card_code_to_checkout(
        checkout, "test@example.com", gift_card.code, gift_card.currency
    )

    # then
    assert checkout.gift_cards.count() == 1


def test_add_gift_card_code_to_checkout_inactive_card(checkout, gift_card):
    # given
    gift_card.is_active = False
    gift_card.save(update_fields=["is_active"])

    assert checkout.gift_cards.count() == 0

    # when
    # then
    with pytest.raises(InvalidPromoCode):
        add_gift_card_code_to_checkout(
            checkout, "test@example.com", gift_card.code, gift_card.currency
        )


def test_add_gift_card_code_to_checkout_expired_card(checkout, gift_card):
    # given
    gift_card.expiry_date = date.today() - timedelta(days=10)
    gift_card.save(update_fields=["expiry_date"])

    assert checkout.gift_cards.count() == 0

    # when
    # then
    with pytest.raises(InvalidPromoCode):
        add_gift_card_code_to_checkout(
            checkout, "test@example.com", gift_card.code, gift_card.currency
        )


def test_add_gift_card_code_to_checkout_invalid_currency(checkout, gift_card):
    # given
    currency = "EUR"

    assert gift_card.currency != currency
    assert checkout.gift_cards.count() == 0

    # when
    # then
    with pytest.raises(InvalidPromoCode):
        add_gift_card_code_to_checkout(
            checkout, "test@example.com", gift_card.code, currency
        )


def test_add_gift_card_code_to_checkout_used_gift_card(checkout, gift_card_used):
    # given
    assert gift_card_used.used_by_email
    assert checkout.gift_cards.count() == 0

    # when
    add_gift_card_code_to_checkout(
        checkout,
        gift_card_used.used_by_email,
        gift_card_used.code,
        gift_card_used.currency,
    )

    # then
    assert checkout.gift_cards.count() == 1


def test_add_gift_card_code_to_checkout_used_gift_card_invalid_user(
    checkout, gift_card_used
):
    # given
    email = "new_user@example.com"
    assert gift_card_used.used_by_email
    assert gift_card_used.used_by_email != email
    assert checkout.gift_cards.count() == 0

    # when
    # then
    with pytest.raises(InvalidPromoCode):
        add_gift_card_code_to_checkout(
            checkout, email, gift_card_used.code, gift_card_used.currency
        )


def test_remove_gift_card_code_from_checkout(checkout, gift_card):
    # given
    checkout.gift_cards.add(gift_card)
    assert checkout.gift_cards.count() == 1

    # when
    remove_gift_card_code_from_checkout(checkout, gift_card.code)

    # then
    assert checkout.gift_cards.count() == 0


def test_remove_gift_card_code_from_checkout_no_checkout_gift_cards(
    checkout, gift_card
):
    # given
    assert checkout.gift_cards.count() == 0

    # when
    remove_gift_card_code_from_checkout(checkout, gift_card.code)

    # then
    assert checkout.gift_cards.count() == 0


@pytest.mark.parametrize(
    "period_type, period", [("years", 5), ("weeks", 1), ("months", 13), ("days", 100)]
)
def test_calculate_expiry_settings(period_type, period, site_settings):
    # given
    site_settings.gift_card_expiry_type = GiftCardSettingsExpiryType.EXPIRY_PERIOD
    site_settings.gift_card_expiry_period_type = period_type.rstrip("s")
    site_settings.gift_card_expiry_period = period
    site_settings.save(
        update_fields=[
            "gift_card_expiry_type",
            "gift_card_expiry_period_type",
            "gift_card_expiry_period",
        ]
    )

    # when
    expiry_date = calculate_expiry_date(site_settings)

    # then
    assert expiry_date == timezone.now().date() + relativedelta(**{period_type: period})


def test_calculate_expiry_settings_for_never_expire_settings(site_settings):
    # given
    site_settings.gift_card_expiry_type = GiftCardSettingsExpiryType.NEVER_EXPIRE

    # when
    expiry_date = calculate_expiry_date(site_settings)

    # then
    assert expiry_date is None


@patch("saleor.giftcard.utils.send_gift_card_notification")
def test_gift_cards_create(
    send_notification_mock,
    order,
    gift_card_shippable_order_line,
    gift_card_non_shippable_order_line,
    site_settings,
    staff_user,
):
    # given
    manager = get_plugins_manager()
    order_lines = [gift_card_shippable_order_line, gift_card_non_shippable_order_line]
    quantities = {
        gift_card_shippable_order_line.pk: 1,
        gift_card_non_shippable_order_line.pk: 1,
    }
    user_email = order.user_email

    # when
    gift_cards = gift_cards_create(
        order, order_lines, quantities, site_settings, staff_user, None, manager
    )

    # then
    assert len(gift_cards) == len(order_lines)

    shippable_gift_card = gift_cards[0]
    shippable_price = gift_card_shippable_order_line.unit_price_gross
    assert shippable_gift_card.initial_balance == shippable_price
    assert shippable_gift_card.current_balance == shippable_price
    assert shippable_gift_card.created_by == order.user
    assert shippable_gift_card.created_by_email == user_email
    assert shippable_gift_card.expiry_date is None

    bought_event_for_shippable_card = GiftCardEvent.objects.get(
        gift_card=shippable_gift_card
    )
    assert bought_event_for_shippable_card.user == staff_user
    assert bought_event_for_shippable_card.app is None
    assert bought_event_for_shippable_card.type == GiftCardEvents.BOUGHT
    assert bought_event_for_shippable_card.parameters == {
        "order_id": order.id,
        "expiry_date": None,
    }

    non_shippable_gift_card = gift_cards[1]
    non_shippable_price = gift_card_non_shippable_order_line.total_price_gross
    assert non_shippable_gift_card.initial_balance == non_shippable_price
    assert non_shippable_gift_card.current_balance == non_shippable_price
    assert non_shippable_gift_card.created_by == order.user
    assert non_shippable_gift_card.created_by_email == user_email
    assert non_shippable_gift_card.expiry_date is None

    sent_to_customer_event = GiftCardEvent.objects.get(
        gift_card=non_shippable_gift_card, type=GiftCardEvents.SENT_TO_CUSTOMER
    )
    assert sent_to_customer_event.user == staff_user
    assert sent_to_customer_event.app is None
    assert sent_to_customer_event.parameters == {"email": user_email}

    shippable_event = GiftCardEvent.objects.get(
        gift_card=non_shippable_gift_card, type=GiftCardEvents.BOUGHT
    )
    assert shippable_event.user == staff_user
    assert shippable_event.app is None
    assert shippable_event.parameters == {"order_id": order.id, "expiry_date": None}

    send_notification_mock.assert_called_once_with(
        staff_user, None, user_email, non_shippable_gift_card, manager
    )


@patch("saleor.giftcard.utils.send_gift_card_notification")
def test_gift_cards_create_expiry_date_set(
    send_notification_mock,
    order,
    gift_card_shippable_order_line,
    gift_card_non_shippable_order_line,
    site_settings,
    staff_user,
):
    # given
    manager = get_plugins_manager()
    site_settings.gift_card_expiry_type = GiftCardSettingsExpiryType.EXPIRY_PERIOD
    site_settings.gift_card_expiry_period_type = TimePeriodType.WEEK
    site_settings.gift_card_expiry_period = 20
    site_settings.save(
        update_fields=[
            "gift_card_expiry_type",
            "gift_card_expiry_period_type",
            "gift_card_expiry_period",
        ]
    )
    order_lines = [gift_card_non_shippable_order_line]
    quantities = {
        gift_card_shippable_order_line.pk: 1,
        gift_card_non_shippable_order_line.pk: 1,
    }
    user_email = order.user_email

    # when
    gift_cards = gift_cards_create(
        order, order_lines, quantities, site_settings, staff_user, None, manager
    )

    # then
    assert len(gift_cards) == len(order_lines)

    non_shippable_gift_card = gift_cards[0]
    non_shippable_price = gift_card_non_shippable_order_line.total_price_gross
    assert non_shippable_gift_card.initial_balance == non_shippable_price
    assert non_shippable_gift_card.current_balance == non_shippable_price
    assert non_shippable_gift_card.created_by == order.user
    assert non_shippable_gift_card.created_by_email == user_email
    assert non_shippable_gift_card.expiry_date

    sent_to_customer_event = GiftCardEvent.objects.get(
        gift_card=non_shippable_gift_card, type=GiftCardEvents.SENT_TO_CUSTOMER
    )
    assert sent_to_customer_event.user == staff_user
    assert sent_to_customer_event.app is None
    assert sent_to_customer_event.parameters == {"email": user_email}

    shippable_event = GiftCardEvent.objects.get(
        gift_card=non_shippable_gift_card, type=GiftCardEvents.BOUGHT
    )
    assert shippable_event.user == staff_user
    assert shippable_event.app is None
    assert shippable_event.parameters == {
        "order_id": order.id,
        "expiry_date": non_shippable_gift_card.expiry_date.isoformat(),
    }

    send_notification_mock.assert_called_once_with(
        staff_user, None, user_email, non_shippable_gift_card, manager
    )


@patch("saleor.giftcard.utils.send_gift_card_notification")
def test_gift_cards_create_multiple_quantity(
    send_notification_mock,
    order,
    gift_card_non_shippable_order_line,
    site_settings,
    staff_user,
):
    # given
    manager = get_plugins_manager()
    quantity = 3
    gift_card_non_shippable_order_line.quantity = quantity
    gift_card_non_shippable_order_line.save(update_fields=["quantity"])
    order_lines = [gift_card_non_shippable_order_line]
    quantities = {gift_card_non_shippable_order_line.pk: quantity}

    # when
    gift_cards = gift_cards_create(
        order, order_lines, quantities, site_settings, staff_user, None, manager
    )

    # then
    assert len(gift_cards) == quantity
    price = gift_card_non_shippable_order_line.unit_price_gross
    for gift_card in gift_cards:
        assert gift_card.initial_balance == price
        assert gift_card.current_balance == price

    assert GiftCardEvent.objects.filter(type=GiftCardEvents.BOUGHT).count() == quantity
    assert (
        GiftCardEvent.objects.filter(type=GiftCardEvents.SENT_TO_CUSTOMER).count()
        == quantity
    )
    assert send_notification_mock.call_count == 3
