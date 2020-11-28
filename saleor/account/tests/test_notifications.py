from unittest import mock

from freezegun import freeze_time

from ...core.notify_events import UserNotifyEvent
from ...plugins.manager import get_plugins_manager
from .. import notifications
from ..notifications import get_default_user_payload


@freeze_time("2018-05-31 12:00:01")
@mock.patch("saleor.plugins.manager.PluginsManager.notify")
def test_send_email_request_change(mocked_notify, site_settings, customer_user):
    new_email = "example@example.com"
    redirect_url = "http://localhost:8000/redirect"
    token = "token_example"

    manager = get_plugins_manager()
    notifications.send_request_user_change_email_notification(
        redirect_url, customer_user, new_email, token, manager
    )

    expected_payload = {
        "user": get_default_user_payload(customer_user),
        "recipient_email": new_email,
        "token": token,
        "redirect_url": f"{redirect_url}?token={token}",
        "old_email": customer_user.email,
        "new_email": new_email,
        "site_name": "mirumee.com",
        "domain": "mirumee.com",
    }

    mocked_notify.assert_called_once_with(
        UserNotifyEvent.ACCOUNT_CHANGE_EMAIL_REQUEST, payload=expected_payload
    )


@mock.patch("saleor.plugins.manager.PluginsManager.notify")
def test_send_email_changed_notification(mocked_notify, site_settings, customer_user):
    old_email = "example@example.com"

    notifications.send_user_change_email_notification(
        old_email, customer_user, get_plugins_manager()
    )

    expected_payload = {
        "user": get_default_user_payload(customer_user),
        "recipient_email": old_email,
        "site_name": "mirumee.com",
        "domain": "mirumee.com",
    }

    mocked_notify.assert_called_once_with(
        UserNotifyEvent.ACCOUNT_CHANGE_EMAIL_CONFIRM, payload=expected_payload
    )
