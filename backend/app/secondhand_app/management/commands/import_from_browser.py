"""
从浏览器手动获取的数据导入命令
使用方法：
1. 在浏览器中打开爱回收商品详情页
2. 在浏览器控制台运行提取脚本获取数据
3. 将数据保存为JSON文件
4. 使用此命令导入
"""
import json
from pathlib import Path
from typing import Dict, Any

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
import requests
import time
import re

from app.secondhand_app.models import Category, VerifiedProduct, VerifiedProductImage

CATEGORY_MAPPING = {
    '手机': '手机数码',
    '电脑': '电脑办公',
    '平板': '平板/笔记本',
    '手表': '智能穿戴',
    '耳机': '耳机音响',
}

CONDITION_MAPPING = {
    '全新': 'new',
    '99新': 'like_new',
    '95新': 'good',
    '9成新': 'fair',
    '8成新': 'poor',
}


def safe_filename(name: str, default: str = "image") -> str:
    name = re.sub(r"[^\w\s-]", "", name).strip()
    return name[:30] or default


class Command(BaseCommand):
    help = "从浏览器获取的数据导入到数据库"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, help="JSON数据文件路径")
        parser.add_argument("--data", type=str, help="直接提供JSON数据（单条）")
        parser.add_argument("--username", type=str, default="aihuishou", help="作为卖家的用户名")
        parser.add_argument("--download-timeout", type=int, default=30, help="下载图片超时(秒)")

    def handle(self, *args, **options):
        file_path = options.get("file")
        data_str = options.get("data")
        username = options["username"]
        timeout = options["download_timeout"]

        # 获取数据
        if file_path:
            file = Path(file_path)
            if not file.exists():
                raise CommandError(f"文件不存在: {file_path}")
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        elif data_str:
            data = json.loads(data_str)
        else:
            raise CommandError("请提供 --file 或 --data 参数")

        if not isinstance(data, list):
            data = [data]

        # 确保用户存在
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"}
        )
        if created:
            user.set_password("pbkdf2_sha256$600000$dummy$dummy=")
            user.save()

        # 确保分类存在
        categories = {}
        for cat_name in CATEGORY_MAPPING.values():
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={"description": f"{cat_name}分类"}
            )
            categories[cat_name] = cat

        created_count = 0

        for item in data:
            try:
                with transaction.atomic():
                    title = (item.get("title") or "").strip()[:200]
                    if not title:
                        continue

                    category_name = item.get("category", "手机")
                    mapped_category = CATEGORY_MAPPING.get(category_name, "手机数码")
                    category = categories.get(mapped_category)

                    condition_text = item.get("condition", "good")
                    condition = CONDITION_MAPPING.get(condition_text, "good")
                    if condition not in CONDITION_MAPPING.values():
                        for key, value in CONDITION_MAPPING.items():
                            if key in str(condition_text):
                                condition = value
                                break
                        else:
                            condition = "good"

                    price = float(item.get("price", 0))
                    if price <= 0:
                        continue

                    original_price = item.get("original_price")
                    if original_price:
                        original_price = float(original_price)

                    product = VerifiedProduct.objects.create(
                        seller=user,
                        category=category,
                        title=title,
                        description=item.get("description", "")[:2000] or f"{title}，成色良好，功能正常。",
                        price=price,
                        original_price=original_price,
                        condition=condition,
                        status="active",
                        location="全国",
                        brand=item.get("brand", "")[:50] or "",
                        model=item.get("model", "")[:50] or "",
                        storage=item.get("storage", "")[:50] or "",
                        screen_size=item.get("screen_size", "")[:50] or "",
                        battery_health=item.get("battery_health", "")[:50] or "",
                        charging_type=item.get("charging_type", "")[:50] or "",
                    )

                    # 下载图片
                    all_images = []
                    if item.get("images") and isinstance(item.get("images"), list):
                        all_images.extend([x for x in item["images"] if isinstance(x, str) and x])
                    elif item.get("image"):
                        all_images.append(item.get("image"))

                    detail_images = item.get("detail_images", [])
                    if detail_images:
                        all_images.extend([img for img in detail_images if isinstance(img, str)])

                    downloaded_images = 0
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://m.aihuishou.com/',
                    }

                    for idx_img, img_url in enumerate(all_images[:15]):
                        try:
                            resp = requests.get(img_url, timeout=timeout, headers=headers, allow_redirects=True)
                            if resp.ok and resp.content and len(resp.content) > 1000:
                                content_type = resp.headers.get('content-type', '').lower()
                                if 'image' in content_type or img_url.lower().endswith(
                                    ('.jpg', '.jpeg', '.png', '.webp', '.gif')
                                ):
                                    base = safe_filename(title[:30] or "product")
                                    fname = f"{base}-{int(time.time()*1000)}-{idx_img}.jpg"
                                    image_file = ContentFile(resp.content, name=fname)
                                    VerifiedProductImage.objects.create(
                                        product=product,
                                        image=image_file,
                                        is_primary=(idx_img == 0)
                                    )
                                    downloaded_images += 1
                                    self.stdout.write(f"  ✓ 下载图片 {idx_img+1}")
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"  下载图片失败: {e}"))

                    # 如果没有图片，创建占位图
                    if downloaded_images == 0:
                        try:
                            from PIL import Image
                            import io
                            import random

                            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
                            img = Image.new("RGB", (400, 400), color=color)
                            img_io = io.BytesIO()
                            img.save(img_io, format="JPEG")
                            img_io.seek(0)

                            image_file = ContentFile(img_io.read(), name=f"{product.id}_main.jpg")
                            VerifiedProductImage.objects.create(
                                product=product,
                                image=image_file,
                                is_primary=True,
                            )
                        except ImportError:
                            pass

                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ 导入: {product.title}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"导入失败: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n完成！共导入 {created_count} 条数据"))

