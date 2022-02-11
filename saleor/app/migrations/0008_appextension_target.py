# Generated by Django 3.2.6 on 2022-01-27 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_auto_20220127_0942"),
    ]

    operations = [
        migrations.AddField(
            model_name="appextension",
            name="target",
            field=models.CharField(
                choices=[("popup", "popup"), ("app_page", "app_page")],
                default="popup",
                max_length=128,
            ),
        ),
    ]
