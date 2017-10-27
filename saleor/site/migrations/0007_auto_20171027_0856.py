# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-27 13:56
from __future__ import unicode_literals

from django.db import migrations


def link_to_sites(apps, schema_editor):
    SiteSettings = apps.get_model('site', 'SiteSettings')
    Site = apps.get_model('sites', 'Site')

    for site in SiteSettings.objects.all():
        site.site = Site.objects.get_or_create(domain=site.domain, name=site.name)[0]
        site.save()


class Migration(migrations.Migration):

    dependencies = [
        ('site', '0006_auto_20171025_0454'),
    ]

    operations = [
        migrations.RunPython(link_to_sites),
    ]
