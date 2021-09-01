# Generated by Django 3.2.2 on 2021-07-13 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0014_remove_warehouse_company_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="warehouse",
            name="click_and_collect_option",
            field=models.CharField(
                choices=[
                    ("disabled", "Disabled"),
                    ("local", "Local stock only"),
                    ("all", "All warehouses"),
                ],
                default="disabled",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="warehouse",
            name="is_private",
            field=models.BooleanField(default=True),
        ),
    ]
