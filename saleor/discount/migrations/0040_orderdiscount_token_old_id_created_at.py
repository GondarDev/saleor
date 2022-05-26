# Generated by Django 3.2.13 on 2022-05-02 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discount", "0039_rename_created_sale_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderdiscount",
            name="created_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="orderdiscount",
            name="old_id",
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="orderdiscount",
            name="token",
            field=models.UUIDField(null=True, unique=True),
        ),
    ]
