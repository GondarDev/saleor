# Generated by Django 3.2.12 on 2022-02-24 09:13

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0130_save_order_token_in_relation_models"),
        ("account", "0063_save_customerevent_order_token"),
        ("discount", "0036_save_discocunt_order_token"),
        ("invoice", "0007_save_invoice_order_token"),
        ("payment", "0032_save_payment_order_token"),
    ]

    operations = [
        migrations.RunSQL(
            """
                ALTER TABLE order_order
                DROP CONSTRAINT order_order_pkey;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name="order",
            name="token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
        migrations.RemoveField(
            model_name="order",
            name="id",
        ),
    ]
