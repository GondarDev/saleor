# Generated by Django 2.2.9 on 2020-01-20 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0014_django_price_2"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="action_required",
            field=models.BooleanField(default=False),
        ),
    ]
