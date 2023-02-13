# Generated by Django 2.0.2 on 2018-03-11 18:54
from django.core.validators import MaxLengthValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("product", "0052_slug_field_length")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="seo_description",
            field=models.CharField(
                blank=True,
                null=True,
                max_length=300,
                validators=[MaxLengthValidator(300)],
            ),
            preserve_default=False,
        ),
    ]
