# Generated by Django 2.0.3 on 2018-08-22 12:20

import django_measurement.models
from django.db import migrations

import saleor.core.weight


class Migration(migrations.Migration):
    dependencies = [("product", "0067_remove_product_is_featured")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="weight",
            field=django_measurement.models.MeasurementField(
                blank=True, measurement_class="Mass", null=True
            ),
        ),
        migrations.AddField(
            model_name="producttype",
            name="weight",
            field=django_measurement.models.MeasurementField(
                default=saleor.core.weight.zero_weight, measurement_class="Mass"
            ),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="weight",
            field=django_measurement.models.MeasurementField(
                blank=True, measurement_class="Mass", null=True
            ),
        ),
    ]
