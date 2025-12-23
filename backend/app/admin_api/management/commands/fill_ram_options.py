"""
为所有回收机型模板补齐常用 RAM 选项（ram_options）。

默认只做 dry-run；传入 --yes 才会写入数据库。
"""

from django.core.management.base import BaseCommand

from app.admin_api.models import RecycleDeviceTemplate


DEFAULT_RAM_OPTIONS = [
    "2GB",
    "3GB",
    "4GB",
    "6GB",
    "8GB",
    "12GB",
    "16GB",
    "24GB",
    "32GB",
    "64GB",
]


def _normalize_option(value: str) -> str:
    return str(value or "").strip().lower()


class Command(BaseCommand):
    help = "Fill common RAM options into all RecycleDeviceTemplate.ram_options"

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Apply changes (write to DB). Without this flag, runs in dry-run mode.",
        )
        parser.add_argument(
            "--only-empty",
            action="store_true",
            help="Only update templates whose ram_options is empty.",
        )

    def handle(self, *args, **options):
        apply_changes = bool(options.get("yes"))
        only_empty = bool(options.get("only_empty"))

        qs = RecycleDeviceTemplate.objects.all().order_by("device_type", "brand", "model")
        total = qs.count()

        changed = 0
        skipped = 0

        for t in qs.iterator():
            current = list(getattr(t, "ram_options", None) or [])
            if only_empty and current:
                skipped += 1
                continue

            seen = {_normalize_option(x) for x in current if _normalize_option(x)}
            merged = list(current)
            for opt in DEFAULT_RAM_OPTIONS:
                key = _normalize_option(opt)
                if key and key not in seen:
                    merged.append(opt)
                    seen.add(key)

            if merged == current:
                skipped += 1
                continue

            changed += 1
            if apply_changes:
                t.ram_options = merged
                t.save(update_fields=["ram_options", "updated_at"])

        mode = "APPLIED" if apply_changes else "DRY-RUN"
        self.stdout.write(
            self.style.SUCCESS(
                f"[{mode}] templates_total={total} changed={changed} skipped={skipped}"
            )
        )
