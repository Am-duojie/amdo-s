import json
import os
import re
import time
from pathlib import Path
from typing import Dict, Any

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
import requests

from app.secondhand_app.models import Category, Product, ProductImage

CATEGORY_ALIASES = {
    "手机": "手机数码",
    "手机数码": "手机数码",
    "相机": "摄影摄像",
    "摄影": "摄影摄像",
    "摄影摄像": "摄影摄像",
    "平板": "平板/笔记本",
    "平板/笔记本": "平板/笔记本",
    "电脑": "电脑办公",
    "电脑办公": "电脑办公",
    "耳机": "耳机音响",
    "音响": "耳机音响",
    "耳机音响": "耳机音响",
    "游戏设备": "游戏设备",
    "游戏": "游戏设备",
    # 摄影摄像类
    "无人机": "摄影摄像",
    "大疆": "摄影摄像",
    "云台": "摄影摄像",
    # 电脑办公类
    "鼠标": "电脑办公",
    "键盘": "电脑办公",
    "显示器": "电脑办公",
    "路由器": "电脑办公",
    # 智能穿戴类（新增）
    "手表": "智能穿戴",
    "手环": "智能穿戴",
    "智能手表": "智能穿戴",
    "智能手环": "智能穿戴",
    "watch": "智能穿戴",
    "band": "智能穿戴",
    # 数码配件类（新增）
    "充电器": "数码配件",
    "数据线": "数码配件",
    "手机壳": "数码配件",
    "保护膜": "数码配件",
    "移动电源": "数码配件",
    "充电宝": "数码配件",
    "保护壳": "数码配件",
    # 智能家居类（新增）
    "智能音箱": "智能家居",
    "智能门锁": "智能家居",
    "智能摄像头": "智能家居",
    "智能开关": "智能家居",
    # 存储设备类（新增）
    "u盘": "存储设备",
    "移动硬盘": "存储设备",
    "内存卡": "存储设备",
    "ssd": "存储设备",
    "固态硬盘": "存储设备",
}

SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fa5_\-]+")


def safe_filename(name: str, default: str = "image") -> str:
    name = SAFE_NAME_RE.sub("_", name).strip("_")
    return name or default


class Command(BaseCommand):
    help = "导入数据集(JSON)到数据库，并下载图片到 media/products。"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, required=True, help="JSON 数据集路径")
        parser.add_argument("--limit", type=int, default=0, help="最多导入多少条，0 表示全部")
        parser.add_argument("--username", type=str, default="demo", help="作为卖家的用户名，不存在则自动创建")
        parser.add_argument("--download-timeout", type=int, default=20, help="下载图片超时(秒)")
        parser.add_argument("--truncate", action="store_true", help="导入前清空该用户名下旧商品")

    def handle(self, *args, **options):
        file_path: str = options["file"]
        limit: int = options["limit"]
        username: str = options["username"]
        timeout: int = options["download_timeout"]
        truncate: bool = options["truncate"]

        p = Path(file_path)
        if not p.exists():
            raise CommandError(f"文件不存在: {p}")

        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise CommandError("数据格式错误，应为数组")

        # 确保分类存在
        needed = [
            "手机数码",
            "摄影摄像",
            "平板/笔记本",
            "电脑办公",
            "耳机音响",
            "游戏设备",
            "智能穿戴",
            "数码配件",
            "智能家居",
            "存储设备",
        ]
        cats: Dict[str, Category] = {}
        for name in needed:
            obj, _ = Category.objects.get_or_create(name=name, defaults={"description": name})
            cats[name] = obj

        # 确保用户存在
        user, _ = User.objects.get_or_create(username=username, defaults={"password": "demo123456"})

        # 如需清空该用户旧数据
        if truncate:
            Product.objects.filter(seller=user).delete()

        created_count = 0
        total = 0

        @transaction.atomic
        def import_one(item: Dict[str, Any]):
            nonlocal created_count, total
            total += 1

            title = (item.get("title") or "").strip()[:200]
            if not title:
                return

            price = item.get("price")
            try:
                price = float(price)
            except Exception:
                return

            city = (item.get("city") or "未知").strip()[:100]
            keyword = item.get("keyword") or ""
            raw_cat = item.get("category") or keyword
            cat_name = self._map_category(str(raw_cat))
            category = cats.get(cat_name)

            description = (item.get("desc") or item.get("description") or title)[:2000]

            product = Product.objects.create(
                seller=user,
                category=category,
                title=title,
                description=description,
                price=price,
                original_price=None,
                condition="good",
                status="active",
                location=city,
            )

            # 下载主图 + 其余图片
            all_images = []
            if item.get("images") and isinstance(item.get("images"), list):
                all_images = [x for x in item["images"] if isinstance(x, str) and x]
            elif item.get("image"):
                all_images = [item.get("image")]  # 退化为单图

            downloaded_images = 0
            for idx_img, img_url in enumerate(all_images[:5]):  # 最多取5张
                try:
                    # 添加请求头，模拟浏览器
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': 'https://www.goofish.com/',
                        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    }
                    resp = requests.get(img_url, timeout=timeout, headers=headers, allow_redirects=True)
                    
                    # 检查响应是否成功且有内容
                    if resp.ok and resp.content and len(resp.content) > 1000:  # 至少1KB，过滤掉太小的图片
                        # 检查是否是图片类型
                        content_type = resp.headers.get('content-type', '').lower()
                        if 'image' in content_type or img_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                            base = safe_filename(title[:30] or "product")
                            fname = f"{base}-{int(time.time()*1000)}-{idx_img}.jpg"
                            image_file = ContentFile(resp.content, name=fname)
                            ProductImage.objects.create(product=product, image=image_file, is_primary=(idx_img == 0))
                            downloaded_images += 1
                except Exception as e:
                    continue

            # 如果没有成功下载任何图片，删除该商品
            # if downloaded_images == 0:
            #     product.delete()
            #     return

            created_count += 1

        # 导入
        for idx, item in enumerate(data):
            if limit and created_count >= limit:
                break
            try:
                import_one(item)
            except Exception:
                continue

        self.stdout.write(self.style.SUCCESS(f"导入完成：创建 {created_count} 条/读取 {total} 条"))

    def _map_category(self, raw: str) -> str:
        """根据商品标题和分类名称智能映射分类"""
        raw_lower = raw.lower()
        
        # 先检查预定义的别名映射
        for k, v in CATEGORY_ALIASES.items():
            if k.lower() in raw_lower:
                return v
        
        # 如果没找到，根据商品标题关键词智能判断（按优先级排序）
        # 智能穿戴类（必须在手机类之前，避免手表被误判为手机）
        if any(k in raw_lower for k in ["手表", "watch", "手环", "band", "智能手表", "智能手环", "gt3", "gt4", "gt5", "表盘", "watch fit", "apple watch"]):
            return "智能穿戴"
        # 数码配件类
        elif any(k in raw_lower for k in ["充电器", "数据线", "手机壳", "保护膜", "移动电源", "充电宝", "保护壳", "充电线", "typec", "lightning", "磁吸", "无线充"]):
            return "数码配件"
        # 存储设备类
        elif any(k in raw_lower for k in ["u盘", "移动硬盘", "内存卡", "ssd", "固态硬盘", "tf卡", "sd卡", "cf卡", "存储卡", "硬盘盒"]):
            return "存储设备"
        # 智能家居类
        elif any(k in raw_lower for k in ["智能音箱", "智能门锁", "智能摄像头", "智能开关", "小爱", "天猫精灵", "小度", "homepod", "nest", "智能灯", "智能插座"]):
            return "智能家居"
        # 游戏类（必须在手机类之前）
        elif any(k in raw_lower for k in ["switch", "ps5", "xbox", "游戏", "game", "playstation", "nintendo", "steam deck"]):
            return "游戏设备"
        # 相机类
        elif any(k in raw_lower for k in ["相机", "camera", "索尼a7", "索尼a", "尼康z", "尼康d", "佳能r", "佳能eos", "单反", "微单", "镜头", "富士", "无人机", "大疆", "dji", "云台"]):
            return "摄影摄像"
        # 手机类（必须在电脑类之前，避免被误判）
        elif any(k in raw_lower for k in ["iphone", "手机", "华为mate", "华为p", "小米", "oppo", "vivo", "三星", "荣耀", "一加", "realme", "红米"]) and "手表" not in raw_lower and "手环" not in raw_lower:
            return "手机数码"
        # 音频类（必须在手机类之前，避免耳机被误判）
        elif any(k in raw_lower for k in ["airpods", "耳机", "headphone", "音响", "speaker", "bose", "索尼wh", "索尼wf", "beats", "森海", "jbl", "linkbuds"]):
            return "耳机音响"
        # 平板类（必须在手机类之前）
        elif any(k in raw_lower for k in ["ipad", "平板", "tablet", "matepad", "pad air", "pad pro"]):
            return "平板/笔记本"
        # 键盘鼠标类（必须在电脑类之前）
        elif any(k in raw_lower for k in ["键盘", "keyboard", "鼠标", "mouse", "机械键盘", "机械轴", "ikbc", "罗技mx", "罗技m", "罗技g"]):
            return "电脑办公"
        # 显示器类（排除手机）
        elif any(k in raw_lower for k in ["显示器", "monitor", "屏幕", "屏", "aoc", "戴尔显示器", "lg显示器"]) and "手机" not in raw_lower:
            return "电脑办公"
        # 路由器类
        elif any(k in raw_lower for k in ["路由器", "router", "wifi", "ax", "ac", "小米路由器"]):
            return "电脑办公"
        # 电脑类（排除手机相关关键词）
        elif any(k in raw_lower for k in ["macbook", "笔记本", "电脑", "thinkpad", "laptop", "联想小新", "联想", "戴尔xps", "华硕", "xps"]) and "手机" not in raw_lower:
            return "电脑办公"
        # 默认返回手机数码
        else:
            return "手机数码"
