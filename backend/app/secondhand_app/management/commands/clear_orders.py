from django.core.management.base import BaseCommand
from django.db import transaction
from app.secondhand_app.models import Order, VerifiedOrder, RecycleOrder
from app.admin_api.models import AdminAuditLog

class Command(BaseCommand):
    help = 'Clear all order-related data'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        yes = options.get('yes', False)
        dry = options.get('dry_run', False)
        if not yes and not dry:
            self.stdout.write('Use --yes to confirm or --dry-run to preview')
            return
        with transaction.atomic():
            count_orders = Order.objects.count()
            count_vorders = VerifiedOrder.objects.count()
            count_rorders = RecycleOrder.objects.count()
            count_audit = AdminAuditLog.objects.filter(target_type__in=['Order','VerifiedOrder','RecycleOrder','Payment','Settlement']).count()
            self.stdout.write(f'Orders: {count_orders}, VerifiedOrders: {count_vorders}, RecycleOrders: {count_rorders}, AdminAuditLogs: {count_audit}')
            if dry:
                return
            AdminAuditLog.objects.filter(target_type__in=['Order','VerifiedOrder','RecycleOrder','Payment','Settlement']).delete()
            VerifiedOrder.objects.all().delete()
            Order.objects.all().delete()
            RecycleOrder.objects.all().delete()
            self.stdout.write('Cleared')
