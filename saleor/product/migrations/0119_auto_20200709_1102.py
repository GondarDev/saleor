# Generated by Django 3.0.6 on 2020-07-09 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0118_populate_product_variant_price"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="attributeproduct",
            options={"ordering": ("sort_order", "pk")},
        ),
        migrations.AlterModelOptions(
            name="attributevalue",
            options={"ordering": ("sort_order", "pk")},
        ),
        migrations.AlterModelOptions(
            name="attributevariant",
            options={"ordering": ("sort_order", "pk")},
        ),
        migrations.AlterModelOptions(
            name="product",
            options={
                "ordering": ("slug",),
                "permissions": (("manage_products", "Manage products."),),
            },
        ),
        migrations.AlterModelOptions(
            name="productimage",
            options={"ordering": ("sort_order", "pk")},
        ),
    ]
