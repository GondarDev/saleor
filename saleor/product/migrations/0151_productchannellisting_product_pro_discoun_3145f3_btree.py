# Generated by Django 3.2.6 on 2021-12-06 13:41

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0150_collection_collection_search_gin"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="productchannellisting",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["discounted_price_amount"],
                name="product_pro_discoun_3145f3_btree",
            ),
        ),
    ]
