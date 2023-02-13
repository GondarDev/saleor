# Generated by Django 3.2.13 on 2022-06-06 14:31

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0150_update_authorize_and_charge_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="order_tsearch"
            ),
        ),
    ]
