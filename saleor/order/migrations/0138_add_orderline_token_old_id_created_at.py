# Generated by Django 3.2.12 on 2022-04-11 12:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0137_alter_orderevent_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderline",
            name="token",
            field=models.UUIDField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name="orderline",
            name="old_id",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="fulfillmentline",
            name="order_line_token",
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name="orderline",
            name="created_at",
            field=models.DateTimeField(null=True),
        ),
    ]
