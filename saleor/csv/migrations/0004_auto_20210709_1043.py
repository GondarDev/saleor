# Generated by Django 3.2.2 on 2021-07-09 10:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0004_auto_20210308_1135"),
        ("csv", "0003_auto_20200810_1415"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exportevent",
            name="app",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="export_csv_events",
                to="app.app",
            ),
        ),
        migrations.AlterField(
            model_name="exportevent",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="export_csv_events",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
