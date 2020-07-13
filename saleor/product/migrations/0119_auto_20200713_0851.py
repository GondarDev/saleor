# Generated by Django 3.0.6 on 2020-07-13 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0118_populate_product_variant_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attribute",
            name="slug",
            field=models.SlugField(allow_unicode=True, max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name="attributevalue",
            name="slug",
            field=models.SlugField(allow_unicode=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(allow_unicode=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="collection",
            name="slug",
            field=models.SlugField(allow_unicode=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="slug",
            field=models.SlugField(allow_unicode=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="slug",
            field=models.SlugField(allow_unicode=True, max_length=255, unique=True),
        ),
    ]
