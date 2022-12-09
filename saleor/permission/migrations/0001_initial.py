# Generated by Django 3.2.16 on 2022-11-22 11:20

from django.db import migrations, models
import saleor.permission.models


# Forward helpers
DROP_OLD_CONSTRAINTS = """
ALTER TABLE auth_permission
    DROP CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq;

ALTER TABLE auth_permission
    DROP CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co;
"""

CREATE_NEW_CONSTRAINTS = """
ALTER TABLE permission_permission
    ADD CONSTRAINT permission_permission_content_type_id_codename_aa582bb6_uniq
    UNIQUE (content_type_id, codename);

ALTER TABLE permission_permission
    ADD CONSTRAINT permission_permissio_content_type_id_e526e8f2_fk_django_co
    FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
    DEFERRABLE INITIALLY DEFERRED;
"""


RENAME_CONSTRAINTS_AND_INDEX = """
ALTER TABLE permission_permission RENAME CONSTRAINT auth_permission_pkey
    TO permission_permission_pkey;

ALTER INDEX IF EXISTS auth_permission_content_type_id_2f476e4b
    RENAME TO permission_permission_content_type_id_e526e8f2;
"""


def rename_permission_table(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    schema_editor.alter_db_table(
        Permission,
        "auth_permission",
        "permission_permission",
    )


# Reverse helpers
DROP_OLD_CONSTRAINTS_REVERSE = """
ALTER TABLE auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq
    UNIQUE (content_type_id, codename);

ALTER TABLE auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co
    FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
    DEFERRABLE INITIALLY DEFERRED;
"""

CREATE_NEW_CONSTRAINTS_REVERSE = """
ALTER TABLE permission_permission
    DROP CONSTRAINT permission_permission_content_type_id_codename_aa582bb6_uniq;

ALTER TABLE permission_permission
    DROP CONSTRAINT permission_permissio_content_type_id_e526e8f2_fk_django_co;
"""

RENAME_CONSTRAINTS_AND_INDEX_REVERSE = """
ALTER TABLE permission_permission
    RENAME CONSTRAINT permission_permission_pkey
    TO auth_permission_pkey;

ALTER INDEX IF EXISTS permission_permission_content_type_id_e526e8f2
    RENAME TO auth_permission_content_type_id_2f476e4b;
"""


def rename_permission_table_reverse(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    schema_editor.alter_db_table(
        Permission,
        "permission_permission",
        "auth_permission",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0071_group"),
        ("app", "0017_app_audience"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    DROP_OLD_CONSTRAINTS, reverse_sql=DROP_OLD_CONSTRAINTS_REVERSE
                ),
                migrations.RunPython(
                    rename_permission_table, rename_permission_table_reverse
                ),
                migrations.RunSQL(
                    CREATE_NEW_CONSTRAINTS, reverse_sql=CREATE_NEW_CONSTRAINTS_REVERSE
                ),
                migrations.RunSQL(
                    RENAME_CONSTRAINTS_AND_INDEX,
                    reverse_sql=RENAME_CONSTRAINTS_AND_INDEX_REVERSE,
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
