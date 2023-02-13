# Generated by Django 3.1.7 on 2021-03-08 11:35

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("warehouse", "0012_auto_20210115_1307"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="warehouse",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["private_metadata"], name="warehouse_p_meta_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="warehouse",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["metadata"], name="warehouse_meta_idx"
            ),
        ),
    ]
