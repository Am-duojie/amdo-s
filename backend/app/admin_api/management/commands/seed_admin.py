from django.core.management.base import BaseCommand
from app.admin_api.models import AdminRole, AdminUser
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Seed admin roles and a default admin user'

    def handle(self, *args, **options):
        super_role, created_super = AdminRole.objects.get_or_create(name='super', defaults={'description': 'all', 'permissions': [
            'dashboard:view',
            'inspection:view','inspection:write','inspection:payment',
            'recycled:view','recycled:write',
            'verified:view','verified:write',
            'audit_log:view',
            'admin_user:view','admin_user:write','admin_user:delete',
            'role:view','role:write',
            'payment:view','payment:write',
            'order:ship',
            'category:view','category:write','category:delete',
            'product:view','product:write','product:delete',
            'user:view','user:write','user:delete',
            'message:view','message:delete',
            'address:view','address:delete'
        ]})
        if not created_super:
            super_role.description = super_role.description or 'all'
            super_role.permissions = super_role.permissions or []
            required = set([
                'dashboard:view',
                'inspection:view','inspection:write','inspection:payment',
                'recycled:view','recycled:write',
                'verified:view','verified:write',
                'audit_log:view',
                'admin_user:view','admin_user:write','admin_user:delete',
                'role:view','role:write',
                'payment:view','payment:write',
                'order:ship',
                'category:view','category:write','category:delete',
                'product:view','product:write','product:delete',
                'user:view','user:write','user:delete',
                'message:view','message:delete',
                'address:view','address:delete'
            ])
            super_role.permissions = list(sorted(set(super_role.permissions) | required))
            super_role.save()
        auditor_role, _ = AdminRole.objects.get_or_create(name='auditor', defaults={'description': 'read'})
        admin_user, created = AdminUser.objects.get_or_create(
            username='admin',
            defaults={'role': super_role, 'email': 'admin@example.com', 'password_hash': make_password('admin')}
        )
        if not created:
            admin_user.role = super_role
            admin_user.email = admin_user.email or 'admin@example.com'
            admin_user.password_hash = make_password('admin')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Reset default admin user password (username=admin, password=admin)'))
        else:
            self.stdout.write(self.style.SUCCESS('Created default admin user (username=admin, password=admin)'))
