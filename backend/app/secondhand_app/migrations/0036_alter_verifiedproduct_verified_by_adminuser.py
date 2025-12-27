from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0011_remove_template_defaults'),
        ('secondhand_app', '0035_platformrecipient'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE secondhand_app_verifiedproduct SET verified_by_id = NULL",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='verifiedproduct',
            name='verified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='verified_products_verified',
                to='admin_api.adminuser',
                verbose_name='验货人',
            ),
        ),
    ]
