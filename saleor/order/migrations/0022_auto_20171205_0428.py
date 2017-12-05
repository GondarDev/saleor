# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-05 10:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0021_auto_20171129_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='delivery_group',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='order.DeliveryGroup', verbose_name='delivery group'),
        ),
    ]
