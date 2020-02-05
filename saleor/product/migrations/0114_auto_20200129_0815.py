# Generated by Django 2.2.9 on 2020-01-29 14:15

from django.db import migrations, models
from django.utils.text import slugify


def create_unique_slug_for_products(apps, schema_editor):
    Product = apps.get_model("product", "Product")
    for product in Product.objects.all():
        if not product.slug:
            product.slug = generate_unique_slug(product)
            product.save(update_fields=["slug"])


def generate_unique_slug(instance):
    slug = slugify(instance.name)
    unique_slug = slug

    ModelClass = instance.__class__
    extension = 1

    pattern = rf"{slug}-\d+$|{slug}$"
    slug_values = (
        ModelClass._default_manager.filter(slug__iregex=pattern)
        .exclude(pk=instance.pk)
        .values_list("slug", flat=True)
    )

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
