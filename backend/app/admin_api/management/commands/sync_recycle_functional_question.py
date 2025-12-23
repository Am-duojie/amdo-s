from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction

from app.admin_api.models import RecycleDeviceTemplate, RecycleQuestionOption, RecycleQuestionTemplate


FUNCTIONAL_OPTIONS: List[Tuple[str, str, str]] = [
    ("all_ok", "全部正常", "positive"),
    ("touch_issue", "触摸失灵/延迟", "critical"),
    ("vibration_flash_issue", "振动/闪光灯异常", "major"),
    ("biometric_issue", "指纹/面部识别异常", "major"),
    ("audio_issue", "听筒/麦克风/扬声器异常", "major"),
    ("sensor_issue", "重力/指南针等感应器异常", "minor"),
    ("wifi_baseband_issue", "WIFI异常/信号异常/不读卡/无基带", "critical"),
    ("nfc_transit_issue", "NFC异常/公交卡无法退出", "major"),
    ("button_issue", "按键无反馈/失灵", "major"),
    ("light_distance_sensor_issue", "光线、距离感应器异常", "minor"),
    ("cannot_charge", "无法充电", "critical"),
    ("water_damage", "机身进水", "critical"),
]


@dataclass
class Stats:
    templates: int = 0
    questions_created: int = 0
    questions_updated: int = 0
    options_replaced: int = 0


class Command(BaseCommand):
    help = "Sync the shared 'functional' question (step 14) for all recycle device templates."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = bool(options.get("dry_run"))
        stats = Stats()

        templates = list(RecycleDeviceTemplate.objects.all())
        stats.templates = len(templates)

        for t in templates:
            q = RecycleQuestionTemplate.objects.filter(device_template=t, key="functional").first()
            if q is None:
                if dry_run:
                    stats.questions_created += 1
                else:
                    q = RecycleQuestionTemplate.objects.create(
                        device_template=t,
                        step_order=14,
                        key="functional",
                        title="功能性问题（非必选，可多选）",
                        helper="",
                        question_type="multi",
                        is_required=False,
                        is_active=True,
                    )
                    stats.questions_created += 1
            else:
                changed = False
                if q.step_order != 14:
                    q.step_order = 14
                    changed = True
                if q.title != "功能性问题（非必选，可多选）":
                    q.title = "功能性问题（非必选，可多选）"
                    changed = True
                if (q.helper or "") != "":
                    q.helper = ""
                    changed = True
                if q.question_type != "multi":
                    q.question_type = "multi"
                    changed = True
                if q.is_required is not False:
                    q.is_required = False
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

            if dry_run:
                stats.options_replaced += 1
                continue

            RecycleQuestionOption.objects.filter(question_template=q).delete()
            for idx, (value, label, impact) in enumerate(FUNCTIONAL_OPTIONS):
                RecycleQuestionOption.objects.create(
                    question_template=q,
                    value=value,
                    label=label,
                    desc=("未发现功能异常" if value == "all_ok" else ""),
                    impact=impact,
                    option_order=idx,
                    is_active=True,
                )
            stats.options_replaced += 1

        prefix = "[dry-run] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}templates={stats.templates} questions_created={stats.questions_created} "
                f"questions_updated={stats.questions_updated} options_replaced={stats.options_replaced}"
            )
        )
