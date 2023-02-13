# Generated by Django 2.2.6 on 2019-12-19 15:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("account", "0036_auto_20191209_0407")]

    operations = [
        migrations.AlterField(
            model_name="customerevent",
            name="type",
            field=models.CharField(
                choices=[
                    ("ACCOUNT_CREATED", "account_created"),
                    ("PASSWORD_RESET_LINK_SENT", "password_reset_link_sent"),
                    ("PASSWORD_RESET", "password_reset"),
                    ("EMAIL_CHANGED_REQUEST", "email_changed_request"),
                    ("PASSWORD_CHANGED", "password_changed"),
                    ("EMAIL_CHANGED", "email_changed"),
                    ("PLACED_ORDER", "placed_order"),
                    ("NOTE_ADDED_TO_ORDER", "note_added_to_order"),
                    ("DIGITAL_LINK_DOWNLOADED", "digital_link_downloaded"),
                    ("CUSTOMER_DELETED", "customer_deleted"),
                    ("NAME_ASSIGNED", "name_assigned"),
                    ("EMAIL_ASSIGNED", "email_assigned"),
                    ("NOTE_ADDED", "note_added"),
                ],
                max_length=255,
            ),
        )
    ]
