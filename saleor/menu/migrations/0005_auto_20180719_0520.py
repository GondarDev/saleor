# Generated by Django 2.0.3 on 2018-07-19 10:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("menu", "0004_sort_order_index")]

    operations = [
        migrations.AlterModelOptions(
            name="menu",
            options={"permissions": (("manage_menus", "Manage navigation."),)},
        )
    ]
