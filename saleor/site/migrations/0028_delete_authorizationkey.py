# Generated by Django 3.1.3 on 2020-12-17 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("site", "0027_sitesettings_automatically_confirm_all_new_orders"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AuthorizationKey",
        ),
    ]
