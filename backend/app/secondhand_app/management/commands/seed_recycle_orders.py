from __future__ import annotations

import random
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection
from django.db import transaction
from django.utils import timezone

from app.admin_api.models import AdminInspectionReport, RecycleDeviceTemplate, RecycleQuestionOption, RecycleQuestionTemplate
from app.secondhand_app.models import RecycleOrder


CONDITION_MULTIPLIERS = {
    "new": 1.00,
    "like_new": 0.90,
    "good": 0.78,
    "fair": 0.62,
    "poor": 0.42,
}


STATUS_WEIGHTS = [
    ("pending", 6),
    ("shipped", 10),
    ("received", 10),
    ("inspected", 24),
    ("completed", 40),
    ("cancelled", 10),
]


def _weighted_choice(rng: random.Random, items: List[Tuple[str, int]]) -> str:
    total = sum(w for _, w in items)
    x = rng.uniform(0, total)
    acc = 0.0
    for value, weight in items:
        acc += weight
        if x <= acc:
            return value
    return items[-1][0]


def _rand_dt(rng: random.Random, days: int) -> timezone.datetime:
    now = timezone.now()
    delta = timedelta(seconds=rng.randint(0, max(1, days * 24 * 3600)))
    return now - delta


def _ensure_users(rng: random.Random, target: int) -> List[User]:
    users = list(User.objects.all()[: target])
    if len(users) >= target:
        return users

    created: List[User] = []
    for i in range(target - len(users)):
        # avoid collisions across multiple runs (even with fixed seed)
        from django.db.utils import IntegrityError

        u = None
        for _attempt in range(50):
            username = f"demo_user_{rng.randint(100000, 999999)}_{rng.randint(0, 9999)}"
            try:
                u = User.objects.create_user(username=username, password="123456")
                break
            except IntegrityError:
                continue
        if u is None:
            raise RuntimeError("Failed to create unique demo users; please retry with a different --seed.")
        created.append(u)
    return list(User.objects.all()[: target])


def _ensure_templates(rng: random.Random) -> None:
    if RecycleDeviceTemplate.objects.exists():
        return

    # Create a minimal template set (if repo was started without imports).
    base_templates = [
        ("手机", "苹果", "iPhone 13", ["128GB", "256GB", "512GB"], {"128GB": 3200, "256GB": 3900, "512GB": 5200}),
        ("手机", "华为", "Mate 60", ["256GB", "512GB"], {"256GB": 3800, "512GB": 4800}),
        ("手机", "小米", "小米13", ["128GB", "256GB", "512GB"], {"128GB": 1800, "256GB": 2400, "512GB": 3000}),
    ]
    for device_type, brand, model, storages, base_prices in base_templates:
        template = RecycleDeviceTemplate.objects.create(
            device_type=device_type,
            brand=brand,
            model=model,
            storages=storages,
            base_prices=base_prices,
            is_active=True,
        )

        questions = [
            ("storage", "存储容量", "single", True),
            ("usage", "使用情况", "single", True),
            ("repair", "维修情况", "single", True),
            ("screen_repair", "屏幕维修情况", "single", True),
            ("functional", "功能性问题（可多选）", "multi", False),
        ]
        for step_order, (key, title, qtype, required) in enumerate(questions, start=1):
            qt = RecycleQuestionTemplate.objects.create(
                device_template=template,
                step_order=step_order,
                key=key,
                title=title,
                question_type=qtype,
                is_required=required,
                is_active=True,
            )

            options: List[Tuple[str, str, str]] = []
            if key == "storage":
                for s in storages:
                    options.append((s, s, "positive"))
            elif key == "usage":
                options = [
                    ("unopened", "未拆封", "positive"),
                    ("light", "轻度使用", "minor"),
                    ("heavy", "重度使用", "major"),
                ]
            elif key == "repair":
                options = [
                    ("none", "无拆修", "positive"),
                    ("battery", "维修或更换电池", "major"),
                    ("board", "主板维修/进水", "critical"),
                ]
            elif key == "screen_repair":
                options = [
                    ("none", "无拆修", "positive"),
                    ("glass", "更换外层玻璃", "minor"),
                    ("assembly", "屏幕总成维修/更换", "major"),
                ]
            elif key == "functional":
                options = [
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

            for idx, (value, label, impact) in enumerate(options, start=1):
                RecycleQuestionOption.objects.create(
                    question_template=qt,
                    value=value,
                    label=label,
                    impact=impact,
                    option_order=idx,
                    is_active=True,
                )


def _pick_template(rng: random.Random) -> RecycleDeviceTemplate:
    templates = list(RecycleDeviceTemplate.objects.filter(is_active=True))
    return rng.choice(templates)


def _pick_storage(rng: random.Random, template: RecycleDeviceTemplate) -> str:
    storages = template.storages or []
    if not storages:
        return "128GB"
    return rng.choice(storages)


def _pick_condition(rng: random.Random) -> str:
    return _weighted_choice(
        rng,
        [
            ("new", 8),
            ("like_new", 16),
            ("good", 40),
            ("fair", 26),
            ("poor", 10),
        ],
    )


def _build_questionnaire_answers(
    rng: random.Random, template: RecycleDeviceTemplate, storage: str
) -> Dict[str, Any]:
    answers: Dict[str, Any] = {}
    questions = list(RecycleQuestionTemplate.objects.filter(device_template=template, is_active=True).order_by("step_order"))
    for q in questions:
        opts = list(RecycleQuestionOption.objects.filter(question_template=q, is_active=True).order_by("option_order", "id"))
        if not opts:
            continue

        if q.key == "storage":
            match = next((o for o in opts if o.value == storage), None)
            chosen = match or rng.choice(opts)
            answers[q.key] = {"value": chosen.value, "label": chosen.label, "impact": chosen.impact or ""}
            continue

        if q.question_type == "multi":
            # mostly 0~2 problems; exclusive "all_ok"/"none" dominates
            exclusive_value = "all_ok" if q.key == "functional" else "none"
            if rng.random() < 0.65:
                none = next((o for o in opts if o.value == exclusive_value), None)
                if none:
                    answers[q.key] = [{"value": none.value, "label": none.label, "impact": none.impact or ""}]
                continue
            k = rng.randint(1, 2)
            chosen_list = rng.sample(
                [o for o in opts if o.value != exclusive_value],
                k=min(k, max(1, len(opts) - 1)),
            )
            answers[q.key] = [{"value": o.value, "label": o.label, "impact": o.impact or ""} for o in chosen_list]
        else:
            chosen = rng.choice(opts)
            answers[q.key] = {"value": chosen.value, "label": chosen.label, "impact": chosen.impact or ""}

    return answers


def _impact_counts(questionnaire_answers: Dict[str, Any]) -> Dict[str, int]:
    counts = {"positive": 0, "minor": 0, "major": 0, "critical": 0, "unknown": 0}

    def consume_one(item: Any) -> None:
        if not isinstance(item, dict):
            counts["unknown"] += 1
            return
        impact = (item.get("impact") or "").strip()
        if impact in counts:
            counts[impact] += 1
        else:
            counts["unknown"] += 1

    for _k, v in (questionnaire_answers or {}).items():
        if v is None:
            continue
        if isinstance(v, list):
            for item in v:
                consume_one(item)
        else:
            consume_one(v)
    return counts


def _estimate_price(
    base_price: float, condition: str, impact_counts: Dict[str, int], rng: random.Random
) -> float:
    price = base_price * CONDITION_MULTIPLIERS.get(condition, 0.78)
    penalty = (
        0.02 * impact_counts.get("minor", 0)
        + 0.05 * impact_counts.get("major", 0)
        + 0.10 * impact_counts.get("critical", 0)
    )
    price = price * max(0.35, 1.0 - penalty)
    price = price * rng.uniform(0.96, 1.04)
    return float(f"{max(0.0, price):.2f}")


def _build_check_items(rng: random.Random, impact_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    base_fail = 0.04 + 0.03 * min(impact_counts.get("minor", 0), 3)
    base_fail += 0.06 * min(impact_counts.get("major", 0), 2)
    base_fail += 0.10 * min(impact_counts.get("critical", 0), 2)
    base_fail = max(0.02, min(0.55, base_fail))

    items: List[Dict[str, Any]] = []
    for i in range(66):
        fail = rng.random() < base_fail
        items.append({"label": f"item_{i+1}", "pass": (not fail)})
    return items


def _calc_fail_rate(check_items: List[Dict[str, Any]]) -> float:
    total = 0
    fail = 0
    for it in check_items:
        if not isinstance(it, dict):
            continue
        p = it.get("pass")
        if p is True:
            total += 1
            continue
        if p is False:
            total += 1
            fail += 1
    return (fail / total) if total else 0.0


def _retime_orders_by_tag(tag: str, days: int) -> int:
    """
    MySQL-specific retime:
    - created_at/updated_at are auto_now(_add) fields and are often overwritten during bulk_create.
    - We retime them based on shipped_at (when exists) to create a realistic timeline for BI demos.
    """
    table = RecycleOrder._meta.db_table
    like = f"%{tag}%"
    seconds = max(1, int(days) * 24 * 3600)

    # 1) created_at: if shipped_at exists, backdate 1~4 days before shipped_at; else random within last N days.
    # 2) updated_at: set to the latest milestone timestamp.
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE `{table}`
            SET created_at =
              CASE
                WHEN shipped_at IS NOT NULL THEN DATE_SUB(shipped_at, INTERVAL (1 + FLOOR(RAND() * 4)) DAY)
                ELSE DATE_SUB(NOW(6), INTERVAL FLOOR(RAND() * %s) SECOND)
              END
            WHERE note LIKE %s
            """,
            [seconds, like],
        )
        affected1 = cursor.rowcount

        cursor.execute(
            f"""
            UPDATE `{table}`
            SET updated_at = GREATEST(
              created_at,
              COALESCE(shipped_at, created_at),
              COALESCE(received_at, created_at),
              COALESCE(inspected_at, created_at),
              COALESCE(paid_at, created_at)
            )
            WHERE note LIKE %s
            """,
            [like],
        )
        affected2 = cursor.rowcount

    return min(affected1, affected2) if affected1 >= 0 and affected2 >= 0 else 0


class Command(BaseCommand):
    help = "Generate realistic-ish recycle orders + inspection reports for demo/analysis."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000, help="How many orders to create.")
        parser.add_argument("--days", type=int, default=60, help="Spread created_at over last N days.")
        parser.add_argument("--seed", type=int, default=20251218, help="Random seed for reproducibility.")
        parser.add_argument("--tag", type=str, default="FAKE_RECYCLE", help="Tag written into note to identify fake data.")
        parser.add_argument("--ensure-templates", action="store_true", help="Create a minimal template set if none exists.")
        parser.add_argument("--delete-by-tag", action="store_true", help="Delete orders whose note contains the tag (and their reports).")
        parser.add_argument("--retime-by-tag", action="store_true", help="Adjust created_at/updated_at for orders whose note contains the tag (useful for BI trend demos).")

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(int(options["seed"]))
        tag = str(options["tag"]).strip() or "FAKE_RECYCLE"

        if options["delete_by_tag"]:
            qs = RecycleOrder.objects.filter(note__icontains=tag)
            order_ids = list(qs.values_list("id", flat=True))
            AdminInspectionReport.objects.filter(order_id__in=order_ids).delete()
            deleted, _ = qs.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} recycle orders (tag={tag})."))
            return

        if options["retime_by_tag"]:
            affected = _retime_orders_by_tag(tag=tag, days=int(options["days"]))
            self.stdout.write(self.style.SUCCESS(f"Retimed {affected} recycle orders (tag={tag})."))
            return

        if options["ensure_templates"]:
            _ensure_templates(rng)

        if not RecycleDeviceTemplate.objects.filter(is_active=True).exists():
            raise RuntimeError("No active recycle templates found. Run with --ensure-templates or import templates first.")

        users = _ensure_users(rng, target=20)

        count = int(options["count"])
        days = int(options["days"])
        now = timezone.now()

        created_orders: List[RecycleOrder] = []
        report_payloads: List[Tuple[int, Dict[str, Any], timezone.datetime]] = []

        for i in range(count):
            template = _pick_template(rng)
            storage = _pick_storage(rng, template)
            condition = _pick_condition(rng)
            created_at = _rand_dt(rng, days)
            status = _weighted_choice(rng, STATUS_WEIGHTS)
            user = rng.choice(users)

            base_price = float((template.base_prices or {}).get(storage) or rng.randint(1500, 6500))
            answers = _build_questionnaire_answers(rng, template, storage)
            impacts = _impact_counts(answers)
            estimated_price = _estimate_price(base_price, condition, impacts, rng)

            # inspection report & final price simulation
            check_items = _build_check_items(rng, impacts)
            fail_rate = _calc_fail_rate(check_items)
            final_price = float(f"{estimated_price * (1.0 - 0.22 * fail_rate) * rng.uniform(0.95, 1.03):.2f}")
            bonus = float(f"{(rng.choice([0, 0, 0, 10, 20, 50, 80]) if status != 'cancelled' else 0):.2f}")

            # timeline stamps
            shipped_at = None
            received_at = None
            inspected_at = None
            paid_at = None

            if status in ["shipped", "received", "inspected", "completed"]:
                shipped_at = min(now, created_at + timedelta(days=rng.randint(1, 4)))
            if status in ["received", "inspected", "completed"]:
                received_at = min(now, (shipped_at or created_at) + timedelta(days=rng.randint(1, 4)))
            if status in ["inspected", "completed"]:
                inspected_at = min(now, (received_at or shipped_at or created_at) + timedelta(days=rng.randint(0, 2)))
            if status == "completed":
                paid_at = min(now, (inspected_at or received_at or shipped_at or created_at) + timedelta(days=rng.randint(1, 5)))

            # confirmation & payment status
            final_price_confirmed = (status == "completed" and rng.random() < 0.85)
            payment_status = "pending"
            if status == "completed" and final_price_confirmed:
                payment_status = _weighted_choice(rng, [("paid", 75), ("pending", 20), ("failed", 5)])
            if payment_status != "paid":
                paid_at = None

            # dispute (only after inspected and before confirmed/paid)
            price_dispute = False
            price_dispute_reason = ""
            if status in ["inspected", "completed"] and not final_price_confirmed and rng.random() < (0.05 + 0.10 * min(impacts.get("critical", 0), 2)):
                price_dispute = True
                price_dispute_reason = "对质检结果与最终价格不认可，申请复核"

            # cancelled
            reject_reason = ""
            if status == "cancelled":
                reject_reason = rng.choice(["用户改约", "信息填错", "不想寄出", "价格不满意", "重复下单"])
                payment_status = "pending"
                final_price_confirmed = False
                paid_at = None

            order = RecycleOrder(
                user=user,
                template=template,
                device_type=template.device_type,
                brand=template.brand,
                model=template.model,
                storage=storage,
                selected_storage=storage,
                selected_color=rng.choice(template.color_options or ["黑色", "白色", "蓝色"]),
                selected_ram=rng.choice(template.ram_options or ["6GB", "8GB", "12GB"]),
                selected_version=rng.choice(template.version_options or ["国行", "港版"]),
                questionnaire_answers=answers,
                condition=condition,
                estimated_price=estimated_price,
                final_price=(final_price if status in ["inspected", "completed"] else None),
                bonus=bonus,
                final_price_confirmed=final_price_confirmed,
                status=status,
                address="北京市朝阳区示例路 1 号（拟真数据）",
                note=f"[{tag}] demo seed data; base={base_price}; impacts={impacts}",
                shipping_carrier=(rng.choice(["顺丰", "圆通", "中通"]) if shipped_at else None),
                tracking_number=(f"SF{rng.randint(10**9, 10**10-1)}" if shipped_at else None),
                shipped_at=shipped_at,
                received_at=received_at,
                inspected_at=inspected_at,
                payment_status=payment_status,
                payment_method=("transfer" if payment_status == "paid" else ""),
                payment_account=None,
                paid_at=paid_at,
                payment_note=("拟真数据打款" if payment_status == "paid" else ""),
                price_dispute=price_dispute,
                price_dispute_reason=price_dispute_reason or None,
                reject_reason=reject_reason or None,
                created_at=created_at,
                updated_at=max(created_at, shipped_at or created_at, received_at or created_at, inspected_at or created_at, paid_at or created_at),
            )
            created_orders.append(order)

        # bulk insert orders
        RecycleOrder.objects.bulk_create(created_orders, batch_size=500)

        # Create reports for inspected/completed orders (most of them)
        inserted = list(RecycleOrder.objects.filter(note__icontains=tag).order_by("-id")[:count])
        inserted.reverse()

        reports: List[AdminInspectionReport] = []
        for o in inserted:
            if o.status not in ["inspected", "completed"]:
                continue
            if rng.random() < 0.12:
                continue
            check_items = _build_check_items(rng, _impact_counts(o.questionnaire_answers or {}))
            reports.append(
                AdminInspectionReport(
                    order=o,
                    check_items=check_items,
                    remarks="拟真数据质检报告",
                    evidence=[],
                    overall_result=("failed" if _calc_fail_rate(check_items) > 0.18 else "passed"),
                    recommend_price=None,
                    score=None,
                    template_name="seed",
                    template_version="v1",
                )
            )
        if reports:
            AdminInspectionReport.objects.bulk_create(reports, batch_size=200)

        # Retiming: make created_at/updated_at realistic for BI demos (bulk_create may overwrite auto_now fields)
        affected = _retime_orders_by_tag(tag=tag, days=days)

        self.stdout.write(self.style.SUCCESS(
            f"Created {len(inserted)} recycle orders (tag={tag}), reports={len(reports)}; retimed={affected}."
        ))
