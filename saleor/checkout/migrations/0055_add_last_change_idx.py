# Generated by Django 3.2.18 on 2023-03-24 09:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0054_alter_checkout_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="checkout",
            name="last_change",
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
