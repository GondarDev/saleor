# Generated by Django 2.1.3 on 2018-12-06 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_rename_payment_method_to_payment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['pk']},
        ),
    ]
