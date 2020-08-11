# Generated by Django 3.1 on 2020-08-10 14:15

from django.db import migrations, models

import saleor.core.utils.json_serializer


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0003_auto_20200713_1311"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=saleor.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=saleor.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="invoiceevent",
            name="parameters",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=saleor.core.utils.json_serializer.CustomJsonEncoder,
            ),
        ),
    ]
