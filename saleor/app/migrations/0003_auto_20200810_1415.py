# Generated by Django 3.1 on 2020-08-10 14:15

from django.db import migrations, models

import saleor.core.utils.json_serializer


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_auto_20200702_0945"),
    ]

    operations = [
        migrations.AlterField(
            model_name="app",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=saleor.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="app",
            name="private_metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=saleor.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
    ]
