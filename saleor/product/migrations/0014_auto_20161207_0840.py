# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-07 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("product", "0013_auto_20161207_0555")]

    operations = [
        migrations.AlterField(
            model_name="stock",
            name="location",
            field=models.CharField(max_length=100, null=True, verbose_name="location"),
        )
    ]
