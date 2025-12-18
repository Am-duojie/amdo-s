from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def _safe_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _round_money(v: float) -> float:
    return float(f"{v:.2f}")


def _count_impacts(questionnaire_answers: Any) -> Dict[str, int]:
    counts = {"positive": 0, "minor": 0, "major": 0, "critical": 0, "unknown": 0}
    if not isinstance(questionnaire_answers, dict):
        return counts

    def consume_one(option: Any) -> None:
        if not isinstance(option, dict):
            counts["unknown"] += 1
            return
        impact = (option.get("impact") or "").strip()
        if impact in counts:
            counts[impact] += 1
        else:
            counts["unknown"] += 1

    for _key, answer in questionnaire_answers.items():
        if answer is None:
            continue
        if isinstance(answer, list):
            for item in answer:
                consume_one(item)
        else:
            consume_one(answer)

    return counts


def _inspection_fail_rate(check_items: Any) -> Tuple[float, int, int]:
    """
    Returns (fail_rate, total_count, fail_count).

    Supports:
    - dict format: {k: bool|'pass'|'fail'|...}
    - list format: [{pass: bool, ...}, ...] (66项质检)
    """
    total = 0
    fail = 0

    def is_fail(v: Any) -> Optional[bool]:
        if v is True or v == "pass":
            return False
        if v is False or v == "fail":
            return True
        return None

    if isinstance(check_items, dict):
        for _k, v in check_items.items():
            r = is_fail(v)
            if r is None:
                continue
            total += 1
            if r:
                fail += 1
    elif isinstance(check_items, list):
        for item in check_items:
            if not isinstance(item, dict):
                continue
            r = is_fail(item.get("pass"))
            if r is None:
                continue
            total += 1
            if r:
                fail += 1

    rate = (fail / total) if total > 0 else 0.0
    return rate, total, fail


@dataclass(frozen=True)
class RecycleOnlineWeights:
    version: str
    price: Dict[str, float]
    dispute: Dict[str, float]
    cancel: Dict[str, float]


@lru_cache(maxsize=1)
def load_weights() -> RecycleOnlineWeights:
    default = RecycleOnlineWeights(
        version="baseline-v1",
        price={
            # 基线：以 estimated_price 为主，叠加“问题严重度/质检不通过率”等线性修正
            "bias": 0.0,
            "w_estimated": 0.92,
            "w_base": 0.25,
            "w_impact_minor": -35.0,
            "w_impact_major": -80.0,
            "w_impact_critical": -160.0,
            "w_fail_rate": -0.22,  # 按比例衰减（乘法项）
            "min_ratio_to_estimated": 0.35,
            "max_ratio_to_estimated": 1.10,
        },
        dispute={
            # 逻辑回归基线：输出异议概率（0~1）
            "bias": -1.35,
            # 注意：用户通常会对“低于预期/低于预估”的报价更敏感；
            # 因此风险用“低于预估价比例”而不是绝对偏离，避免“建议价更高却被判高风险”的误解。
            "w_down_gap_ratio": 2.20,  # max(0, (estimated - suggested) / estimated)
            "w_impact_critical": 0.55,
            "w_impact_major": 0.25,
            "w_fail_rate": 1.40,
        },
        cancel={
            # 逻辑回归基线：输出取消概率（0~1）
            "bias": -2.10,
            "w_down_gap_ratio": 1.10,  # 同上：低于预估价比例越大，取消风险越高
            "w_impact_critical": 0.65,
            "w_impact_major": 0.25,
            "w_fail_rate": 1.00,
        },
    )

    weights_path = Path(__file__).with_name("recycle_online_weights.json")
    if not weights_path.exists():
        return default

    try:
        raw = json.loads(weights_path.read_text(encoding="utf-8"))
        return RecycleOnlineWeights(
            version=str(raw.get("version") or default.version),
            price={**default.price, **(raw.get("price") or {})},
            dispute={**default.dispute, **(raw.get("dispute") or {})},
            cancel={**default.cancel, **(raw.get("cancel") or {})},
        )
    except Exception:
        return default


def predict_recycle_order(order: Any, report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Dependency-free online inference for recycle orders.
    Returns a JSON-serializable dict for admin UI display.
    """
    w = load_weights()

    estimated_price = _safe_float(getattr(order, "estimated_price", None)) or 0.0
    final_price = _safe_float(getattr(order, "final_price", None))

    # base price: prefer template base_prices when available, fallback to estimated_price.
    base_price = 0.0
    try:
        template = getattr(order, "template", None)
        selected_storage = (getattr(order, "selected_storage", None) or getattr(order, "storage", None) or "").strip()
        base_prices = getattr(template, "base_prices", None) if template else None
        if isinstance(base_prices, dict) and selected_storage:
            base_price = _safe_float(base_prices.get(selected_storage)) or 0.0
    except Exception:
        base_price = 0.0
    if base_price <= 0:
        base_price = estimated_price

    impacts = _count_impacts(getattr(order, "questionnaire_answers", None))

    check_items = None
    if isinstance(report, dict):
        check_items = report.get("check_items")
    fail_rate, check_total, check_fail = _inspection_fail_rate(check_items)

    # --- price regression (linear baseline) ---
    suggested = (
        w.price["bias"]
        + w.price["w_estimated"] * estimated_price
        + w.price["w_base"] * base_price
        + w.price["w_impact_minor"] * impacts.get("minor", 0)
        + w.price["w_impact_major"] * impacts.get("major", 0)
        + w.price["w_impact_critical"] * impacts.get("critical", 0)
    )
    suggested = suggested * (1.0 + w.price["w_fail_rate"] * _clamp(fail_rate, 0.0, 1.0))

    # clamp within a reasonable band around estimated_price (if exists)
    if estimated_price > 0:
        lo = estimated_price * float(w.price["min_ratio_to_estimated"])
        hi = estimated_price * float(w.price["max_ratio_to_estimated"])
        suggested = _clamp(suggested, lo, hi)

    suggested = max(0.0, suggested)
    suggested = _round_money(suggested)

    # range: +-5% by default, expand slightly with uncertainty.
    band = 0.05 + 0.03 * _clamp(fail_rate, 0.0, 1.0) + 0.01 * min(impacts.get("critical", 0), 3)
    low = _round_money(max(0.0, suggested * (1.0 - band)))
    high = _round_money(suggested * (1.0 + band))

    # --- risk classification (logistic baseline) ---
    gap_ratio_abs = 0.0
    down_gap_ratio = 0.0
    if estimated_price > 0:
        gap_ratio_abs = abs(suggested - estimated_price) / estimated_price
        down_gap_ratio = max(0.0, (estimated_price - suggested) / estimated_price)

    # Backward-compatible: if someone customizes weights with the old key `w_gap_ratio`, use it.
    dispute_gap_w = float(w.dispute.get("w_down_gap_ratio") or w.dispute.get("w_gap_ratio") or 0.0)
    cancel_gap_w = float(w.cancel.get("w_down_gap_ratio") or w.cancel.get("w_gap_ratio") or 0.0)

    dispute_logit = (
        w.dispute["bias"]
        + dispute_gap_w * _clamp(down_gap_ratio, 0.0, 2.0)
        + w.dispute["w_impact_critical"] * impacts.get("critical", 0)
        + w.dispute["w_impact_major"] * impacts.get("major", 0)
        + w.dispute["w_fail_rate"] * _clamp(fail_rate, 0.0, 1.0)
    )
    cancel_logit = (
        w.cancel["bias"]
        + cancel_gap_w * _clamp(down_gap_ratio, 0.0, 2.0)
        + w.cancel["w_impact_critical"] * impacts.get("critical", 0)
        + w.cancel["w_impact_major"] * impacts.get("major", 0)
        + w.cancel["w_fail_rate"] * _clamp(fail_rate, 0.0, 1.0)
    )
    risk_dispute = _round_money(_sigmoid(dispute_logit))
    risk_cancel = _round_money(_sigmoid(cancel_logit))

    top_factors: List[Dict[str, Any]] = []
    if impacts.get("critical", 0) > 0:
        top_factors.append({"label": "严重问题(critical)数量", "value": impacts.get("critical", 0)})
    if impacts.get("major", 0) > 0:
        top_factors.append({"label": "重大问题(major)数量", "value": impacts.get("major", 0)})
    if fail_rate > 0:
        top_factors.append({"label": "质检不通过率", "value": _round_money(fail_rate)})
    if estimated_price > 0:
        top_factors.append({"label": "低于预估价比例", "value": _round_money(down_gap_ratio)})
        top_factors.append({"label": "与预估价偏离比例", "value": _round_money(gap_ratio_abs)})

    return {
        "model_version": w.version,
        "suggested_final_price": suggested,
        "suggested_range": [low, high],
        "risk_dispute": float(risk_dispute),
        "risk_cancel": float(risk_cancel),
        "features": {
            "estimated_price": _round_money(estimated_price),
            "base_price": _round_money(base_price),
            "impact_counts": impacts,
            "inspection_fail_rate": _round_money(fail_rate),
            "inspection_total": int(check_total),
            "inspection_fail": int(check_fail),
            "final_price": _round_money(final_price) if final_price is not None else None,
            "gap_ratio_abs": _round_money(gap_ratio_abs),
            "down_gap_ratio": _round_money(down_gap_ratio),
        },
        "top_factors": top_factors[:5],
        "notes": [
            "在线推理为“决策辅助”，不自动改价/不自动打款；模型不可用时应回退到规则估价。",
            "当前为无历史数据的 baseline-v1，后续可用质检后的最终价/异议标签进行离线再训练更新权重。",
        ],
    }
