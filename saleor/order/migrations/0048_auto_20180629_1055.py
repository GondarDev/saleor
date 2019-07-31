# Generated by Django 2.0.3 on 2018-06-29 15:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("order", "0047_order_line_name_length")]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="token",
            field=models.CharField(blank=True, max_length=36, unique=True),
        ),
        migrations.AlterField(
            model_name="order",
            name="voucher",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="discount.Voucher",
            ),
        ),
    ]
