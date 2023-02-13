# Generated by Django 1.11.9 on 2018-01-17 09:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("product", "0046_product_category")]

    operations = [
        migrations.RemoveField(model_name="category", name="is_hidden"),
        migrations.RemoveField(model_name="product", name="categories"),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="product.Category",
            ),
        ),
    ]
