from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Delete all recycle orders data (RecycleOrder and related inspection reports)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Actually delete data (required).",
        )

    def handle(self, *args, **options):
        from app.secondhand_app.models import RecycleOrder
        from app.admin_api.models import AdminInspectionReport

        counts = {
            "RecycleOrder": RecycleOrder.objects.count(),
            "AdminInspectionReport(order=RecycleOrder)": AdminInspectionReport.objects.filter(order__isnull=False).count(),
        }

        self.stdout.write("Current recycle data counts:")
        for k, v in counts.items():
            self.stdout.write(f"- {k}: {v}")

        if not options["yes"]:
            self.stdout.write(self.style.WARNING("Dry run only. Re-run with --yes to delete."))
            return

        with transaction.atomic():
            AdminInspectionReport.objects.filter(order__isnull=False).delete()
            RecycleOrder.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("All recycle orders deleted."))

