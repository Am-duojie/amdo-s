from django.conf import settings
from django.db import migrations, models


def seed_platform_recipient(apps, schema_editor):
    PlatformRecipient = apps.get_model('secondhand_app', 'PlatformRecipient')
    if PlatformRecipient.objects.exists():
        return
    defaults = getattr(settings, 'PLATFORM_RECIPIENT_DEFAULT', {}) or {}
    PlatformRecipient.objects.create(
        name=defaults.get('name', ''),
        phone=defaults.get('phone', ''),
        address=defaults.get('address', '')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('secondhand_app', '0034_product_default_pending'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='收件人')),
                ('phone', models.CharField(max_length=32, verbose_name='电话')),
                ('address', models.TextField(verbose_name='地址')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '平台收件信息',
                'verbose_name_plural': '平台收件信息',
            },
        ),
        migrations.RunPython(seed_platform_recipient, migrations.RunPython.noop),
    ]
