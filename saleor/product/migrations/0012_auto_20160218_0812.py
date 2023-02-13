# Generated by Django 1.9.1 on 2016-02-18 14:12
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("product", "0011_stock_quantity_allocated")]

    operations = [
        migrations.CreateModel(
            name="VariantImage",
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
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variant_images",
                        to="product.ProductImage",
                    ),
                ),
                (
                    "variant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variant_images",
                        to="product.ProductVariant",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="productvariant",
            name="images",
            field=models.ManyToManyField(
                through="product.VariantImage", to="product.ProductImage"
            ),
        ),
    ]
