import json
import re
import time
import random
from pathlib import Path
from typing import List, Dict, Any

from django.core.management.base import BaseCommand, CommandError

# 可选：Playwright（若环境不支持将自动回退为模拟数据生成）
try:
    from playwright.sync_api import sync_playwright  # type: ignore
except Exception:  # pragma: no cover
    sync_playwright = None  # type: ignore

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
]

FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200&q=80&auto=format",
    "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1200&q=80&auto=format",
    "https://images.unsplash.com/photo-1510552776732-01acc9a071c3?w=1200&q=80&auto=format",
    "https://images.unsplash.com/photo-1512499617640-c2f999098c4b?w=1200&q=80&auto=format",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80&auto=format",
    "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=1200&q=80&auto=format",
]

CANDIDATE_SEARCH_URLS = [
    # 仅作占位：不同地区/版本结构不同，实际运行可能无法解析，将回退为模拟数据
    "https://goofish.com/search?keyword={q}",
    "https://goofish.com/search?q={q}",
    "https://s.2.taobao.com/list?search_type=item&q={q}",
]

CITY_POOL = ["北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "南京", "武汉", "西安", "天津", "长沙"]

class Command(BaseCommand):
    help = "抓取/生成二手数码数据集（教学/测试），尽量丰富描述信息。"

    def add_arguments(self, parser):
        parser.add_argument("--keywords", type=str, required=True,
                            help="以逗号/空格分隔的关键词，如: 手机,相机,平板,电脑,耳机,音响,游戏设备")
        parser.add_argument("--per", type=int, default=20, help="每个关键词抓取条数，默认20")
        parser.add_argument("--out", type=str, default="backend/data/xianyu_dataset.json",
                            help="输出JSON路径，默认 backend/data/xianyu_dataset.json")
        parser.add_argument("--delay", type=float, default=1.2, help="抓取间隔(秒)")
        parser.add_argument("--headful", action="store_true", help="以可见浏览器运行(调试用)")

    def handle(self, *args, **options):
        raw_keywords: str = options["keywords"]
        per: int = options["per"]
        out_path: str = options["out"]
        delay: float = options["delay"]
        headful: bool = options["headful"]

        # 解析关键词
        keywords = [k.strip() for k in re.split(r"[，,\s]+", raw_keywords) if k.strip()]
        if not keywords:
            raise CommandError("请提供至少一个关键词")

        out_file = Path(out_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        all_items: List[Dict[str, Any]] = []

        if sync_playwright is None:
            self.stdout.write(self.style.WARNING("未安装 playwright 或环境不支持，将使用富描述的模拟数据生成。"))
            for kw in keywords:
                all_items.extend(self._generate_fallback_items(kw, per))
        else:
            try:
                crawled = self._crawl_with_playwright(keywords, per, delay, headful)
                # Playwright 可能也抓不齐，这里对不足部分补齐
                remain = {}
                for kw in keywords:
                    cnt = len([x for x in crawled if x.get("keyword") == kw])
                    if cnt < per:
                        remain[kw] = per - cnt
                for kw, n in remain.items():
                    crawled.extend(self._generate_fallback_items(kw, n))
                all_items.extend(crawled)
            except Exception:
                # 任意异常兜底
                for kw in keywords:
                    all_items.extend(self._generate_fallback_items(kw, per))

        with out_file.open("w", encoding="utf-8") as f:
            json.dump(all_items, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"完成，输出 {len(all_items)} 条数据 -> {out_file}"))

    # ---------------------------- Playwright 抓取（尽量提取详情） ----------------------------
    def _crawl_with_playwright(self, keywords: List[str], per: int, delay: float, headful: bool) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        from playwright.sync_api import TimeoutError as PWTimeout  # type: ignore

        with sync_playwright() as p:  # type: ignore
            browser = p.chromium.launch(headless=not headful)
            context = browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={"width": 1366, "height": 820})
            page = context.new_page()

            for kw in keywords:
                extracted = 0
                for base in CANDIDATE_SEARCH_URLS:
                    if extracted >= per:
                        break
                    url = base.format(q=kw)
                    try:
                        page.goto(url, timeout=30000, wait_until="domcontentloaded")
                        time.sleep(delay)
                    except PWTimeout:
                        continue
                    except Exception:
                        continue

                    # 粗略选择器（无法保证稳定）
                    card_selectors = [
                        "a[href*='item']",
                        ".item a[href]",
                        "a.card, a.Card, a.goods, a.Goods",
                    ]
                    cards = None
                    for sel in card_selectors:
                        nodes = page.query_selector_all(sel)
                        if nodes:
                            cards = nodes
                            break
                    if not cards:
                        continue

                    for a in cards:
                        if extracted >= per:
                            break
                        try:
                            href = a.get_attribute("href") or ""
                            title = (a.inner_text() or "").strip()[:60]
                            if not href or not title:
                                continue

                            # 价格与封面
                            price_text = None
                            img_src = None
                            try:
                                price_el = a.query_selector(".price, .Price, .price-num, .amount, .card-price")
                                if price_el:
                                    price_text = price_el.inner_text().strip()
                            except Exception:
                                pass
                            try:
                                img_el = a.query_selector("img")
                                if img_el:
                                    img_src = img_el.get_attribute("src")
                            except Exception:
                                pass

                            price = self._parse_price(price_text) or round(random.uniform(99, 5999), 2)
                            url_full = href if href.startswith("http") else ("https://" + href.lstrip("/"))

                            # 进入详情页尝试提取描述（可能失败）
                            desc_text = ""
                            try:
                                detail = context.new_page()
                                detail.goto(url_full, timeout=20000, wait_until="domcontentloaded")
                                time.sleep(0.8)
                                # 粗略查找详情描述/正文
                                for sel in [
                                    ".desc, .Desc, .description, .content, .detail, #description",
                                    "article, .article, .post, .RichText",
                                ]:
                                    el = detail.query_selector(sel)
                                    if el:
                                        t = (el.inner_text() or "").strip()
                                        if t and len(t) > 15:
                                            desc_text = t[:800]
                                            break
                                detail.close()
                            except Exception:
                                try:
                                    detail.close()
                                except Exception:
                                    pass

                            item = {
                                "title": title,
                                "price": price,
                                "city": random.choice(CITY_POOL),
                                "image": img_src or random.choice(FALLBACK_IMAGES),
                                "images": [img_src] if img_src else random.sample(FALLBACK_IMAGES, k=3),
                                "url": url_full,
                                "category": self._map_category(kw),
                                "keyword": kw,
                                "description": desc_text or self._build_rich_description(kw, title, price),
                            }
                            items.append(item)
                            extracted += 1
                        except Exception:
                            continue

            context.close()
            browser.close()
        return items

    # ---------------------------- 辅助 ----------------------------
    def _parse_price(self, s: str | None):
        if not s:
            return None
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)", s.replace(",", ""))
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None
        return None

    def _map_category(self, kw: str) -> str:
        mapping = {
            "手机": "手机数码",
            "相机": "摄影摄像",
            "平板": "平板/笔记本",
            "电脑": "电脑办公",
            "耳机": "耳机音响",
            "音响": "耳机音响",
            "游戏": "游戏设备",
        }
        for k, v in mapping.items():
            if k in kw:
                return v
        return "手机数码"

    def _build_rich_description(self, kw: str, title: str, price: float) -> str:
        months = random.randint(2, 24)
        battery = random.randint(85, 100)
        extras_map = {
            "手机": ["原装充电器", "原包装盒", "两幅手机壳"],
            "相机": ["原装电池X2", "相机包", "UV镜"],
            "平板": ["磁吸键盘", "触控笔", "保护套"],
            "电脑": ["原装电源", "背包", "鼠标垫"],
            "耳机": ["充电线", "收纳盒", "备用耳塞"],
            "音响": ["电源线", "音频线", "说明书"],
            "游戏": ["原装手柄", "支架", "HDMI线"],
        }
        extras = extras_map.get(kw[:2], ["原装配件齐全"])
        extras_text = "、".join(extras)
        desc = (
            f"【商品标题】{title}\n"
            f"【成交意向价】¥{price:.2f}（可小刀）\n"
            f"【使用时长】约 {months} 个月，主要用于学习/日常办公\n"
            f"【电池健康】约 {battery}%（以实际为准）\n"
            f"【外观成色】正常轻微使用痕迹，无明显磕碰；功能均正常\n"
            f"【配件清单】{extras_text}\n"
            f"【交易方式】同城当面/平台邮寄，优先同城验货自提\n"
            f"【备注说明】支持当面验机，接受第三方检测，介意勿拍。\n"
        )
        return desc
    def _generate_fallback_items(self, kw: str, n: int) -> List[Dict[str, Any]]:
        res: List[Dict[str, Any]] = []
        for _ in range(n):
            price = round(random.uniform(99, 8999), 2)
            title = f"{kw} 优惠出 | 成色良好 支持当面验货"
            desc = self._build_rich_description(kw, title, price)
            images = random.sample(FALLBACK_IMAGES, k=3)
            res.append({
                "title": title,
                "price": price,
                "city": random.choice(CITY_POOL),
                "image": images[0],
                "images": images,
                "url": "",
                "category": self._map_category(kw),
                "keyword": kw,
                "description": desc,
            })
        return res

