# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def clear_attributes(apps, schema_editor):
    Variant = apps.get_model("product", "ProductVariant")
    for variant in Variant.objects.all():
        variant.attributes = ''
        variant.save()


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0022_auto_20150623_0913'),
    ]

    operations = [
        migrations.RunPython(clear_attributes),
    ]
