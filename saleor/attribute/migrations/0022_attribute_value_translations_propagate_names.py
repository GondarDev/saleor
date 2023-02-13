# Generated by Django 3.2.16 on 2022-10-17 10:10

import re
import warnings
from typing import Dict, Optional

from django.db import migrations
from django.template.defaultfilters import truncatechars
from django.utils.html import strip_tags
from urllib3.util import parse_url

# Start copy of /saleor/core/utils/editorjs.py
BLACKLISTED_URL_SCHEMES = ("javascript",)
HYPERLINK_TAG_WITH_URL_PATTERN = r"(.*?<a\s+href=\\?\")(\w+://\S+[^\\])(\\?\">)"


def clean_editor_js(definitions: Optional[Dict], *, to_string: bool = False):
    """Sanitize a given EditorJS JSON definitions.

    Look for not allowed URLs, replaced them with `invalid` value, and clean valid ones.

    `to_string` flag is used for returning concatenated string from all blocks
     instead of returning json object.
    """
    if definitions is None:
        return "" if to_string else definitions

    blocks = definitions.get("blocks")

    if not blocks or not isinstance(blocks, list):
        return "" if to_string else definitions

    plain_text_list = []

    for index, block in enumerate(blocks):
        block_type = block["type"]
        data = block.get("data")
        if not data or not isinstance(data, dict):
            continue

        if block_type == "list":
            for item_index, item in enumerate(block["data"]["items"]):
                if not item:
                    continue
                new_text = clean_text_data(item)
                if to_string:
                    plain_text_list.append(strip_tags(new_text))
                else:
                    blocks[index]["data"]["items"][item_index] = new_text
        else:
            text = block["data"].get("text")
            if not text:
                continue
            new_text = clean_text_data(text)
            if to_string:
                plain_text_list.append(strip_tags(new_text))
            else:
                blocks[index]["data"]["text"] = new_text

    return " ".join(plain_text_list) if to_string else definitions


def clean_text_data(text: str):
    """Look for url in text, check if URL is allowed and return the cleaned URL.

    By default, only the protocol ``javascript`` is denied.
    """

    if not text:
        return

    end_of_match = 0
    new_text = ""
    for match in re.finditer(HYPERLINK_TAG_WITH_URL_PATTERN, text):
        original_url = match.group(2)
        original_url.strip()

        url = parse_url(original_url)
        new_url = url.url
        if url.scheme in BLACKLISTED_URL_SCHEMES:
            warnings.warn(
                f"An invalid url was sent: {original_url} "
                f"-- Scheme: {url.scheme} is blacklisted"
            )
            new_url = "#invalid"

        new_text += match.group(1) + new_url + match.group(3)
        end_of_match = match.end()

    if end_of_match:
        new_text += text[end_of_match:]

    return new_text if new_text else text


# End copy of /saleor/core/utils/editorjs.py


def queryset_in_batches(queryset):
    """Slice a queryset into batches.

    Input queryset should be sorted be pk.
    """
    start_pk = 0

    while True:
        qs = queryset.filter(pk__gt=start_pk)[:2000]
        pks = list(qs.values_list("pk", flat=True))

        if not pks:
            break

        yield pks

        start_pk = pks[-1]


def propagate_names_for_rich_text_attribute_value_translations(apps, schema_editor):
    AttributeValueTranslation = apps.get_model("attribute", "AttributeValueTranslation")

    queryset = (
        AttributeValueTranslation.objects.exclude(rich_text=None)
        .filter(name="")
        .order_by("pk")
    )

    for batch_pks in queryset_in_batches(queryset):
        batch = AttributeValueTranslation.objects.filter(pk__in=batch_pks)
        instances = []
        for instance in batch:
            instance.name = truncatechars(
                clean_editor_js(instance.rich_text, to_string=True), 100
            )
            instances.append(instance)
        AttributeValueTranslation.objects.bulk_update(instances, ["name"])


class Migration(migrations.Migration):
    dependencies = [
        ("attribute", "0021_auto_20220406_1713"),
    ]

    operations = [
        migrations.RunPython(
            propagate_names_for_rich_text_attribute_value_translations,
            migrations.RunPython.noop,
        ),
    ]
