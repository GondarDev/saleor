# Generated by Django 2.2.2 on 2019-06-18 12:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [("discount", "0012_auto_20190329_0836")]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="sale",
            name="start_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="voucher",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="voucher",
            name="start_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
