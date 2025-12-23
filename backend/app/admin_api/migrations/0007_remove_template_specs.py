from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("admin_api", "0006_add_template_relations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recycledevicetemplate",
            name="screen_size",
        ),
        migrations.RemoveField(
            model_name="recycledevicetemplate",
            name="battery_capacity",
        ),
        migrations.RemoveField(
            model_name="recycledevicetemplate",
            name="charging_type",
        ),
    ]
