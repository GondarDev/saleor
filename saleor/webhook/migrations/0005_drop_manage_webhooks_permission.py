# Generated by Django 3.0.5 on 2020-04-24 12:52

from django.db import migrations


def change_webhook_permission_to_app_permission(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    App = apps.get_model("app", "App")

    manage_webhooks = Permission.objects.filter(
        codename="manage_webhooks", content_type__app_label="webhook"
    ).first()
    manage_apps = Permission.objects.filter(
        codename="manage_apps", content_type__app_label="app"
    ).first()
    apps = App.objects.filter(
        permissions__content_type__app_label="webhook",
        permissions__codename="manage_webhooks",
    )

    groups = Group.objects.filter(
        permissions__content_type__app_label="webhook",
        permissions__codename="manage_webhooks",
    )

    if not manage_apps:
        if manage_webhooks:
            manage_webhooks.delete()
        return

    for group in groups:
        group.permissions.remove(manage_webhooks)
        group.permissions.add(manage_apps)

    for app in apps:
        app.permissions.remove(manage_webhooks)
        app.permissions.add(manage_apps)

    if manage_webhooks:
        manage_webhooks.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("webhook", "0004_mount_app"),
    ]

    operations = [
        migrations.RunPython(change_webhook_permission_to_app_permission),
        migrations.AlterModelOptions(name="webhook", options={},),
    ]
