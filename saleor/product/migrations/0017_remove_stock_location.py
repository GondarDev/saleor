# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-07 14:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("product", "0016_auto_20161207_0843")]

    operations = [migrations.RemoveField(model_name="stock", name="location")]
