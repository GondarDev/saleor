# Generated by Django 2.2.7 on 2019-12-19 09:38

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("checkout", "0021_django_price_2")]

    operations = [
        migrations.AddField(
            model_name="checkout",
            name="country",
            field=django_countries.fields.CountryField(default="US", max_length=2),
        )
    ]
