# Generated by Django 3.1.2 on 2020-11-10 09:29

import os

import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def create_collection_channel_listing(apps, schema_editor):
    CollectionChannelListing = apps.get_model("product", "CollectionChannelListing")
    Collection = apps.get_model("product", "Collection")
    Channel = apps.get_model("channel", "Channel")

    if Collection.objects.exists():
        currency = os.environ.get("DEFAULT_CURRENCY", "USD")
        name = f"Channel {currency}"
        channel, _ = Channel.objects.get_or_create(
            currency_code=currency,
            defaults={"name": name, "slug": slugify(name)},
        )
        for collection in Collection.objects.iterator():
            CollectionChannelListing.objects.create(
                collection=collection,
                channel=channel,
                is_published=collection.is_published,
                publication_date=collection.publication_date,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("channel", "0001_initial"),
        ("product", "0134_product_channel_listing"),
    ]

    operations = [
        migrations.CreateModel(
            name="CollectionChannelListing",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("publication_date", models.DateField(blank=True, null=True)),
                ("is_published", models.BooleanField(default=False)),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collection_listings",
                        to="channel.channel",
                    ),
                ),
                (
                    "collection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="channel_listings",
                        to="product.collection",
                    ),
                ),
            ],
            options={
                "ordering": ("pk",),
                "unique_together": {("collection", "channel")},
            },
        ),
        migrations.RunPython(
            create_collection_channel_listing, migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name="collection",
            name="is_published",
        ),
        migrations.RemoveField(
            model_name="collection",
            name="publication_date",
        ),
    ]
