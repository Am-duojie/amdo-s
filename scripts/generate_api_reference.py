#!/usr/bin/env python3
"""
Generate docs/30-api/api-reference.generated.md

覆盖范围：
1) backend/core/urls.py
   - DefaultRouter.register(...) 资源
   - urlpatterns 里显式 path（auth/payment/recycle-catalog 等）
2) backend/app/secondhand_app/views.py
   - 各 ViewSet 的 @action 自定义接口
   - RecycleCatalogView 等 CBV 的 http method（基于 get/post/put/patch/delete 方法名推断）
3) backend/app/secondhand_app/payment_views.py
   - @api_view([...]) 推断方法
4) backend/app/admin_api/urls.py + views.py
   - 管理端所有 path，并尽量推断方法

注意：
- 本脚本不会 import Django（只做 AST 静态解析），可在 Windows 直接运行
- 输出文件：docs/30-api/api-reference.generated.md
"""

from __future__ import annotations
from pathlib import Path
import ast
import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]

CORE_URLS = REPO_ROOT / "backend" / "core" / "urls.py"
SECONDHAND_VIEWS = REPO_ROOT / "backend" / "app" / "secondhand_app" / "views.py"
PAYMENT_VIEWS = REPO_ROOT / "backend" / "app" / "secondhand_app" / "payment_views.py"

ADMIN_URLS = REPO_ROOT / "backend" / "app" / "admin_api" / "urls.py"
ADMIN_VIEWS = REPO_ROOT / "backend" / "app" / "admin_api" / "views.py"

OUT = REPO_ROOT / "docs" / "30-api" / "api-reference.generated.md"


# ----------------- helpers -----------------

def read_text(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def dotted_name(node: ast.AST) -> str:
    """Convert ast.Name / ast.Attribute to dotted string."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{dotted_name(node.value)}.{node.attr}"
    return "UNKNOWN"


def const_str(node: ast.AST) -> Optional[str]:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def const_bool(node: ast.AST) -> Optional[bool]:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, bool) else None


def list_of_str(node: ast.AST) -> Optional[List[str]]:
    if isinstance(node, (ast.List, ast.Tuple)):
        out: List[str] = []
        for el in node.elts:
            s = const_str(el)
            if s:
                out.append(s.upper())
        return out
    return None


def md_escape(s: str) -> str:
    return s.replace("`", "\\`")


# ----------------- parse core urls -----------------

def parse_core_router_registers(core_text: str) -> List[Tuple[str, str]]:
    """
    return: [(prefix, ViewSetClassName)]
    """
    tree = ast.parse(core_text)
    out: List[Tuple[str, str]] = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "register":
            if len(n.args) >= 2:
                prefix = const_str(n.args[0])
                if not prefix:
                    continue
                vs_expr = dotted_name(n.args[1])
                vs_name = vs_expr.split(".")[-1]
                out.append((prefix, vs_name))
    return out


def parse_django_path_calls(py_text: str) -> List[Dict[str, str]]:
    tree = ast.parse(py_text)
    results: List[Dict[str, str]] = []

    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            func_name = None
            if isinstance(n.func, ast.Name):
                func_name = n.func.id
            elif isinstance(n.func, ast.Attribute):
                func_name = n.func.attr

            if func_name not in ("path", "re_path"):
                continue
            if len(n.args) < 2:
                continue

            route = const_str(n.args[0])
            if not route:
                continue

            target_node = n.args[1]

            # include(...)
            if isinstance(target_node, ast.Call) and isinstance(target_node.func, ast.Name) and target_node.func.id == "include":
                target = "include"
            # ✅ 关键：Class.as_view() / func() 这种 Call
            elif isinstance(target_node, ast.Call):
                target = dotted_name(target_node.func)   # 例如 LoginView.as_view
            else:
                target = dotted_name(target_node)

            results.append({"route": route, "target": target})

    return results



# ----------------- parse secondhand viewsets/actions -----------------

def parse_viewset_bases_and_actions(views_text: str) -> Dict[str, Dict]:
    """
    return:
    {
      "UserViewSet": {
        "bases": ["viewsets.ModelViewSet"],
        "actions": [
           {"func":"me","detail":False,"methods":["GET","PATCH"],"url_path":"me","doc":"..."}
        ]
      },
      ...
    }
    """
    tree = ast.parse(views_text)
    out: Dict[str, Dict] = {}

    def is_action_decorator(dec: ast.AST) -> bool:
        if isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name) and dec.func.id == "action":
                return True
            if isinstance(dec.func, ast.Attribute) and dec.func.attr == "action":
                return True
        return False

    def parse_action(dec_call: ast.Call) -> Dict:
        detail = None
        methods = None
        url_path = None
        url_name = None
        for kw in dec_call.keywords:
            if kw.arg == "detail":
                detail = const_bool(kw.value)
            elif kw.arg == "methods":
                methods = list_of_str(kw.value)
            elif kw.arg == "url_path":
                url_path = const_str(kw.value)
            elif kw.arg == "url_name":
                url_name = const_str(kw.value)
        return {
            "detail": detail,
            "methods": methods,
            "url_path": url_path,
            "url_name": url_name,
        }

    def base_names(cls: ast.ClassDef) -> List[str]:
        names: List[str] = []
        for b in cls.bases:
            names.append(dotted_name(b))
        return names

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name.endswith("ViewSet"):
            actions: List[Dict] = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    for dec in item.decorator_list:
                        if is_action_decorator(dec) and isinstance(dec, ast.Call):
                            info = parse_action(dec)
                            info["func"] = item.name
                            info["url_path"] = info["url_path"] or item.name
                            info["doc"] = ast.get_docstring(item) or ""
                            actions.append(info)
            out[node.name] = {
                "bases": base_names(node),
                "actions": actions,
            }

    return out


def parse_cbv_methods(views_text: str) -> Dict[str, List[str]]:
    """
    For class-based views (non-ViewSet), infer http methods by checking get/post/put/patch/delete defs.
    """
    tree = ast.parse(views_text)
    method_map: Dict[str, List[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = set()
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in ("get", "post", "put", "patch", "delete"):
                    methods.add(item.name.upper())
            if methods:
                method_map[node.name] = sorted(methods)
    return method_map


# ----------------- parse payment function methods -----------------

def parse_api_view_methods(payment_text: str) -> Dict[str, List[str]]:
    """
    From @api_view([...]) decorator, infer allowed methods for function views.
    """
    tree = ast.parse(payment_text)
    out: Dict[str, List[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == "api_view":
                    if dec.args and isinstance(dec.args[0], (ast.List, ast.Tuple)):
                        ms = []
                        for el in dec.args[0].elts:
                            s = const_str(el)
                            if s:
                                ms.append(s.upper())
                        if ms:
                            out[node.name] = ms
    return out


# ----------------- parse admin urls + infer methods from admin views -----------------

def parse_admin_view_methods(admin_views_text: str) -> Dict[str, List[str]]:
    tree = ast.parse(admin_views_text)
    out: Dict[str, List[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = set()
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in ("get", "post", "put", "patch", "delete"):
                    methods.add(item.name.upper())
            if methods:
                out[node.name] = sorted(methods)
    return out


# ----------------- output composition -----------------

def standard_routes_for_viewset(prefix: str, bases: List[str]) -> List[Tuple[str, str]]:
    """
    Return list of (METHODS, PATH) for standard routes based on base class.
    """
    p = f"/api/{prefix}/"
    pk = f"/api/{prefix}/<id>/"

    if any("ReadOnlyModelViewSet" in b for b in bases):
        return [
            ("GET", p + ""),
            ("GET", pk + ""),
        ]

    # Default assume ModelViewSet-like
    return [
        ("GET", p + ""),
        ("POST", p + ""),
        ("GET", pk + ""),
        ("PUT", pk + ""),
        ("PATCH", pk + ""),
        ("DELETE", pk + ""),
    ]


def action_routes_for_viewset(prefix: str, action: Dict) -> Tuple[str, str, str]:
    """
    Return (METHODS, PATH, DOC) for action.
    """
    methods = ",".join(action.get("methods") or ["(UNKNOWN)"])
    url_path = action.get("url_path") or action.get("func")
    detail = action.get("detail")
    # DRF DefaultRouter action path usually ends with a trailing slash
    if detail is True:
        path = f"/api/{prefix}/<id>/{url_path}/"
    else:
        path = f"/api/{prefix}/{url_path}/"
    doc = action.get("doc") or ""
    return methods, path, doc


def group_admin_paths(paths: List[Dict[str, str]], method_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = defaultdict(list)
    for e in paths:
        route = e["route"]
        target = e["target"]

        # 统一输出为 /admin-api/xxx
        full = "/admin-api/" + route.lstrip("/")

        # 尽量从 target 推断方法（ClassView.as_view -> ClassView）
        methods = []
        if target.endswith(".as_view"):
            cls = target.split(".")[-2] if "." in target else target.replace(".as_view", "")
            methods = method_map.get(cls, [])
        else:
            cls = target.split(".")[-1]
            methods = method_map.get(cls, [])

        mtxt = ",".join(methods) if methods else "(METHODS UNKNOWN)"
        # 按第一段分组
        key = route.split("/")[0] if route else "misc"
        groups[key].append(f"- `{mtxt}` `{full}`")
    return groups


def main():
    core_text = read_text(CORE_URLS)
    views_text = read_text(SECONDHAND_VIEWS)
    pay_text = read_text(PAYMENT_VIEWS)

    admin_urls_text = read_text(ADMIN_URLS)
    admin_views_text = read_text(ADMIN_VIEWS)

    today = datetime.date.today().isoformat()

    router_regs = parse_core_router_registers(core_text) if core_text else []
    core_paths = parse_django_path_calls(core_text) if core_text else []
    viewset_info = parse_viewset_bases_and_actions(views_text) if views_text else {}
    cbv_methods = parse_cbv_methods(views_text) if views_text else {}
    payment_methods = parse_api_view_methods(pay_text) if pay_text else {}

    admin_paths = parse_django_path_calls(admin_urls_text) if admin_urls_text else []
    admin_method_map = parse_admin_view_methods(admin_views_text) if admin_views_text else {}

    # ----------------- core explicit endpoints -----------------
    explicit_api_endpoints: List[str] = []
    for e in core_paths:
        route = e["route"]
        target = e["target"]
        # only show explicit /api/* (exclude router include)
        if not route.startswith("api/"):
            continue
        if route == "api/":
            continue
        if target == "include":
            # router include
            continue

        full = "/" + route

        # Infer methods for some known patterns
        methods = "(METHODS UNKNOWN)"
        # payment_views.<func>
        if target.startswith("payment_views."):
            fn = target.split(".")[-1]
            ms = payment_methods.get(fn, [])
            methods = ",".join(ms) if ms else methods
        # auth views are typically POST
        if route.startswith("api/auth/login/"):
            methods = "POST"
        if route.startswith("api/auth/refresh/"):
            methods = "POST"
        # RecycleCatalogView.as_view()
        if target.endswith(".as_view") and "RecycleCatalogView" in target:
            ms = cbv_methods.get("RecycleCatalogView", [])
            methods = ",".join(ms) if ms else methods

        explicit_api_endpoints.append(f"- `{methods}` `{full}`  (target: `{md_escape(target)}`)")

    # ----------------- compose markdown -----------------
    md: List[str] = []
    md.append("# API 参考（生成）")
    md.append("")
    md.append("> 该文件由脚本生成：`python scripts/generate_api_reference.py`")
    md.append("> 请勿手工编辑。手工说明请写在 `docs/30-api/api-guide.md`。")
    md.append("")
    md.append(f"- 生成日期：{today}")
    md.append("- 占位符说明：`<id>` 表示资源主键（DRF 默认 pk）")
    md.append("")

    md.append("## 用户端 API（/api）— 资源（DefaultRouter）")
    if not router_regs:
        md.append("- （未解析到 router.register，请检查 backend/core/urls.py）")
    else:
        # Build a quick lookup: viewset_name -> prefix
        for prefix, vs_name in router_regs:
            md.append("")
            md.append(f"### `{prefix}` (ViewSet: `{vs_name}`)")
            info = viewset_info.get(vs_name, {})
            bases = info.get("bases", [])
            actions = info.get("actions", [])

            # Standard routes
            md.append("")
            md.append("标准路由：")
            for mth, path in standard_routes_for_viewset(prefix, bases):
                # DefaultRouter usually has trailing slash
                # We keep paths as ending with "/" for readability
                if not path.endswith("/"):
                    path = path + "/"
                md.append(f"- `{mth}` `{path}`")

            # Custom actions
            md.append("")
            md.append("自定义 @action：")
            if not actions:
                md.append("- （无）")
            else:
                for a in actions:
                    methods, path, doc = action_routes_for_viewset(prefix, a)
                    line = f"- `{methods}` `{path}`"
                    if doc.strip():
                        # keep doc short
                        short = doc.strip().splitlines()[0]
                        line += f" — {md_escape(short)}"
                    md.append(line)

    md.append("")
    md.append("## 用户端 API（/api）— 显式接口（非 Router）")
    if explicit_api_endpoints:
        md.extend(explicit_api_endpoints)
    else:
        md.append("- （无）")

    md.append("")
    md.append("## 管理端 API（/admin-api）")
    if not admin_paths:
        md.append("- （未解析到 admin_api urls，请检查 backend/app/admin_api/urls.py）")
    else:
        groups = group_admin_paths(admin_paths, admin_method_map)
        for k in sorted(groups.keys()):
            md.append("")
            md.append(f"### `{k}`")
            md.extend(sorted(groups[k]))

    md.append("")
    md.append("## WebSocket")
    md.append("- `GET` `/ws/chat/?token=<jwt>`")
    md.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote: {OUT}")


if __name__ == "__main__":
    main()
