# Generated migration file

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secondhand_app', '0022_simplify_recycle_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifiedproduct',
            name='ram',
            field=models.CharField(blank=True, max_length=20, verbose_name='运行内存'),
        ),
        migrations.AddField(
            model_name='verifiedproduct',
            name='version',
            field=models.CharField(blank=True, max_length=50, verbose_name='版本'),
        ),
        migrations.AddField(
            model_name='verifiedproduct',
            name='repair_status',
            field=models.CharField(blank=True, max_length=100, verbose_name='拆修和功能'),
        ),
    ]
