# Generated by Django 2.0.3 on 2018-08-03 10:28

import django.db.models.deletion
from django.contrib.postgres import fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("menu", "0005_auto_20180719_0520")]

    operations = [
        migrations.CreateModel(
            name="MenuItemTranslation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("language_code", models.CharField(max_length=10)),
                ("name", models.CharField(max_length=128)),
                (
                    "menu_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="menu.MenuItem",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="menu",
            name="json_content",
            field=fields.JSONField(blank=True, default=dict),
        ),
        migrations.AlterUniqueTogether(
            name="menuitemtranslation", unique_together={("language_code", "menu_item")}
        ),
    ]
