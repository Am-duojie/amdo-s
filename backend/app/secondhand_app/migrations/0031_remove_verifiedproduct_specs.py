from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("secondhand_app", "0030_remove_recycleorder_contact_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="verifiedproduct",
            name="screen_size",
        ),
        migrations.RemoveField(
            model_name="verifiedproduct",
            name="charging_type",
        ),
    ]
