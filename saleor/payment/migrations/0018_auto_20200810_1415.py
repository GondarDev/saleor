# Generated by Django 3.1 on 2020-08-10 14:15

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0017_payment_payment_method_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="gateway_response",
            field=models.JSONField(
                encoder=django.core.serializers.json.DjangoJSONEncoder
            ),
        ),
    ]
