from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Delete all Official Verified inventory data (VerifiedProduct/VerifiedDevice and related rows)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Actually delete data (required).",
        )

    def handle(self, *args, **options):
        from app.secondhand_app.models import (
            VerifiedDevice,
            VerifiedFavorite,
            VerifiedOrder,
            VerifiedProduct,
            VerifiedProductImage,
        )

        counts = {
            "VerifiedProduct": VerifiedProduct.objects.count(),
            "VerifiedDevice": VerifiedDevice.objects.count(),
            "VerifiedProductImage": VerifiedProductImage.objects.count(),
            "VerifiedOrder": VerifiedOrder.objects.count(),
            "VerifiedFavorite": VerifiedFavorite.objects.count(),
        }

        self.stdout.write("Current verified data counts:")
        for k, v in counts.items():
            self.stdout.write(f"- {k}: {v}")

        if not options["yes"]:
            self.stdout.write(self.style.WARNING("Dry run only. Re-run with --yes to delete."))
            return

        with transaction.atomic():
            # Delete child tables first for clear audit/logs, although CASCADE would handle most.
            VerifiedFavorite.objects.all().delete()
            VerifiedOrder.objects.all().delete()
            VerifiedProductImage.objects.all().delete()
            VerifiedProduct.objects.all().delete()
            VerifiedDevice.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("All verified inventory data deleted."))
