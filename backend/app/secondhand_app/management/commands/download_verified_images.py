"""
为官方验商品下载图片的命令
从爱回收等网站获取图片并下载到本地
"""
import re
import time
from pathlib import Path
from typing import List

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.db import transaction
import requests

from app.secondhand_app.models import VerifiedProduct, VerifiedProductImage


def safe_filename(name: str, default: str = "image") -> str:
    """生成安全的文件名"""
    name = re.sub(r"[^\w\s-]", "", name).strip()
    return name[:30] or default


class Command(BaseCommand):
    help = "为官方验商品下载图片"

    def add_arguments(self, parser):
        parser.add_argument(
            "--product-id",
            type=int,
            help="指定商品ID，如果不指定则处理所有没有图片的商品"
        )
        parser.add_argument(
            "--image-urls",
            type=str,
            nargs="+",
            help="图片URL列表"
        )
        parser.add_argument(
            "--username",
            type=str,
            help="只处理指定用户的商品"
        )

    def handle(self, *args, **options):
        product_id = options.get("product_id")
        image_urls = options.get("image_urls") or []
        username = options.get("username")

        # 如果提供了图片URL，直接下载
        if image_urls:
            if not product_id:
                raise CommandError("提供图片URL时必须指定商品ID")
            
            try:
                product = VerifiedProduct.objects.get(id=product_id)
            except VerifiedProduct.DoesNotExist:
                raise CommandError(f"商品不存在: {product_id}")
            
            self.download_images_for_product(product, image_urls)
            return

        # 否则处理没有图片的商品
        queryset = VerifiedProduct.objects.filter(images__isnull=True).distinct()
        
        if product_id:
            queryset = queryset.filter(id=product_id)
        if username:
            queryset = queryset.filter(seller__username=username)

        products = queryset[:50]  # 最多处理50个商品
        
        if not products.exists():
            self.stdout.write(self.style.SUCCESS("所有商品都有图片了！"))
            return

        self.stdout.write(f"找到 {products.count()} 个没有图片的商品")
        
        # 为每个商品创建占位图片
        for product in products:
            self.create_placeholder_image(product)

    def download_images_for_product(self, product: VerifiedProduct, image_urls: List[str]):
        """为指定商品下载图片"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://m.aihuishou.com/",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        }
        
        downloaded_count = 0
        for idx, img_url in enumerate(image_urls[:10]):  # 最多下载10张
            try:
                resp = requests.get(img_url, timeout=20, headers=headers, allow_redirects=True)
                
                if resp.ok and resp.content and len(resp.content) > 1000:
                    content_type = resp.headers.get("content-type", "").lower()
                    if "image" in content_type or img_url.lower().endswith(
                        (".jpg", ".jpeg", ".png", ".webp", ".gif")
                    ):
                        base = safe_filename(product.title[:30] or "product")
                        fname = f"{base}-{int(time.time()*1000)}-{idx}.jpg"
                        image_file = ContentFile(resp.content, name=fname)
                        VerifiedProductImage.objects.create(
                            product=product,
                            image=image_file,
                            is_primary=(idx == 0),
                        )
                        downloaded_count += 1
                        self.stdout.write(f"  ✓ 下载图片 {idx+1}: {fname}")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ✗ 下载图片失败 {img_url}: {e}")
                )

        if downloaded_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"共下载 {downloaded_count} 张图片")
            )

    def create_placeholder_image(self, product: VerifiedProduct):
        """为商品创建占位图片"""
        try:
            from PIL import Image
            import io
            import random

            # 创建占位图片（随机颜色）
            color = (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255)
            )
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
            self.stdout.write(f"  ✓ 创建占位图片: {product.title}")
        except ImportError:
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠ 跳过: {product.title} (需要安装Pillow: pip install Pillow)"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ 创建失败: {product.title} - {e}")
            )

