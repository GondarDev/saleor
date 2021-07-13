# Generated by Django 3.1.8 on 2021-04-29 07:02

from django.db import migrations, models
from django.db.models.functions import Coalesce


def update_orders_total_paid_in_db(apps, schema_editor):
    Order = apps.get_model("order", "Order")
    Order.objects.update(
        total_paid_amount=models.Subquery(
            Order.objects.filter(id=models.OuterRef("id"))
            .annotate(
                _total_paid_amount=Coalesce(
                    models.Sum("payments__captured_amount"),
                    0,
                    output_field=models.DecimalField(),
                )
            )
            .values("_total_paid_amount")[:1],
        )
    )


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0104_auto_20210506_0835"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="total_paid_amount",
            field=models.DecimalField(decimal_places=3, default=0, max_digits=12),
        ),
        migrations.RunPython(update_orders_total_paid_in_db, migrations.RunPython.noop),
    ]
