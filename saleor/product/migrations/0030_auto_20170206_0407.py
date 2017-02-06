# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 10:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_product_is_featured'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attributechoicevalue',
            options={'verbose_name': 'attribute choices value', 'verbose_name_plural': 'attribute choices values'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'category', 'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'product', 'verbose_name_plural': 'products'},
        ),
        migrations.AlterModelOptions(
            name='productattribute',
            options={'ordering': ('name',), 'verbose_name': 'product attribute', 'verbose_name_plural': 'product attributes'},
        ),
        migrations.AlterModelOptions(
            name='productclass',
            options={'verbose_name': 'product class', 'verbose_name_plural': 'product classes'},
        ),
        migrations.AlterModelOptions(
            name='productimage',
            options={'ordering': ('order',), 'verbose_name': 'product image', 'verbose_name_plural': 'product images'},
        ),
        migrations.AlterModelOptions(
            name='productvariant',
            options={'verbose_name': 'product variant', 'verbose_name_plural': 'product variants'},
        ),
        migrations.AlterModelOptions(
            name='variantimage',
            options={'verbose_name': 'variant image', 'verbose_name_plural': 'variant images'},
        ),
        migrations.AlterField(
            model_name='product',
            name='product_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.ProductClass', verbose_name='product class'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(upload_to='products', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='order',
            field=models.PositiveIntegerField(editable=False, verbose_name='order'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='ppoi',
            field=versatileimagefield.fields.PPOIField(default='0.5x0.5', editable=False, max_length=20, verbose_name='ppoi'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='product.Product', verbose_name='product'),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='images',
            field=models.ManyToManyField(through='product.VariantImage', to='product.ProductImage', verbose_name='images'),
        ),
        migrations.AlterField(
            model_name='variantimage',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_images', to='product.ProductImage', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='variantimage',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_images', to='product.ProductVariant', verbose_name='variant'),
        ),
    ]
