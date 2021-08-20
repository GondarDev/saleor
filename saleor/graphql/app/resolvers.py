from ...app import models
from ...core.jwt import (
    create_access_token_for_app,
    create_access_token_for_app_extension,
)
from ...core.permissions import AppPermission
from ...core.utils.validators import user_is_valid
from ..core.utils import from_global_id_or_error
from ..decorators import permission_required
from .enums import AppTypeEnum


def resolve_apps_installations(info, **_kwargs):
    return models.AppInstallation.objects.all()


def resolve_apps(info, **_kwargs):
    return models.App.objects.all()


def resolve_access_token_for_app(info, root, **_kwargs):
    if root.type != AppTypeEnum.THIRDPARTY.value:
        return None

    user = info.context.user
    if user.is_anonymous:
        return None
    return create_access_token_for_app(root, user)


def resolve_access_token_for_app_extension(info, root, **_kwargs):
    user = info.context.user
    if not user_is_valid(user):
        return None
    extension_permissions = root.permissions.all()
    user_permissions = user.effective_permissions
    if set(extension_permissions).issubset(user_permissions):
        return create_access_token_for_app_extension(
            app_extension=root, permissions=extension_permissions, user=user
        )
    return None


@permission_required(AppPermission.MANAGE_APPS)
def resolve_app(_info, id):
    if not id:
        return None
    _, id = from_global_id_or_error(id, "App")
    return models.App.objects.filter(id=id).first()


def resolve_app_extensions(_info):
    return models.AppExtension.objects.filter(app__is_active=True)
