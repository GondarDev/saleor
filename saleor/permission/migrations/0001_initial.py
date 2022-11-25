# Generated by Django 3.2.16 on 2022-11-22 11:20

from django.db import migrations, models
import saleor.permission.models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("account", "0070_alter_user_uuid"),
        ("app", "0017_app_audience"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE auth_permission RENAME TO permission_permission "
                    ),
                    reverse_sql=(
                        "ALTER TABLE permission_permission RENAME TO auth_permission"
                    ),
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="Permission",
                    fields=[
                        (
                            "id",
                            models.AutoField(
                                verbose_name="ID",
                                serialize=False,
                                auto_created=True,
                                primary_key=True,
                            ),
                        ),
                        ("name", models.CharField(max_length=255, verbose_name="name")),
                        (
                            "content_type",
                            models.ForeignKey(
                                to="contenttypes.ContentType",
                                on_delete=models.CASCADE,
                                verbose_name="content type",
                                related_name="saleor_content_type",
                            ),
                        ),
                        (
                            "codename",
                            models.CharField(max_length=100, verbose_name="codename"),
                        ),
                    ],
                    options={
                        "ordering": [
                            "content_type__app_label",
                            "content_type__model",
                            "codename",
                        ],
                        "unique_together": {("content_type", "codename")},
                        "verbose_name": "permission",
                        "verbose_name_plural": "permissions",
                    },
                    managers=[
                        ("objects", saleor.permission.models.PermissionManager()),
                    ],
                ),
            ],
        ),
    ]
