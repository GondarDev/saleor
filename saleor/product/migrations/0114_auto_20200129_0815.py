# Generated by Django 2.2.9 on 2020-01-29 14:15

from django.db import migrations, models
from django.db.models.functions import Lower
from django.utils.text import slugify


def create_unique_slug_for_products(apps, schema_editor):
    Product = apps.get_model("product", "Product")

    products = (
        Product.objects.filter(slug__isnull=True).order_by(Lower("name")).iterator()
    )
    previous_char = ""
    slug_values = []
    for product in products:
        first_char = product.name[0].lower()
        if first_char != previous_char:
            previous_char = first_char
            slug_values = Product.objects.filter(
                slug__istartswith=first_char
            ).values_list("slug", flat=True)

        slug = generate_unique_slug(product, slug_values)
        product.slug = slug
        slug_values.append(slug)


def generate_unique_slug(instance, slug_values):
    slug = slugify(instance.name)
    unique_slug = slug
    extension = 1

    while unique_slug in slug_values:
        extension += 1
        unique_slug = f"{slug}-{extension}"

    return unique_slug


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0113_auto_20200129_0717"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(null=True, max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="product", name="name", field=models.CharField(max_length=250),
        ),
        migrations.RunPython(
            create_unique_slug_for_products, migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="product",
            name="slug",
            field=models.SlugField(max_length=255, unique=True),
        ),
    ]
