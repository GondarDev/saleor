# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-15 10:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0047_auto_20180117_0359'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductClass',
            new_name='ProductType',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='product_class',
            new_name='product_type',
        ),
        migrations.AlterField(
            model_name='producttype',
            name='product_attributes',
            field=models.ManyToManyField(blank=True, related_name='product_types', to='product.ProductAttribute'),
        ),
        migrations.AlterField(
            model_name='producttype',
            name='variant_attributes',
            field=models.ManyToManyField(blank=True, related_name='product_variant_types', to='product.ProductAttribute'),
        ),
    ]
