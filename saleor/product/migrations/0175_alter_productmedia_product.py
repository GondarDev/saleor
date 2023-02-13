# Generated by Django 3.2.14 on 2022-07-19 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0174_drop_media_to_remove"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productmedia",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="media",
                to="product.product",
            ),
        ),
    ]
