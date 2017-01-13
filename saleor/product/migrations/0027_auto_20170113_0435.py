# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-13 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0026_auto_20161230_0347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productclass',
            name='has_variants',
            field=models.BooleanField(default=True, verbose_name='has variants'),
        ),
        migrations.AlterField(
            model_name='productclass',
            name='is_shipping_required',
            field=models.BooleanField(default=False, verbose_name='is shipping required'),
        ),
        migrations.AlterField(
            model_name='productclass',
            name='product_attributes',
            field=models.ManyToManyField(blank=True, related_name='products_class', to='product.ProductAttribute', verbose_name='product attributes'),
        ),
        migrations.AlterField(
            model_name='productclass',
            name='variant_attributes',
            field=models.ManyToManyField(blank=True, related_name='product_variants_class', to='product.ProductAttribute', verbose_name='variant attributes'),
        ),
        migrations.AlterField(
            model_name='stocklocation',
            name='name',
            field=models.CharField(max_length=100, verbose_name='location'),
        ),
    ]
