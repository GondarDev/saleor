# Generated by Django 2.0.3 on 2018-04-09 09:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("product", "0060_collection_is_published")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="charge_taxes",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="product",
            name="tax_rate",
            field=models.CharField(blank=True, default="standard", max_length=128),
        ),
        migrations.AddField(
            model_name="producttype",
            name="tax_rate",
            field=models.CharField(blank=True, default="standard", max_length=128),
        ),
    ]
