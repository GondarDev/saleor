# Generated by Django 2.2.1 on 2019-05-16 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("payment", "0010_auto_20190220_2001")]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="kind",
            field=models.CharField(
                choices=[
                    ("auth", "Authorization"),
                    ("refund", "Refund"),
                    ("capture", "Capture"),
                    ("void", "Void"),
                ],
                max_length=10,
            ),
        )
    ]
