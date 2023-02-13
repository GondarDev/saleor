# Generated by Django 2.2.9 on 2020-01-14 09:30

import django_countries.fields
from django.db import migrations

import saleor.checkout.models


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0022_auto_20191219_1137"),
    ]

    operations = [
        migrations.AddField(
            model_name="checkout",
            name="country",
            field=django_countries.fields.CountryField(
                default=saleor.checkout.models.get_default_country, max_length=2
            ),
        ),
    ]
