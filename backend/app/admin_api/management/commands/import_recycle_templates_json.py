from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from django.core.management.base import BaseCommand
from django.db import transaction

from app.admin_api.models import (
    AdminUser,
    RecycleDeviceTemplate,
    RecycleQuestionOption,
    RecycleQuestionTemplate,
)


def _clean_relaxed_json(text: str) -> str:
    """
    Make a best-effort attempt to parse JSON copied from Markdown/chat:
    - undo escaping like \\_ \\[ \\]
    - remove leading BOM
    - strip common quote blocks and trailing notes
    """
    text = text.lstrip("\ufeff").strip()

    # Drop markdown quote prefix lines like "> ..."
    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            continue
        lines.append(line)
    text = "\n".join(lines).strip()

    # Undo common escapes from markdown
    text = text.replace("\\_", "_").replace("\\[", "[").replace("\\]", "]")

    # If user pasted with a leading title line, try to locate the first "{"
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        text = text[first : last + 1]

    return text


def _norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


BRAND_MAP = {
    "Redmi": "红米",
    "redmi": "红米",
    "Xiaomi": "小米",
    "xiaomi": "小米",
    "HONOR": "荣耀",
    "honor": "荣耀",
    "HUAWEI": "华为",
    "huawei": "华为",
    "Apple": "苹果",
    "apple": "苹果",
    "Samsung": "三星",
    "samsung": "三星",
    "Lenovo": "联想",
    "lenovo": "联想",
    "DELL": "戴尔",
    "dell": "戴尔",
    "HP": "惠普",
    "hp": "惠普",
}


def _normalize_brand(brand: str) -> str:
    b = _norm_space(brand)
    if b in BRAND_MAP:
        return BRAND_MAP[b]
    # Heuristic: "荣耀平板" -> "荣耀"
    if b.startswith("荣耀"):
        return "荣耀"
    return b


def _normalize_device_type(device_type: str) -> str:
    d = _norm_space(device_type)
    allowed = {"手机", "平板", "笔记本"}
    return d if d in allowed else d


def _normalize_storage(s: str) -> str:
    s = _norm_space(s).upper().replace(" ", "")
    # Normalize common forms: 1TB, 1024GB -> 1TB
    if s == "1024GB":
        return "1TB"
    return s


def _normalize_base_prices(base_prices: Any, storages: List[str]) -> Tuple[Dict[str, float], List[str]]:
    """
    Returns (base_prices, storages_filtered).
    Keeps only storages that have a numeric base price.
    """
    if not isinstance(base_prices, dict):
        return {}, []
    out: Dict[str, float] = {}
    filtered: List[str] = []
    for raw_storage in storages:
        storage = _normalize_storage(raw_storage)
        price = base_prices.get(raw_storage)
        if price is None:
            price = base_prices.get(storage)
        try:
            p = float(price)
        except (TypeError, ValueError):
            continue
        if p <= 0:
            continue
        out[storage] = p
        filtered.append(storage)
    return out, filtered


def _normalize_str_list(v: Any) -> List[str]:
    if not isinstance(v, list):
        return []
    out = []
    for item in v:
        if item is None:
            continue
        out.append(_norm_space(str(item)))
    return [x for x in out if x]


def _normalize_spec_str(v: Any) -> str:
    s = _norm_space(str(v or ""))
    # "6.7 英寸" -> "6.7英寸"
    s = s.replace(" 英寸", "英寸")
    return s


@dataclass
class ImportStats:
    created: int = 0
    updated: int = 0
    skipped: int = 0


def _ensure_default_questions(template: RecycleDeviceTemplate) -> None:
    """
    Reuse the same default question set as import_recycle_templates.py.
    Create questions only when template has no questions at all.
    """
    if template.questions.exists():
        return
    try:
        from app.admin_api.management.commands.import_recycle_templates import DEFAULT_QUESTIONS
    except Exception:
        return

    for q_data in DEFAULT_QUESTIONS:
        question = RecycleQuestionTemplate.objects.create(
            device_template=template,
            step_order=q_data["step_order"],
            key=q_data["key"],
            title=q_data["title"],
            helper=q_data.get("helper", ""),
            question_type=q_data.get("question_type", "single"),
            is_required=bool(q_data.get("is_required", True)),
            is_active=True,
        )

        # Storage options are generated from `template.storages` in UI; we still create option records for completeness.
        if q_data["key"] == "storage":
            for idx, storage in enumerate(template.storages or []):
                RecycleQuestionOption.objects.create(
                    question_template=question,
                    value=storage,
                    label=storage,
                    desc="",
                    impact="",
                    option_order=idx,
                    is_active=True,
                )
            continue

        for opt in q_data.get("options", []) or []:
            RecycleQuestionOption.objects.create(
                question_template=question,
                value=opt["value"],
                label=opt["label"],
                desc=opt.get("desc", ""),
                impact=opt.get("impact", "") or "",
                option_order=int(opt.get("option_order") or 0),
                is_active=True,
            )


class Command(BaseCommand):
    help = "Import recycle device templates from a JSON file (e.g. third-party AI output)."

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, required=True, help="Path to JSON file.")
        parser.add_argument("--clear", action="store_true", help="Clear existing recycle templates (DANGEROUS).")
        parser.add_argument("--dry-run", action="store_true", help="Validate and print stats, but do not write.")
        parser.add_argument("--ensure-questions", action="store_true", help="Create default questions for templates missing questions.")

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            raise SystemExit(f"File not found: {file_path}")

        raw = file_path.read_text(encoding="utf-8")
        cleaned = _clean_relaxed_json(raw)
        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON: {exc}") from exc

        templates = payload.get("templates")
        if not isinstance(templates, list) or not templates:
            raise SystemExit("JSON must contain non-empty `templates` array.")

        admin_user = AdminUser.objects.first()

        if options["clear"]:
            if options["dry_run"]:
                self.stdout.write(self.style.WARNING("[dry-run] would clear existing templates"))
            else:
                RecycleQuestionOption.objects.all().delete()
                RecycleQuestionTemplate.objects.all().delete()
                RecycleDeviceTemplate.objects.all().delete()
                self.stdout.write(self.style.WARNING("Cleared existing recycle templates."))

        stats = ImportStats()
        errors: List[str] = []

        for idx, t in enumerate(templates, start=1):
            if not isinstance(t, dict):
                stats.skipped += 1
                errors.append(f"#{idx}: template is not an object")
                continue

            device_type = _normalize_device_type(t.get("device_type", ""))
            brand = _normalize_brand(t.get("brand", ""))
            model = _norm_space(t.get("model", ""))
            if not device_type or not brand or not model:
                stats.skipped += 1
                errors.append(f"#{idx}: missing required fields (device_type/brand/model)")
                continue

            storages_raw = _normalize_str_list(t.get("storages"))
            storages_raw = [_normalize_storage(s) for s in storages_raw]
            base_prices_raw = t.get("base_prices")
            base_prices, storages = _normalize_base_prices(base_prices_raw, storages_raw)
            if not storages or not base_prices:
                stats.skipped += 1
                errors.append(f"#{idx}: no valid storages/base_prices for {device_type}/{brand}/{model}")
                continue

            defaults = {
                "storages": storages,
                "base_prices": base_prices,
                "series": _norm_space(t.get("series", "")),
                "ram_options": _normalize_str_list(t.get("ram_options")),
                "version_options": _normalize_str_list(t.get("version_options")),
                "color_options": _normalize_str_list(t.get("color_options")),
                "default_cover_image": _norm_space(t.get("default_cover_image", "")),
                "default_detail_images": _normalize_str_list(t.get("default_detail_images")),
                "description_template": _norm_space(t.get("description_template", "")),
                "is_active": bool(t.get("is_active", True)),
                "created_by": admin_user,
            }

            if options["dry_run"]:
                # Count as update/create based on existence
                exists = RecycleDeviceTemplate.objects.filter(device_type=device_type, brand=brand, model=model).exists()
                stats.updated += 1 if exists else 0
                stats.created += 0 if exists else 1
                continue

            obj, created = RecycleDeviceTemplate.objects.get_or_create(
                device_type=device_type,
                brand=brand,
                model=model,
                defaults=defaults,
            )
            if created:
                stats.created += 1
            else:
                changed = False
                for k, v in defaults.items():
                    if getattr(obj, k) != v:
                        setattr(obj, k, v)
                        changed = True
                if changed:
                    obj.save()
                stats.updated += 1

            if options["ensure_questions"]:
                _ensure_default_questions(obj)

        if errors:
            self.stdout.write(self.style.WARNING(f"Skipped {stats.skipped} templates; showing first 10 errors:"))
            for e in errors[:10]:
                self.stdout.write(f"  - {e}")

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(
                f"[dry-run] templates={len(templates)} created={stats.created} updated={stats.updated} skipped={stats.skipped}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Imported templates={len(templates)} created={stats.created} updated={stats.updated} skipped={stats.skipped}"
            ))
