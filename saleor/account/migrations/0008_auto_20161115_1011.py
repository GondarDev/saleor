# Generated by Django 1.10.1 on 2016-11-15 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("account", "0007_auto_20161115_0940")]

    replaces = [("userprofile", "0008_auto_20161115_1011")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="active"),
        )
    ]
