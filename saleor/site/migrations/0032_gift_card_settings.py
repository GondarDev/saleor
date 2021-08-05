# Generated by Django 3.2.5 on 2021-07-28 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("site", "0031_merge_20210820_1454"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="automatically_fulfill_non_shippable_gift_card",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="gift_card_expiry_period",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="gift_card_expiry_period_type",
            field=models.CharField(
                blank=True,
                choices=[("day", "day"), ("month", "Month"), ("year", "Year")],
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="gift_card_expiry_type",
            field=models.CharField(
                choices=[
                    ("never_expire", "Never expire"),
                    ("expiry_period", "Expiry period"),
                ],
                default="never_expire",
                max_length=32,
            ),
        ),
    ]
