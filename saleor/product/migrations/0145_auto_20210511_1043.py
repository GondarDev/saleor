# Generated by Django 3.1.8 on 2021-05-11 10:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0144_auto_20210318_1155"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="productchannellisting",
            index=models.Index(
                fields=["publication_date"], name="product_pro_publica_67290c_idx"
            ),
        ),
    ]
