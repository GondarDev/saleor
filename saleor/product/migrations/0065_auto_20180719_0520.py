# Generated by Django 2.0.3 on 2018-07-19 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0064_productvariant_handle_stock'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'permissions': (('manage_products', 'Manage products. Access to inventory and inventory management.'),)},
        ),
    ]
