# Generated by Django 2.2.9 on 2020-01-20 07:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0023_checkout_country"),
    ]

    operations = [
        migrations.AlterField(
            model_name="checkout",
            name="last_change",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
