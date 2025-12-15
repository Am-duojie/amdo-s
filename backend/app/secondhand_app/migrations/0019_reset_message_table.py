from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('secondhand_app', '0018_fix_message_updated_at'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS secondhand_app_message;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True, verbose_name='消息内容')),
                ('message_type', models.CharField(choices=[('text', '文本'), ('product', '商品'), ('recall', '撤回'), ('system', '系统')], default='text', max_length=20, verbose_name='消息类型')),
                ('payload', models.JSONField(blank=True, null=True, verbose_name='扩展数据')),
                ('is_read', models.BooleanField(default=False, verbose_name='已读')),
                ('recalled', models.BooleanField(default=False, verbose_name='是否撤回')),
                ('recallable_until', models.DateTimeField(blank=True, null=True, verbose_name='可撤回截止时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='发送时间')),
                ('updated_at', models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='更新时间')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='secondhand_app.product', verbose_name='关联商品')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL, verbose_name='接收者')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL, verbose_name='发送者')),
            ],
            options={
                'verbose_name': '消息',
                'verbose_name_plural': '消息',
                'ordering': ['-created_at'],
            },
        ),
    ]




























