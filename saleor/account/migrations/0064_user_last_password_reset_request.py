# Generated by Django 3.2.16 on 2023-01-24 12:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0063_user_user_p_meta_jsonb_path_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_password_reset_request",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
