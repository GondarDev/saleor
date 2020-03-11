# Generated by Django 2.2.9 on 2020-03-09 11:11

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models

import saleor.core.utils.json_serializer


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0080_invoice"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="metadata",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=dict,
                encoder=saleor.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="private_metadata",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=dict,
                encoder=saleor.core.utils.json_serializer.CustomJsonEncoder,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="status",
            field=models.CharField(default="pending", max_length=32),
        ),
        migrations.AlterField(
            model_name="invoice", name="created", field=models.DateTimeField(null=True),
        ),
    ]
