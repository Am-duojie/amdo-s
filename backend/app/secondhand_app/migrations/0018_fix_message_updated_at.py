from django.db import migrations, connection


def relax_updated_at(apps, schema_editor):
    """
    部分 MySQL 表可能遗留 updated_at 非空无默认，导致插入失败。
    将其改为可为空并允许自动更新。
    """
    table_name = 'secondhand_app_message'
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = %s AND column_name = 'updated_at'
            """,
            [table_name],
        )
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "ALTER TABLE secondhand_app_message MODIFY updated_at DATETIME(6) NULL DEFAULT NULL;"
            )


class Migration(migrations.Migration):
    dependencies = [
        ('secondhand_app', '0017_fix_message_status_column'),
    ]

    operations = [
        migrations.RunPython(relax_updated_at, reverse_code=migrations.RunPython.noop),
    ]








