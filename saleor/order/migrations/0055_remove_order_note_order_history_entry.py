# Generated by Django 2.0.8 on 2018-09-10 13:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("order", "0054_move_data_to_order_events")]

    operations = [
        migrations.RemoveField(model_name="orderhistoryentry", name="order"),
        migrations.RemoveField(model_name="orderhistoryentry", name="user"),
        migrations.RemoveField(model_name="ordernote", name="order"),
        migrations.RemoveField(model_name="ordernote", name="user"),
        migrations.DeleteModel(name="OrderHistoryEntry"),
        migrations.DeleteModel(name="OrderNote"),
    ]
