# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-08 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("site", "0002_add_default_data")]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="description",
            field=models.CharField(
                blank=True, max_length=500, verbose_name="site description"
            ),
        )
    ]
