# Generated by Django 3.2.16 on 2022-11-29 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0177_product_tax_class_producttype_tax_class"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="external_reference",
            field=models.CharField(
                blank=True, db_index=True, max_length=250, null=True, unique=True
            ),
        ),
    ]
