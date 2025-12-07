from django.core.management.base import BaseCommand
from app.admin_api.models import AdminUser
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = '重置用户密码（支持管理员用户和前端用户）'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='要重置密码的用户名',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='123456',
            help='新密码（默认为 123456）',
        )
        parser.add_argument(
            '--admin',
            action='store_true',
            help='重置管理员用户密码（AdminUser）',
        )

    def handle(self, *args, **options):
        username = options['username']
        new_password = options['password']
        is_admin = options['admin']

        if is_admin:
            # 重置管理员用户密码
            try:
                admin_user = AdminUser.objects.get(username=username)
                admin_user.password_hash = make_password(new_password)
                admin_user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ 成功重置管理员用户 "{username}" 的密码为: {new_password}'
                    )
                )
            except AdminUser.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ 管理员用户 "{username}" 不存在')
                )
        else:
            # 重置前端用户密码（Django User）
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ 成功重置前端用户 "{username}" 的密码为: {new_password}'
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ 前端用户 "{username}" 不存在')
                )
                # 尝试查找管理员用户
                try:
                    admin_user = AdminUser.objects.get(username=username)
                    self.stdout.write(
                        self.style.WARNING(
                            f'提示: 找到了管理员用户 "{username}"，请使用 --admin 参数重置密码'
                        )
                    )
                except AdminUser.DoesNotExist:
                    pass





