# Generated by Django 1.11.5 on 2017-11-09 15:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("shipping", "0005_auto_20170906_0556")]

    operations = [
        migrations.AlterModelOptions(
            name="shippingmethod",
            options={
                "permissions": (
                    ("view_shipping", "Can view shipping method"),
                    ("edit_shipping", "Can edit shipping method"),
                ),
                "verbose_name": "shipping method",
                "verbose_name_plural": "shipping methods",
            },
        )
    ]
