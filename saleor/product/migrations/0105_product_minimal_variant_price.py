# Generated by Django 2.2.1 on 2019-06-10 11:23

import django_prices.models
from django.conf import settings
from django.db import migrations


def populate_product_minimal_variant_price(apps, schema_editor):
    Product = apps.get_model("product", "Product")
    for product in Product.objects.iterator():
        # Set the "minimal variant price" to the default product's price
        # We don't calculate the "minimal variant price" here because the logic
        # depends on models' methods and we would have to copy all the code into
        # this migration. Instead we should manually run the management command:
        # - "update_all_products_minimal_variant_prices"
        product.minimal_variant_price = product.price
        product.save(update_fields=["minimal_variant_price"])


class Migration(migrations.Migration):

    dependencies = [("product", "0104_fix_invalid_attributes_map")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="minimal_variant_price",
            field=django_prices.models.MoneyField(
                currency=settings.DEFAULT_CURRENCY,
                decimal_places=2,
                max_digits=12,
                null=True,
            ),
        ),
        migrations.RunPython(
            populate_product_minimal_variant_price,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="product",
            name="minimal_variant_price",
            field=django_prices.models.MoneyField(
                currency=settings.DEFAULT_CURRENCY, decimal_places=2, max_digits=12
            ),
        ),
    ]
