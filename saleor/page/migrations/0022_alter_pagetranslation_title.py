# Generated by Django 3.2.2 on 2021-05-18 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("page", "0021_auto_20210308_1135"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pagetranslation",
            name="title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
