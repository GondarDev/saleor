# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 14:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_auto_20170906_0556'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-last_status_change',), 'permissions': (('view_order', 'Can View Order'), ('edit_order', 'Can Edit Order')), 'verbose_name': 'Order', 'verbose_name_plural': 'Orders'},
        ),
    ]
