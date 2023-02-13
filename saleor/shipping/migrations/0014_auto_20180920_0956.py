# Generated by Django 2.0.8 on 2018-09-20 14:56

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shipping", "0013_auto_20180822_0721")]

    operations = [
        migrations.AddField(
            model_name="shippingzone",
            name="default",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="shippingzone",
            name="countries",
            field=django_countries.fields.CountryField(
                blank=True, default=[], max_length=749, multiple=True
            ),
        ),
    ]
