# Generated by Django 2.0.8 on 2018-09-19 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0059_auto_20180913_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='translated_product_name',
            field=models.CharField(blank=True, default='', max_length=386),
        ),
    ]
