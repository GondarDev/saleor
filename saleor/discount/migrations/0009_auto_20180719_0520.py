# Generated by Django 2.0.3 on 2018-07-19 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0008_sale_collections'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'permissions': (('manage_discounts', 'Manage sales and vouchers.'),)},
        ),
        migrations.AlterModelOptions(
            name='voucher',
            options={},
        ),
    ]
