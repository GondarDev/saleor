# Generated by Django 3.2.12 on 2022-04-12 13:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0139_fulfil_orderline_token_old_id_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderline",
            name="old_id",
            field=models.PositiveIntegerField(null=True, unique=True, blank=True),
        ),
        migrations.AlterField(
            model_name="orderline",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
