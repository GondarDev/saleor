# Generated by Django 3.1 on 2021-01-07 11:59

from django.db import migrations
from django.db.models import F

import saleor.core.db.fields
import saleor.core.utils.editorjs


def clean_description_field(apps, schema_editor):
    Category = apps.get_model("product", "Category")
    CategoryTranslation = apps.get_model("product", "CategoryTranslation")
    Collection = apps.get_model("product", "Collection")
    CollectionTranslation = apps.get_model("product", "CollectionTranslation")
    Product = apps.get_model("product", "Product")
    ProductTranslation = apps.get_model("product", "ProductTranslation")

    models = [
        Category,
        CategoryTranslation,
        Collection,
        CollectionTranslation,
        Product,
        ProductTranslation,
    ]

    for model in models:
        model.objects.all().update(description="{}")


def migrate_description_json_into_description_field(apps, schema_editor):
    Category = apps.get_model("product", "Category")
    CategoryTranslation = apps.get_model("product", "CategoryTranslation")
    Collection = apps.get_model("product", "Collection")
    CollectionTranslation = apps.get_model("product", "CollectionTranslation")
    Product = apps.get_model("product", "Product")
    ProductTranslation = apps.get_model("product", "ProductTranslation")

    models = [
        Category,
        CategoryTranslation,
        Collection,
        CollectionTranslation,
        Product,
        ProductTranslation,
    ]

    for model in models:
        model.objects.all().update(description=F("description_json"))


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0137_drop_attribute_models"),
    ]

    operations = [
        migrations.RunPython(
            clean_description_field,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="category",
            name="description",
            field=saleor.core.db.fields.SanitizedJSONField(
                blank=True,
                default=dict,
                sanitizer=saleor.core.utils.editorjs.clean_editor_js,
            ),
        ),
        migrations.AlterField(
            model_name="categorytranslation",
            name="description",
            field=saleor.core.db.fields.SanitizedJSONField(
                blank=True,
                default=dict,
                sanitizer=saleor.core.utils.editorjs.clean_editor_js,
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="description",
            field=saleor.core.db.fields.SanitizedJSONField(
                blank=True,
                default=dict,
                sanitizer=saleor.core.utils.editorjs.clean_editor_js,
            ),
        ),
        migrations.AlterField(
            model_name="collectiontranslation",
            name="description",
            field=saleor.core.db.fields.SanitizedJSONField(
                blank=True,
                default=dict,
                sanitizer=saleor.core.utils.editorjs.clean_editor_js,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="description",
            field=saleor.core.db.fields.SanitizedJSONField(
                blank=True,
                default=dict,
                sanitizer=saleor.core.utils.editorjs.clean_editor_js,
            ),
        ),
        migrations.AlterField(
            model_name="producttranslation",
            name="description",
            field=saleor.core.db.fields.SanitizedJSONField(
                blank=True,
                default=dict,
                sanitizer=saleor.core.utils.editorjs.clean_editor_js,
            ),
        ),
        migrations.RunPython(
            migrate_description_json_into_description_field,
            migrations.RunPython.noop,
        ),
    ]
