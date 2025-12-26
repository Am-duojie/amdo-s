from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("admin_api", "0008_remove_audit_queue_item"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recycledevicetemplate",
            name="storages",
        ),
        migrations.RemoveField(
            model_name="recycledevicetemplate",
            name="ram_options",
        ),
        migrations.RemoveField(
            model_name="recycledevicetemplate",
            name="version_options",
        ),
        migrations.RemoveField(
            model_name="recycledevicetemplate",
            name="color_options",
        ),
    ]
