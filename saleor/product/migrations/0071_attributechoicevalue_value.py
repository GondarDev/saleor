# Generated by Django 2.0.8 on 2018-09-14 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("product", "0070_auto_20180912_0329")]

    operations = [
        migrations.AddField(
            model_name="attributechoicevalue",
            name="value",
            field=models.CharField(default="", max_length=100),
        )
    ]
