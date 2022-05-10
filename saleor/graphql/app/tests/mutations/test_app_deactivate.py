from unittest import mock

import graphene
from django.utils.functional import SimpleLazyObject

from .....app.models import App
from .....webhook.event_types import WebhookEventAsyncType
from ....tests.utils import assert_no_permission, get_graphql_content

APP_DEACTIVATE_MUTATION = """
    mutation AppDeactivate($id: ID!){
      appDeactivate(id:$id){
        app{
          id
          isActive
        }
        errors{
          field
          message
          code
        }
      }
    }
"""


def test_deactivate_app(app, staff_api_client, permission_manage_apps):
    # given
    app.is_active = True
    app.save()
    query = APP_DEACTIVATE_MUTATION
    id = graphene.Node.to_global_id("App", app.id)
    variables = {
        "id": id,
    }

    # when
    response = staff_api_client.post_graphql(
        query, variables=variables, permissions=(permission_manage_apps,)
    )

    # then
    get_graphql_content(response)

    app.refresh_from_db()
    assert not app.is_active


@mock.patch("saleor.plugins.webhook.plugin.get_webhooks_for_event")
@mock.patch("saleor.plugins.webhook.plugin.trigger_webhooks_async")
def test_deactivate_app_trigger_webhook(
    mocked_webhook_trigger,
    mocked_get_webhooks_for_event,
    any_webhook,
    app,
    staff_api_client,
    permission_manage_apps,
    settings,
):
    # given
    mocked_get_webhooks_for_event.return_value = [any_webhook]
    settings.PLUGINS = ["saleor.plugins.webhook.plugin.WebhookPlugin"]

    app.is_active = True
    app.save()

    variables = {
        "id": graphene.Node.to_global_id("App", app.id),
    }

    # when
    staff_api_client.post_graphql(
        APP_DEACTIVATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_apps,),
    )
    app.refresh_from_db()

    # then
    assert not app.is_active
    mocked_webhook_trigger.assert_called_once_with(
        {
            "id": variables["id"],
            "is_active": app.is_active,
            "name": app.name,
        },
        WebhookEventAsyncType.APP_STATUS_CHANGED,
        [any_webhook],
        app,
        SimpleLazyObject(lambda: staff_api_client.user),
    )


def test_deactivate_app_by_app(app, app_api_client, permission_manage_apps):
    # given
    app = App.objects.create(name="Sample app objects", is_active=True)
    query = APP_DEACTIVATE_MUTATION
    id = graphene.Node.to_global_id("App", app.id)
    variables = {
        "id": id,
    }
    app_api_client.app.permissions.set([permission_manage_apps])

    # when
    response = app_api_client.post_graphql(query, variables=variables)

    # then
    get_graphql_content(response)

    app.refresh_from_db()
    assert not app.is_active


def test_deactivate_app_missing_permission(
    app, staff_api_client, permission_manage_orders
):
    # given
    app.is_active = True
    app.save()
    query = APP_DEACTIVATE_MUTATION
    id = graphene.Node.to_global_id("App", app.id)
    variables = {
        "id": id,
    }

    # when
    response = staff_api_client.post_graphql(
        query, variables=variables, permissions=(permission_manage_orders,)
    )

    # then
    assert_no_permission(response)

    app.refresh_from_db()
    assert app.is_active


def test_activate_app_by_app_missing_permission(
    app, app_api_client, permission_manage_orders
):
    # given
    app = App.objects.create(name="Sample app objects", is_active=True)
    query = APP_DEACTIVATE_MUTATION
    id = graphene.Node.to_global_id("App", app.id)
    variables = {
        "id": id,
    }
    app_api_client.app.permissions.set([permission_manage_orders])

    # when
    response = app_api_client.post_graphql(query, variables=variables)

    # then
    assert_no_permission(response)

    assert app.is_active


def test_app_has_more_permission_than_user_requestor(
    app, staff_api_client, permission_manage_orders, permission_manage_apps
):
    # given
    app.permissions.add(permission_manage_orders)
    app.is_active = True
    app.save()

    query = APP_DEACTIVATE_MUTATION
    id = graphene.Node.to_global_id("App", app.id)
    variables = {
        "id": id,
    }

    # when
    response = staff_api_client.post_graphql(
        query, variables=variables, permissions=(permission_manage_apps,)
    )

    # then
    content = get_graphql_content(response)
    app_data = content["data"]["appDeactivate"]["app"]
    app_errors = content["data"]["appDeactivate"]["errors"]
    app.refresh_from_db()

    assert not app_errors
    assert not app.is_active
    assert app_data["isActive"] is False


def test_app_has_more_permission_than_app_requestor(
    app_api_client, permission_manage_orders, permission_manage_apps
):
    # given
    app = App.objects.create(name="Sample app objects", is_active=True)
    app.permissions.add(permission_manage_orders)

    query = APP_DEACTIVATE_MUTATION
    id = graphene.Node.to_global_id("App", app.id)
    variables = {
        "id": id,
    }

    # when
    response = app_api_client.post_graphql(
        query, variables=variables, permissions=(permission_manage_apps,)
    )

    # then
    content = get_graphql_content(response)
    app_data = content["data"]["appDeactivate"]["app"]
    app_errors = content["data"]["appDeactivate"]["errors"]
    app.refresh_from_db()

    assert not app_errors
    assert not app.is_active
    assert app_data["isActive"] is False
