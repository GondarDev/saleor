# Generated by Django 1.10.5 on 2017-01-27 11:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


def create_default_site(apps, schema_editor):
    SiteSettings = apps.get_model("site", "SiteSettings")
    settings_id = getattr(settings, "SITE_SETTINGS_ID", None)
    SiteSettings.objects.get_or_create(
        pk=settings_id,
        defaults={
            "name": "Saleor e-commerce",
            "header_text": "Test Saleor - a sample shop!",
            "domain": "localhost:8000",
        },
    )


class Migration(migrations.Migration):

    dependencies = [("site", "0001_initial")]

    operations = [
        migrations.RunPython(create_default_site, lambda app, schema_editor: None)
    ]
