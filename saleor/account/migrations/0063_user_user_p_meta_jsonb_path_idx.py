# Generated by Django 3.2.16 on 2022-12-27 10:22

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0062_alter_user_updated_at"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["private_metadata"],
                name="user_p_meta_jsonb_path_idx",
                opclasses=["jsonb_path_ops"],
            ),
        ),
    ]
