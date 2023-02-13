# Generated by Django 3.1.7 on 2021-03-08 11:35

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("attribute", "0006_auto_20210105_1031"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="attribute",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["private_metadata"], name="attribute_p_meta_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="attribute",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["metadata"], name="attribute_meta_idx"
            ),
        ),
    ]
