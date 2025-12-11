from django.db import migrations, connection


def relax_message_status(apps, schema_editor):
    """
    某些历史表结构可能在 message 表遗留了非空且无默认的 status 列，导致插入失败。
    若存在该列，则改为可为空，默认 NULL。
    """
    table_name = 'secondhand_app_message'
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = %s AND column_name = 'status'
            """,
            [table_name],
        )
        row = cursor.fetchone()
        if row:
            # 仅在存在该列时调整为可空
            cursor.execute(
                "ALTER TABLE secondhand_app_message MODIFY status varchar(50) NULL DEFAULT NULL;"
            )


class Migration(migrations.Migration):
    dependencies = [
        ('secondhand_app', '0016_ensure_message_extra_fields'),
    ]

    operations = [
        migrations.RunPython(relax_message_status, reverse_code=migrations.RunPython.noop),
    ]




