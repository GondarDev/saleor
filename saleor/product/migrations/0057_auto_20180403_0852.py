# Generated by Django 2.0.3 on 2018-04-03 13:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("product", "0056_auto_20180330_0321")]

    operations = [
        migrations.AlterField(
            model_name="productvariant",
            name="name",
            field=models.CharField(blank=True, max_length=255),
        )
    ]
