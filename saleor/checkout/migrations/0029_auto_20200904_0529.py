# Generated by Django 3.1 on 2020-09-04 05:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0028_auto_20200824_1019"),
    ]

    operations = [
        migrations.AlterField(
            model_name="checkout",
            name="discount_amount",
            field=models.DecimalField(decimal_places=3, default=0, max_digits=12),
        ),
    ]
