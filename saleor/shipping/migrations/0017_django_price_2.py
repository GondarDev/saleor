# Generated by Django 2.2.4 on 2019-08-14 09:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("shipping", "0016_shippingmethod_meta")]

    operations = [
        migrations.RenameField(
            model_name="shippingmethod",
            old_name="maximum_order_price",
            new_name="maximum_order_price_amount",
        ),
        migrations.RenameField(
            model_name="shippingmethod",
            old_name="minimum_order_price",
            new_name="minimum_order_price_amount",
        ),
        migrations.RenameField(
            model_name="shippingmethod", old_name="price", new_name="price_amount"
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="currency",
            field=models.CharField(default=settings.DEFAULT_CURRENCY, max_length=10),
        ),
    ]
