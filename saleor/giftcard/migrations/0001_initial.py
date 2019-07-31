# Generated by Django 2.2.1 on 2019-06-07 09:43

import datetime

import django.db.models.deletion
import django_prices.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="GiftCard",
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
                ("code", models.CharField(db_index=True, max_length=16, unique=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("start_date", models.DateField(default=datetime.date.today)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("last_used_on", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "initial_balance",
                    django_prices.models.MoneyField(
                        currency="USD", decimal_places=2, max_digits=12
                    ),
                ),
                (
                    "current_balance",
                    django_prices.models.MoneyField(
                        currency="USD", decimal_places=2, max_digits=12
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="gift_cards",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"permissions": (("manage_gift_card", "Manage gift cards."),)},
        )
    ]
