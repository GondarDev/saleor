# Generated by Django 3.2.5 on 2021-07-19 12:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("app", "0004_auto_20210308_1135"),
    ]

    operations = [
        migrations.CreateModel(
            name="AppExtension",
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
                ("label", models.CharField(max_length=256)),
                ("url", models.URLField()),
                (
                    "view",
                    models.CharField(choices=[("product", "product")], max_length=128),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("overview", "overview"), ("details", "details")],
                        max_length=128,
                    ),
                ),
                (
                    "target",
                    models.CharField(
                        choices=[
                            ("more_actions", "more_actions"),
                            ("create", "create"),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    "app",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extensions",
                        to="app.app",
                    ),
                ),
                (
                    "permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this app extension.",
                        to="auth.Permission",
                    ),
                ),
            ],
        ),
    ]
