# Generated by Django 2.2.10 on 2020-02-17 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0015_auto_20190725_0811"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="menuitemtranslation",
            options={"ordering": ("language_code", "menu_item")},
        ),
    ]
