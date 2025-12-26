from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F

from app.admin_api.models import RecycleDeviceTemplate, RecycleQuestionOption, RecycleQuestionTemplate


DEFAULT_RAM_OPTIONS: List[str] = [
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


QUESTION_SPECS: Dict[str, Dict] = {
    "channel": {
        "step_order": 1,
        "title": "购买渠道",
        "helper": "官方直营/运营商/第三方等",
        "question_type": "single",
        "is_required": True,
    },
    "color": {
        "step_order": 2,
        "title": "颜色",
        "helper": "",
        "question_type": "single",
        "is_required": True,
    },
    "storage": {
        "step_order": 3,
        "title": "存储容量",
        "helper": "选择存储容量以便精准估价",
        "question_type": "single",
        "is_required": True,
    },
    "ram": {
        "step_order": 4,
        "title": "运行内存",
        "helper": "必选：用于区分配置（不影响存储容量选择）",
        "question_type": "single",
        "is_required": True,
    },
    "usage": {"step_order": 5, "title": "使用情况", "helper": "", "question_type": "single", "is_required": True},
    "accessories": {"step_order": 6, "title": "有无配件", "helper": "", "question_type": "single", "is_required": True},
    "screen_appearance": {"step_order": 7, "title": "屏幕外观", "helper": "", "question_type": "single", "is_required": True},
    "body": {"step_order": 8, "title": "机身外壳", "helper": "", "question_type": "single", "is_required": True},
    "display": {"step_order": 9, "title": "屏幕显示", "helper": "", "question_type": "single", "is_required": True},
    "front_camera": {"step_order": 10, "title": "前摄拍照", "helper": "", "question_type": "single", "is_required": True},
    "rear_camera": {"step_order": 11, "title": "后摄拍照", "helper": "", "question_type": "single", "is_required": True},
    "repair": {"step_order": 12, "title": "维修情况（机身）", "helper": "", "question_type": "single", "is_required": True},
    "screen_repair": {"step_order": 13, "title": "屏幕维修情况", "helper": "", "question_type": "single", "is_required": True},
    "functional": {
        "step_order": 14,
        "title": "功能性问题（非必选，可多选）",
        "helper": "",
        "question_type": "multi",
        "is_required": False,
    },
}


def _normalize_option(value: str) -> str:
    return str(value or "").strip().lower()


@dataclass
class Stats:
    templates: int = 0
    questions_created: int = 0
    questions_updated: int = 0
    storage_options_cleared: int = 0
    ram_options_replaced: int = 0


class Command(BaseCommand):
    help = "Sync the RAM question (step 4) and normalize step orders/titles for all recycle templates."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = bool(options.get("dry_run"))
        stats = Stats()

        templates = list(RecycleDeviceTemplate.objects.all())
        stats.templates = len(templates)

        for t in templates:
            # step_order 在 (device_template, step_order) 上有唯一约束。
            # 先整体平移到临时区间，避免插入/调整过程中出现重复 step_order 冲突。
            if not dry_run:
                RecycleQuestionTemplate.objects.filter(device_template=t).update(step_order=F("step_order") + 100)

            for key, spec in QUESTION_SPECS.items():
                q = RecycleQuestionTemplate.objects.filter(device_template=t, key=key).first()
                if q is None:
                    if dry_run:
                        stats.questions_created += 1
                        continue
                    q = RecycleQuestionTemplate.objects.create(
                        device_template=t,
                        step_order=spec["step_order"],
                        key=key,
                        title=spec["title"],
                        helper=spec.get("helper", "") or "",
                        question_type=spec["question_type"],
                        is_required=spec["is_required"],
                        is_active=True,
                    )
                    stats.questions_created += 1
                else:
                    changed = False
                    if q.step_order != spec["step_order"]:
                        q.step_order = spec["step_order"]
                        changed = True
                    if (q.title or "") != spec["title"]:
                        q.title = spec["title"]
                        changed = True
                    if (q.helper or "") != (spec.get("helper", "") or ""):
                        q.helper = spec.get("helper", "") or ""
                        changed = True
                    if q.question_type != spec["question_type"]:
                        q.question_type = spec["question_type"]
                        changed = True
                    if q.is_required != spec["is_required"]:
                        q.is_required = spec["is_required"]
                        changed = True
                    if q.is_active is not True:
                        q.is_active = True
                        changed = True
                    if changed:
                        if dry_run:
                            stats.questions_updated += 1
                        else:
                            q.save()
                            stats.questions_updated += 1

                if q is None:
                    continue

                if key == "storage":
                    if dry_run:
                        stats.storage_options_cleared += 1
                    else:
                        RecycleQuestionOption.objects.filter(question_template=q).delete()
                        stats.storage_options_cleared += 1

                if key == "ram":
                    ram_options = DEFAULT_RAM_OPTIONS

                    merged: List[str] = []
                    seen = set()
                    for opt in ram_options:
                        norm = _normalize_option(opt)
                        if not norm or norm in seen:
                            continue
                        merged.append(str(opt).strip())
                        seen.add(norm)

                    if dry_run:
                        stats.ram_options_replaced += 1
                    else:
                        RecycleQuestionOption.objects.filter(question_template=q).delete()
                        for idx, opt in enumerate(merged):
                            RecycleQuestionOption.objects.create(
                                question_template=q,
                                value=opt,
                                label=opt,
                                desc="",
                                impact="",
                                option_order=idx,
                                is_active=True,
                            )
                        stats.ram_options_replaced += 1

        prefix = "[dry-run] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}templates={stats.templates} questions_created={stats.questions_created} "
                f"questions_updated={stats.questions_updated} storage_options_cleared={stats.storage_options_cleared} "
                f"ram_options_replaced={stats.ram_options_replaced}"
            )
        )
