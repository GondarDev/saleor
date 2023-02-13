# Generated by Django 3.1.8 on 2021-05-06 10:58

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0049_user_language_code"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["email", "first_name", "last_name"],
                name="account_use_email_d707ff_gin",
            ),
        ),
    ]
