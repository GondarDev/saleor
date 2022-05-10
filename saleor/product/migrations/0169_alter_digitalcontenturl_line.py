# Generated by Django 3.2.12 on 2022-04-12 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0168_fulfil_digitalcontenturl_orderline_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="digitalcontenturl",
            name="line",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="digital_content_url",
                to="order.orderline",
                to_field="old_id",
            ),
        ),
    ]
