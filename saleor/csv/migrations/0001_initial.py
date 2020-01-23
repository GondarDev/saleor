# Generated by Django 2.2.9 on 2020-01-23 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Job",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "pending"),
                            ("SUCCESS", "success"),
                            ("FAILED", "failed"),
                        ],
                        max_length=50,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(null=True)),
                ("content_file", models.FileField(null=True, upload_to="csv_files")),
            ],
        ),
    ]
