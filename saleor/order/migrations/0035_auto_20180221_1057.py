# Generated by Django 2.0.2 on 2018-02-21 16:57

from django.db import migrations


def populate_orders_total_gross(apps, schema_editor):
    Order = apps.get_model('order', 'Order')
    orders_with_total = Order.objects.filter(
        total_net__isnull=False).iterator()

    for order in orders_with_total:
        order.total_gross = order.total_net + order.total_tax
        order.save()


def populate_orders_total_tax(apps, schema_editor):
    Order = apps.get_model('order', 'Order')
    orders_with_total = Order.objects.filter(
        total_net__isnull=False).iterator()

    for order in orders_with_total:
        order.total_tax = order.total_gross - order.total_net
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0034_auto_20180221_1056'),
    ]

    operations = [
        migrations.RunPython(
            populate_orders_total_gross, populate_orders_total_tax),
    ]
