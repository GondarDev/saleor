# Generated by Django 2.2.4 on 2019-08-14 09:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("discount", "0016_auto_20190716_0330")]

    operations = [
        migrations.RenameField(
            model_name="voucher",
            old_name="min_amount_spent",
            new_name="min_spent_amount",
        ),
        migrations.AddField(
            model_name="voucher",
            name="currency",
            field=models.CharField(default=settings.DEFAULT_CURRENCY, max_length=10),
        ),
    ]
