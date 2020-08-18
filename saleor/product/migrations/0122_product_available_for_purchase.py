# Generated by Django 3.1 on 2020-08-18 09:19
import datetime

from django.db import migrations, models


def set_all_published_products_as_available_for_purchase(apps, schema_editor):
    Product = apps.get_model("product", "Product")
    Product.objects.filter(is_published=True).update(
        available_for_purchase=datetime.datetime.today()
    )


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0121_auto_20200810_1415"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="available_for_purchase",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(
            set_all_published_products_as_available_for_purchase,
            migrations.RunPython.noop,
        ),
    ]
