# Generated by Django 3.2.2 on 2021-07-13 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_auto_20210308_1135"),
        ("invoice", "0005_auto_20210308_1135"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoiceevent",
            name="app",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="app.app",
            ),
        ),
    ]
