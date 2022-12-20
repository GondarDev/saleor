# Generated by Django 3.2.15 on 2022-08-26 08:14

from django.apps import apps as registry
from django.db import migrations
from django.db.models.signals import post_migrate


def assign_permissions(apps, schema_editor):
    def on_migrations_complete(sender=None, **kwargs):
        try:
            apps = kwargs["apps"]
        except KeyError:
            # In test when we use use `@pytest.mark.django_db(transaction=True)`
            # pytest trigger additional post_migrate signal without `apps` in kwargs.
            return
        Permission = apps.get_model("permission", "Permission")
        App = apps.get_model("app", "App")
        Group = apps.get_model("account", "Group")

        manage_taxes = Permission.objects.filter(
            codename="manage_taxes", content_type__app_label="checkout"
        ).first()

        manage_checkouts = Permission.objects.filter(
            codename="manage_checkouts", content_type__app_label="checkout"
        ).first()

        apps_qs = App.objects.filter(
            permissions=manage_checkouts,
        )
        for app in apps_qs.iterator():
            app.permissions.add(manage_taxes)

        groups = Group.objects.filter(
            permissions=manage_checkouts,
        )
        for group in groups.iterator():
            group.permissions.add(manage_taxes)

    sender = registry.get_app_config("checkout")
    post_migrate.connect(on_migrations_complete, weak=False, sender=sender)


class Migration(migrations.Migration):

    dependencies = [
        ("checkout", "0053_checkout_tax_exemption"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="checkout",
            options={
                "ordering": ("-last_change", "pk"),
                "permissions": (
                    ("manage_checkouts", "Manage checkouts"),
                    ("handle_checkouts", "Handle checkouts"),
                    ("handle_taxes", "Handle taxes"),
                    ("manage_taxes", "Manage taxes"),
                ),
            },
        ),
        migrations.RunPython(assign_permissions, migrations.RunPython.noop),
    ]
