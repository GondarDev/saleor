# Generated by Django 2.1.4 on 2019-02-21 01:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("product", "0087_auto_20190208_0326")]

    operations = [
        migrations.AlterField(
            model_name="collection",
            name="is_published",
            field=models.BooleanField(default=True),
        )
    ]
