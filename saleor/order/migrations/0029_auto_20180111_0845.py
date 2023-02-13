# Generated by Django 1.11.5 on 2018-01-11 14:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("order", "0028_status_fsm")]

    operations = [
        migrations.AlterField(
            model_name="deliverygroup",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "Processing"),
                    ("cancelled", "Cancelled"),
                    ("shipped", "Shipped"),
                ],
                default="new",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="ordernote",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
