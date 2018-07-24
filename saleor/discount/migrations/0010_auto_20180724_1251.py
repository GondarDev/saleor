# Generated by Django 2.0.3 on 2018-07-24 17:51

import datetime
from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0065_auto_20180719_0520'),
        ('discount', '0009_auto_20180719_0520'),
    ]

    operations = [
        migrations.RenameField(
            model_name='voucher',
            old_name='limit',
            new_name='min_amount_spent',
        ),
        migrations.RemoveField(
            model_name='voucher',
            name='apply_to',
        ),
        migrations.RemoveField(
            model_name='voucher',
            name='category',
        ),
        migrations.RemoveField(
            model_name='voucher',
            name='product',
        ),
        migrations.AddField(
            model_name='sale',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='voucher',
            name='apply_once_per_order',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='voucher',
            name='categories',
            field=models.ManyToManyField(blank=True, to='product.Category'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='collections',
            field=models.ManyToManyField(blank=True, to='product.Collection'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='countries',
            field=django_countries.fields.CountryField(blank=True, max_length=749, multiple=True),
        ),
        migrations.AddField(
            model_name='voucher',
            name='products',
            field=models.ManyToManyField(blank=True, to='product.Product'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='type',
            field=models.CharField(choices=[('value', 'All products'), ('product', 'Specific products'), ('collection', 'Specific collections of products'), ('category', 'Specific categories of products'), ('shipping', 'Shipping')], default='value', max_length=20),
        ),
    ]
