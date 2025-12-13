#!/usr/bin/env python3
"""
Generate docs/30-api/api-reference.generated.md

毕业设计阶段的“低成本自动化”：从 Django 路由文件中提取明显的 API 入口与说明占位，
避免你每次改接口都手工维护长表格。

你可以逐步增强它：
- 解析 DRF router.register 列表
- 解析 @action 的 url_path / methods
- 输出成 Markdown 目录结构

注意：本脚本默认在仓库根目录执行。
"""

from pathlib import Path
import re
import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "docs" / "30-api" / "api-reference.generated.md"

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")

def extract_from_core_urls() -> list[str]:
    candidates = []
    urls_py = REPO_ROOT / "backend" / "core" / "urls.py"
    if not urls_py.exists():
        return candidates
    s = read_text(urls_py)

    # Router register: router.register(r'users', UserViewSet, basename='users')
    for m in re.finditer(r"router\.register\(\s*r[\"']([^\"']+)[\"']\s*,\s*([A-Za-z0-9_]+)", s):
        prefix, viewset = m.group(1), m.group(2)
        candidates.append(f"- `/api/{prefix}/`  (ViewSet: `{viewset}`)")

    # Explicit payment endpoints in urls.py
    if "payment" in s:
        candidates.append("- `/api/payment/*`  (支付相关：create/query/notify 等，详见后端 urls 聚合)")

    return candidates

def main():
    items = extract_from_core_urls()
    now = datetime.date.today().isoformat()

    md = []
    md.append("# API 参考（生成）")
    md.append("")
    md.append("> 该文件由脚本生成：`python scripts/generate_api_reference.py`")
    md.append("> 请勿手工编辑。手工说明请写在 `docs/30-api/api-guide.md`。")
    md.append("")
    md.append(f"- 生成日期：{now}")
    md.append("")
    md.append("## 用户端 API（/api）")
    md.extend(items or ["- （未能自动提取，请检查 backend/core/urls.py）"])
    md.append("")
    md.append("## 管理端 API（/admin-api）")
    md.append("- `/admin-api/*`（建议：在此补充管理端关键入口，或增强脚本解析 admin_api 路由）")
    md.append("")
    md.append("## WebSocket")
    md.append("- `/ws/chat/?token=<jwt>`")
    md.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote: {OUT}")

if __name__ == "__main__":
    main()
