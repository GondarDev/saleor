# Generated by Django 3.1.8 on 2021-05-06 08:35

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0103_auto_20210401_1105"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="order",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["user_email"], name="order_order_user_em_bda05b_gin"
            ),
        ),
    ]
