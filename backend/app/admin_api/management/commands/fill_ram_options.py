"""
为回收问卷中的 RAM 问题补齐常用选项。

默认只做 dry-run；传入 --yes 才会写入数据库。
"""

from django.core.management.base import BaseCommand

from app.admin_api.models import RecycleQuestionOption, RecycleQuestionTemplate


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
    help = "Fill common RAM options into recycle question templates (key=ram)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Apply changes (write to DB). Without this flag, runs in dry-run mode.",
        )
        parser.add_argument(
            "--only-empty",
            action="store_true",
            help="Only update questions that currently have no options.",
        )

    def handle(self, *args, **options):
        apply_changes = bool(options.get("yes"))
        only_empty = bool(options.get("only_empty"))

        qs = RecycleQuestionTemplate.objects.filter(key="ram").order_by("device_template_id", "step_order")
        total = qs.count()

        changed = 0
        skipped = 0

        for q in qs.iterator():
            current = list(q.options.values_list("label", flat=True))
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
                RecycleQuestionOption.objects.filter(question_template=q).delete()
                for idx, label in enumerate(merged):
                    RecycleQuestionOption.objects.create(
                        question_template=q,
                        value=str(label).strip(),
                        label=str(label).strip(),
                        desc="",
                        impact="",
                        option_order=idx,
                        is_active=True,
                    )

        mode = "APPLIED" if apply_changes else "DRY-RUN"
        self.stdout.write(
            self.style.SUCCESS(
                f"[{mode}] templates_total={total} changed={changed} skipped={skipped}"
            )
        )
