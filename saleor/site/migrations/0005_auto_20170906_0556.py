# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-06 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("site", "0004_auto_20170221_0426")]

    operations = [
        migrations.AlterField(
            model_name="authorizationkey",
            name="name",
            field=models.CharField(
                choices=[
                    (b"facebook", b"Facebook-Oauth2"),
                    (b"google-oauth2", b"Google-Oauth2"),
                ],
                max_length=20,
                verbose_name="name",
            ),
        )
    ]
