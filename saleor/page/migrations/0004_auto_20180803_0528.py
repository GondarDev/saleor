# Generated by Django 2.0.3 on 2018-08-03 10:28

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("page", "0003_auto_20180719_0520")]

    operations = [
        migrations.CreateModel(
            name="PageTranslation",
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
                    "seo_title",
                    models.CharField(
                        blank=True,
                        max_length=70,
                        null=True,
                        validators=[django.core.validators.MaxLengthValidator(70)],
                    ),
                ),
                (
                    "seo_description",
                    models.CharField(
                        blank=True,
                        max_length=300,
                        null=True,
                        validators=[django.core.validators.MaxLengthValidator(300)],
                    ),
                ),
                ("language_code", models.CharField(max_length=10)),
                ("title", models.CharField(blank=True, max_length=255)),
                ("content", models.TextField()),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="page.Page",
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="pagetranslation", unique_together={("language_code", "page")}
        ),
    ]
