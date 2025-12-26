from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('admin_api', '0010_set_option_value_from_label'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recycledevicetemplate',
            name='default_cover_image',
        ),
        migrations.RemoveField(
            model_name='recycledevicetemplate',
            name='default_detail_images',
        ),
        migrations.RemoveField(
            model_name='recycledevicetemplate',
            name='description_template',
        ),
    ]
