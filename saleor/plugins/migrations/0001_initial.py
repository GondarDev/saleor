# Generated by Django 2.2.3 on 2019-08-07 10:11

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models

import saleor.core.utils.json_serializer


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PluginConfiguration",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128, unique=True)),
                ("description", models.TextField(blank=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "configuration",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True,
                        default=dict,
                        encoder=saleor.core.utils.json_serializer.CustomJsonEncoder,
                        null=True,
                    ),
                ),
            ],
            options={"permissions": (("manage_plugins", "Manage plugins"),)},
        )
    ]
