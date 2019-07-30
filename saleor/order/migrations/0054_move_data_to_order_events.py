# Generated by Django 2.0.8 on 2018-09-11 06:09

from django.db import migrations

from saleor.order import OrderEvents


def move_order_note_to_events(apps, schema_editor):
    """Move legacy OrderNote content to OrderEvent.

    It's meant to prevent data loss during the migration.
    """
    OrderNote = apps.get_model("order", "OrderNote")
    OrderEvent = apps.get_model("order", "OrderEvent")

    for note in OrderNote.objects.all():
        OrderEvent.objects.create(
            type="note_added",
            user=note.user,
            parameters={"message": note.content},
            order=note.order,
            date=note.date,
        )


def move_order_history_entry_to_events(apps, schema_editor):
    """Move legacy OrderHistoryEntry content to OrderEvent.

    It is meant to prevent data loss during the migration.
    """
    OrderHistoryEntry = apps.get_model("order", "OrderHistoryEntry")
    OrderEvent = apps.get_model("order", "OrderEvent")

    for entry in OrderHistoryEntry.objects.all():
        OrderEvent.objects.create(
            type=OrderEvents.OTHER,
            parameters={"message": entry.content},
            date=entry.date,
            order=entry.order,
            user=entry.user,
        )


class Migration(migrations.Migration):

    dependencies = [("order", "0053_orderevent")]

    operations = [
        migrations.RunPython(move_order_note_to_events),
        migrations.RunPython(move_order_history_entry_to_events),
    ]
