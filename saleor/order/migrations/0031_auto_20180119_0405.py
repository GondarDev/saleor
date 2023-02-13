# Generated by Django 1.11.5 on 2018-01-19 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("order", "0030_auto_20180118_0605")]

    operations = [
        migrations.RemoveField(model_name="orderhistoryentry", name="comment"),
        migrations.RemoveField(model_name="orderhistoryentry", name="status"),
        migrations.AddField(
            model_name="orderhistoryentry",
            name="content",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="ordernote", name="content", field=models.TextField()
        ),
    ]
