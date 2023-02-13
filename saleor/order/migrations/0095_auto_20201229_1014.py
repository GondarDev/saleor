# Generated by Django 3.1.3 on 2020-12-29 10:14

from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0094_auto_20201221_1128"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderline",
            name="tax_rate",
            field=models.DecimalField(
                decimal_places=4, default=Decimal("0.0"), max_digits=5
            ),
        ),
    ]
