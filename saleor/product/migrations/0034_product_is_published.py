# Generated by Django 1.10.6 on 2017-04-05 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("product", "0033_auto_20170227_0757")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_published",
            field=models.BooleanField(default=True, verbose_name="is published"),
        )
    ]
