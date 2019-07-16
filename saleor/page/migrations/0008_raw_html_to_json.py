# Generated by Django 2.2.3 on 2019-07-15 07:51

from django.db import migrations
from html_to_draftjs import html_to_draftjs

from ...core.utils.draftjs import json_content_to_raw_text


def convert_pages_html_to_json(apps, schema_editor):
    Page = apps.get_model("page", "Page")
    qs = Page.objects.all()

    for page in qs:
        content_json = page.content_json
        content_raw = json_content_to_raw_text(content_json)

        # Override the the JSON content if there was nothing in it
        if not content_raw.strip():
            page.description_json = html_to_draftjs(page.content)
            page.save(update_fields=["content_json"])

    PageTranslation = apps.get_model("page", "PageTranslation")
    qs = PageTranslation.objects.all()

    for translation in qs:
        content_json = translation.content_json
        content_raw = json_content_to_raw_text(content_json)

        # Override the the JSON content if there was nothing in it
        if not content_raw.strip():
            translation.description_json = html_to_draftjs(translation.content)
            translation.save(update_fields=["content_json"])


class Migration(migrations.Migration):

    dependencies = [("page", "0007_auto_20190225_0252")]

    operations = [migrations.RunPython(convert_pages_html_to_json)]
