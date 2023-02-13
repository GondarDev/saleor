# Generated by Django 3.1.5 on 2021-01-21 09:19

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


def parse_draftjs_content_to_string(definitions):
    string = ""
    blocks = definitions.get("blocks")
    if not blocks or not isinstance(blocks, list):
        return ""
    for block in blocks:
        text = block.get("text")
        if not text:
            continue
        string += f"{text} "

    return string


def parse_description_json_field(apps, schema):
    Product = apps.get_model("product", "Product")

    for product in Product.objects.iterator():
        product.description_plaintext = parse_draftjs_content_to_string(
            product.description_json
        )
        product.save()


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0129_add_product_types_and_attributes_perm"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="description_plaintext",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="product",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="product_pro_search__e78047_gin"
            ),
        ),
        migrations.RunSQL(
            """
            CREATE TRIGGER title_vector_update BEFORE INSERT OR UPDATE
            ON product_product FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger(
                'search_vector', 'pg_catalog.english', 'description_plaintext', 'name'
            )


        """
        ),
        migrations.RunSQL(
            """
            CREATE FUNCTION messages_trigger() RETURNS trigger AS $$
            begin
              new.search_vector :=
                 setweight(
                 to_tsvector('pg_catalog.english', coalesce(new.name,'')), 'A'
                 ) ||
                 setweight(
                 to_tsvector(
                 'pg_catalog.english', coalesce(new.description_plaintext,'')),
                 'B'
                 );
              return new;
            end
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
                ON product_product FOR EACH ROW EXECUTE FUNCTION messages_trigger();
            """
        ),
        migrations.RunPython(
            parse_description_json_field,
            migrations.RunPython.noop,
        ),
    ]
