# Generated by Django 2.2.7 on 2019-12-19 17:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("checkout", "0021_django_price_2")]

    operations = [
        migrations.AlterModelOptions(
            name="checkout",
            options={
                "ordering": ("-last_change",),
                "permissions": (("manage_checkouts", "Manage checkouts"),),
            },
        )
    ]
