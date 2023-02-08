from functools import partial

from django.apps import apps as registry
from django.db import connection, migrations
from django.db.models.signals import post_migrate

from saleor.order.tasks import send_order_updated


RAW_SQL = """
    UPDATE "order_orderline"
    SET
        "undiscounted_total_price_gross_amount" = CASE
            WHEN NOT (
                ("order_orderline"."undiscounted_unit_price_gross_amount" * "order_orderline"."quantity") =
                                                    "order_orderline"."undiscounted_total_price_gross_amount")
            THEN ("order_orderline"."undiscounted_unit_price_gross_amount" * "order_orderline"."quantity")
            ELSE "order_orderline"."undiscounted_total_price_gross_amount" END,

        "undiscounted_total_price_net_amount"   = CASE
            WHEN NOT (
                ("order_orderline"."undiscounted_unit_price_net_amount" * "order_orderline"."quantity") =
                                                    "order_orderline"."undiscounted_total_price_net_amount")
            THEN ("order_orderline"."undiscounted_unit_price_net_amount" * "order_orderline"."quantity")
            ELSE "order_orderline"."undiscounted_total_price_net_amount" END

    WHERE (
        NOT ("order_orderline"."undiscounted_total_price_gross_amount" =
                ("order_orderline"."undiscounted_unit_price_gross_amount" *
                "order_orderline"."quantity")) OR
        NOT ("order_orderline"."undiscounted_total_price_net_amount" =
                ("order_orderline"."undiscounted_unit_price_net_amount" *
                "order_orderline"."quantity")))
    RETURNING "order_orderline"."id";
"""  # noqa: E501


def set_order_line_base_prices(apps, schema_editor):
    def on_migrations_complete(sender=None, **kwargs):
        order_ids = list(kwargs.get("updated_orders_pks"))
        send_order_updated.delay(order_ids)

    with connection.cursor() as cursor:
        cursor.execute(RAW_SQL)
        records = cursor.fetchall()

    updated_orders_pks = {record[0] for record in records}
    if updated_orders_pks:
        sender = registry.get_app_config("order")
        post_migrate.connect(
            partial(on_migrations_complete, updated_orders_pks=updated_orders_pks),
            weak=False,
            dispatch_uid="send_order_updated",
            sender=sender,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0138_orderline_base_price"),
    ]

    operations = [
        migrations.RunPython(
            set_order_line_base_prices, reverse_code=migrations.RunPython.noop
        ),
    ]
