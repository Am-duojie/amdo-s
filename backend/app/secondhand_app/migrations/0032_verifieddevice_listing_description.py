from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('secondhand_app', '0031_remove_verifiedproduct_specs'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifieddevice',
            name='listing_description',
            field=models.TextField(blank=True, default='', verbose_name='上架商品描述'),
        ),
    ]

