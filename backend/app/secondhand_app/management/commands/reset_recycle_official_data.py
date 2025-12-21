from __future__ import annotations

from pathlib import Path
from typing import Dict

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from app.admin_api.models import (
    AdminAuditLog,
    AdminAuditQueueItem,
    AdminInspectionReport,
    RecycleDeviceTemplate,
    RecycleQuestionOption,
    RecycleQuestionTemplate,
)
from app.secondhand_app.models import (
    RecycleOrder,
    VerifiedDevice,
    VerifiedFavorite,
    VerifiedOrder,
    VerifiedProduct,
    VerifiedProductImage,
)


class Command(BaseCommand):
    help = "Reset recycle + official-verified datasets (dangerous)."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="Confirm destructive deletion.")
        parser.add_argument("--dry-run", action="store_true", help="Preview counts, do not delete.")
        parser.add_argument(
            "--templates-file",
            type=str,
            default="",
            help="If set, clears existing templates and imports this JSON via import_recycle_templates_json.",
        )
        parser.add_argument(
            "--keep-templates",
            action="store_true",
            help="Do not touch templates (default is to clear+import when --templates-file is set).",
        )
        parser.add_argument(
            "--seed-recycle-count",
            type=int,
            default=0,
            help="Optionally re-seed recycle orders after reset (0 disables).",
        )
        parser.add_argument("--seed-days", type=int, default=60, help="Seed created_at over last N days.")
        parser.add_argument("--seed-tag", type=str, default="FAKE_RECYCLE", help="Tag written into seeded orders note.")

    def _counts(self) -> Dict[str, int]:
        return {
            "AdminInspectionReport": AdminInspectionReport.objects.count(),
            "RecycleOrder": RecycleOrder.objects.count(),
            "VerifiedDevice": VerifiedDevice.objects.count(),
            "VerifiedProduct": VerifiedProduct.objects.count(),
            "VerifiedProductImage": VerifiedProductImage.objects.count(),
            "VerifiedFavorite": VerifiedFavorite.objects.count(),
            "VerifiedOrder": VerifiedOrder.objects.count(),
            "AdminAuditQueueItem": AdminAuditQueueItem.objects.count(),
            "AdminAuditLog(recycle/verified)": AdminAuditLog.objects.filter(
                target_type__in=["RecycleOrder", "VerifiedOrder", "VerifiedProduct", "VerifiedDevice", "Payment", "Settlement"]
            ).count(),
            "RecycleDeviceTemplate": RecycleDeviceTemplate.objects.count(),
            "RecycleQuestionTemplate": RecycleQuestionTemplate.objects.count(),
            "RecycleQuestionOption": RecycleQuestionOption.objects.count(),
        }

    @transaction.atomic
    def handle(self, *args, **options):
        yes = bool(options.get("yes"))
        dry_run = bool(options.get("dry_run"))
        templates_file = (options.get("templates_file") or "").strip()
        keep_templates = bool(options.get("keep_templates"))
        seed_recycle_count = int(options.get("seed_recycle_count") or 0)
        seed_days = int(options.get("seed_days") or 60)
        seed_tag = str(options.get("seed_tag") or "FAKE_RECYCLE")

        if not dry_run and not yes:
            self.stdout.write("Use --dry-run to preview or --yes to confirm.")
            return

        counts = self._counts()
        self.stdout.write("=== Current counts ===")
        for k, v in counts.items():
            self.stdout.write(f"- {k}: {v}")

        if dry_run:
            self.stdout.write(self.style.WARNING("[dry-run] no data deleted."))
            if templates_file:
                self.stdout.write(self.style.WARNING(f"[dry-run] would import templates from: {templates_file}"))
            if seed_recycle_count > 0:
                self.stdout.write(self.style.WARNING(f"[dry-run] would seed recycle orders: {seed_recycle_count}"))
            return

        # Delete official-verified data first (dependents -> owners)
        AdminAuditQueueItem.objects.all().delete()
        VerifiedFavorite.objects.all().delete()
        VerifiedProductImage.objects.all().delete()
        VerifiedOrder.objects.all().delete()
        VerifiedDevice.objects.all().delete()
        VerifiedProduct.objects.all().delete()

        # Delete recycle data (reports -> orders)
        AdminInspectionReport.objects.all().delete()
        RecycleOrder.objects.all().delete()

        # Delete audit logs referencing these datasets
        AdminAuditLog.objects.filter(
            target_type__in=["RecycleOrder", "VerifiedOrder", "VerifiedProduct", "VerifiedDevice", "Payment", "Settlement"]
        ).delete()

        # Templates: clear and import (optional)
        if templates_file and not keep_templates:
            p = Path(templates_file)
            if not p.exists():
                raise SystemExit(f"templates file not found: {p}")

            RecycleQuestionOption.objects.all().delete()
            RecycleQuestionTemplate.objects.all().delete()
            RecycleDeviceTemplate.objects.all().delete()

            call_command(
                "import_recycle_templates_json",
                file=str(p),
                ensure_questions=True,
            )

        # Optional: re-seed recycle orders for BI demos
        if seed_recycle_count > 0:
            call_command(
                "seed_recycle_orders",
                count=seed_recycle_count,
                days=seed_days,
                tag=seed_tag,
            )

        self.stdout.write(self.style.SUCCESS("Reset completed."))
