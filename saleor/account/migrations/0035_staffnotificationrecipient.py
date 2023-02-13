# Generated by Django 2.2.6 on 2019-11-22 10:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("account", "0034_service_account_token")]

    operations = [
        migrations.CreateModel(
            name="StaffNotificationRecipient",
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
                (
                    "staff_email",
                    models.EmailField(
                        blank=True, max_length=254, null=True, unique=True
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff_notification",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        )
    ]
