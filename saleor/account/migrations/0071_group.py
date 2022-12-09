# Generated by Django 3.2.16 on 2022-11-29 09:50

from django.db import migrations, models
import saleor.account.models

# Forward helpers
def rename_group_tables(apps, schema_editor):
    Permission = apps.get_model("auth", "Group")
    schema_editor.alter_db_table(
        Permission,
        "auth_group",
        "account_group",
    )
    PermissionGroup = Permission.permissions.through
    schema_editor.alter_db_table(
        PermissionGroup,
        "auth_group_permissions",
        "account_group_permissions",
    )


RENAME_CONSTRAINTS_AND_INDEX = """
ALTER TABLE account_group RENAME CONSTRAINT auth_group_pkey
    TO account_group_pkey;

ALTER TABLE account_group RENAME CONSTRAINT auth_group_name_key
    TO account_group_name_key;

ALTER INDEX IF EXISTS auth_group_name_a6ea08ec_like
    RENAME TO account_group_name_034e9f3f_like;
"""


# Reverse helpers
def rename_group_tables_reverse(apps, schema_editor):
    Permission = apps.get_model("auth", "Group")
    schema_editor.alter_db_table(
        Permission,
        "account_group",
        "auth_group",
    )
    PermissionGroup = Permission.permissions.through
    schema_editor.alter_db_table(
        PermissionGroup,
        "account_group_permissions",
        "auth_group_permissions",
    )


RENAME_CONSTRAINTS_AND_INDEX_REVERSE = """
ALTER TABLE account_group RENAME CONSTRAINT account_group_pkey
    TO auth_group_pkey;

ALTER TABLE account_group RENAME CONSTRAINT account_group_name_key
    TO auth_group_name_key;

ALTER INDEX IF EXISTS account_group_name_034e9f3f_like
    RENAME TO auth_group_name_a6ea08ec_like;
"""

DROP_OLD_CONSTRAINTS_REVERSE_FROM_0072 = """
ALTER TABLE auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq
    UNIQUE (group_id, permission_id);

ALTER TABLE auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id
    FOREIGN KEY (group_id) REFERENCES auth_group (id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm
    FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
    DEFERRABLE INITIALLY DEFERRED;
"""

DROP_OLD_CONSTRAINTS_REVERSE_FROM_APP_0018 = """
ALTER TABLE app_app_permissions
    ADD CONSTRAINT account_serviceaccou_permission_id_449791f0_fk_auth_perm
    FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
    DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE app_appextension_permissions
    ADD CONSTRAINT app_appextension_per_permission_id_cb6c3ce0_fk_auth_perm
    FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
    DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE app_appinstallation_permissions
    ADD CONSTRAINT app_appinstallation__permission_id_4ee9f6c8_fk_auth_perm
    FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
    DEFERRABLE INITIALLY DEFERRED;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0070_alter_user_uuid"),
        ("app", "0017_app_audience"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    migrations.RunSQL.noop,
                    reverse_sql=DROP_OLD_CONSTRAINTS_REVERSE_FROM_0072,
                ),
                migrations.RunSQL(
                    migrations.RunSQL.noop,
                    reverse_sql=DROP_OLD_CONSTRAINTS_REVERSE_FROM_APP_0018,
                ),
                migrations.RunPython(rename_group_tables, rename_group_tables_reverse),
                migrations.RunSQL(
                    RENAME_CONSTRAINTS_AND_INDEX,
                    reverse_sql=RENAME_CONSTRAINTS_AND_INDEX_REVERSE,
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="Group",
                    fields=[
                        (
                            "id",
                            models.AutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "name",
                            models.CharField(
                                max_length=150, unique=True, verbose_name="name"
                            ),
                        ),
                        (
                            "permissions",
                            models.ManyToManyField(
                                blank=True,
                                to="auth.Permission",
                                verbose_name="permissions",
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "group",
                        "verbose_name_plural": "groups",
                    },
                    managers=[
                        ("objects", saleor.account.models.GroupManager()),
                    ],
                ),
            ],
        ),
    ]
