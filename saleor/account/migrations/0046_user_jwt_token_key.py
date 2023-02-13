# Generated by Django 3.0.6 on 2020-06-08 13:24

from functools import partial
import django.utils.crypto
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0045_auto_20200427_0425"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="jwt_token_key",
            field=models.CharField(
                default=partial(django.utils.crypto.get_random_string, length=12),
                max_length=12,
            ),
        ),
    ]
