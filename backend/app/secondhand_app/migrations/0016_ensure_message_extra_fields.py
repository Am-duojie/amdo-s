from django.db import migrations, connection


def add_missing_columns(apps, schema_editor):
    """
    MySQL 旧版本不支持 IF NOT EXISTS，这里通过 information_schema 检查再动态添加。
    """
    table_name = 'secondhand_app_message'
    required = {
        'message_type': "ALTER TABLE secondhand_app_message ADD COLUMN message_type VARCHAR(20) NOT NULL DEFAULT 'text';",
        'payload': "ALTER TABLE secondhand_app_message ADD COLUMN payload JSON NULL;",
        'recallable_until': "ALTER TABLE secondhand_app_message ADD COLUMN recallable_until DATETIME(6) NULL;",
        'recalled': "ALTER TABLE secondhand_app_message ADD COLUMN recalled BOOL NOT NULL DEFAULT 0;",
    }

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = %s
            """,
            [table_name],
        )
        existing = {row[0] for row in cursor.fetchall()}

        for col, sql in required.items():
            if col not in existing:
                cursor.execute(sql)


class Migration(migrations.Migration):
    dependencies = [
        ('secondhand_app', '0015_message_message_type_message_payload_and_more'),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, reverse_code=migrations.RunPython.noop),
    ]

