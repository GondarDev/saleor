# Generated by Django 2.0.3 on 2018-05-30 12:26

from django.db import migrations, models

import saleor.account.models


class Migration(migrations.Migration):

    dependencies = [("account", "0019_auto_20180528_1205")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="token",
            field=models.UUIDField(
                default=saleor.account.models.get_token, editable=False
            ),
        )
    ]
