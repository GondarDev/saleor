# Generated by Django 3.2.5 on 2021-08-24 09:52

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0030_auto_20210823_1702"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="payment",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["private_metadata"], name="payment_p_meta_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["metadata"], name="payment_meta_idx"
            ),
        ),
    ]
