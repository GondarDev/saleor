# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0015_auto_20170206_0407'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='language_code',
            field=models.CharField(default='en-us', max_length=55),
        ),
    ]
