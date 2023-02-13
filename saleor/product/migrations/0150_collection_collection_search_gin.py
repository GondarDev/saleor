# Generated by Django 3.2.6 on 2021-10-05 15:09

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0149_auto_20211004_1636"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="collection",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["name", "slug"],
                name="collection_search_gin",
                opclasses=["gin_trgm_ops", "gin_trgm_ops"],
            ),
        ),
    ]
