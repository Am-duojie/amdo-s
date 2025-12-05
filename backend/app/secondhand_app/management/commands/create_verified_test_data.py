"""
创建官方验商品测试数据
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from app.secondhand_app.models import Category, VerifiedProduct, VerifiedProductImage
import random

# 测试商品数据
TEST_PRODUCTS = [
    {
        "title": "Apple iPhone 15 Pro Max 256GB 深空黑色",
        "description": "官方验机，99成新，功能完好，电池健康度95%，原装充电器，包装盒齐全。",
        "price": 7899,
        "original_price": 9999,
        "condition": "like_new",
        "brand": "苹果",
        "model": "iPhone 15 Pro Max",
        "storage": "256GB",
        "screen_size": "6.7英寸",
        "battery_health": "95%",
        "charging_type": "Lightning",
        "category": "手机数码",
    },
    {
        "title": "华为 Mate 60 Pro 512GB 羽砂紫",
        "description": "官方验机，95成新，外观轻微使用痕迹，功能正常，支持5G，原装充电器。",
        "price": 5999,
        "original_price": 6999,
        "condition": "good",
        "brand": "华为",
        "model": "Mate 60 Pro",
        "storage": "512GB",
        "screen_size": "6.82英寸",
        "battery_health": "92%",
        "charging_type": "USB-C",
        "category": "手机数码",
    },
    {
        "title": "Apple MacBook Air M2 13英寸 8GB+256GB",
        "description": "官方验机，99成新，M2芯片，性能强劲，适合办公学习，原装充电器。",
        "price": 6999,
        "original_price": 8999,
        "condition": "like_new",
        "brand": "苹果",
        "model": "MacBook Air M2",
        "storage": "256GB",
        "screen_size": "13.3英寸",
        "battery_health": "98%",
        "charging_type": "MagSafe",
        "category": "电脑办公",
    },
    {
        "title": "iPad Pro 11英寸 M2 128GB WIFI版",
        "description": "官方验机，95成新，M2芯片，支持Apple Pencil，适合绘画和办公。",
        "price": 4999,
        "original_price": 6799,
        "condition": "good",
        "brand": "苹果",
        "model": "iPad Pro 11英寸",
        "storage": "128GB",
        "screen_size": "11英寸",
        "battery_health": "94%",
        "charging_type": "USB-C",
        "category": "平板/笔记本",
    },
    {
        "title": "Apple Watch Series 9 GPS+蜂窝 45mm",
        "description": "官方验机，99成新，功能完好，原装表带，包装盒齐全。",
        "price": 2999,
        "original_price": 3999,
        "condition": "like_new",
        "brand": "苹果",
        "model": "Watch Series 9",
        "storage": "32GB",
        "screen_size": "45mm",
        "battery_health": "96%",
        "charging_type": "磁吸充电",
        "category": "智能穿戴",
    },
    {
        "title": "AirPods Pro 2 主动降噪耳机",
        "description": "官方验机，99成新，功能完好，原装充电盒，包装盒齐全。",
        "price": 1299,
        "original_price": 1899,
        "condition": "like_new",
        "brand": "苹果",
        "model": "AirPods Pro 2",
        "storage": "",
        "screen_size": "",
        "battery_health": "95%",
        "charging_type": "Lightning",
        "category": "耳机音响",
    },
]


class Command(BaseCommand):
    help = "创建官方验商品测试数据"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="卖家用户名，默认admin"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="清空该用户的所有官方验商品"
        )

    def handle(self, *args, **options):
        username = options["username"]
        clear = options["clear"]

        # 获取或创建用户
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"}
        )
        if created:
            user.set_password("admin123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"创建用户: {username}"))
        else:
            self.stdout.write(f"使用现有用户: {username}")

        # 清空旧数据
        if clear:
            count = VerifiedProduct.objects.filter(seller=user).count()
            VerifiedProduct.objects.filter(seller=user).delete()
            self.stdout.write(self.style.WARNING(f"已清空 {count} 条旧数据"))

        # 确保分类存在
        categories = {}
        for cat_name in ["手机数码", "电脑办公", "平板/笔记本", "智能穿戴", "耳机音响"]:
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={"description": f"{cat_name}分类"}
            )
            categories[cat_name] = cat

        # 创建商品
        created_count = 0
        for product_data in TEST_PRODUCTS:
            category = categories.get(product_data["category"])
            if not category:
                self.stdout.write(
                    self.style.WARNING(f"分类不存在: {product_data['category']}")
                )
                continue

            product = VerifiedProduct.objects.create(
                seller=user,
                category=category,
                title=product_data["title"],
                description=product_data["description"],
                price=product_data["price"],
                original_price=product_data.get("original_price"),
                condition=product_data["condition"],
                status="active",
                location="全国",
                brand=product_data.get("brand", ""),
                model=product_data.get("model", ""),
                storage=product_data.get("storage", ""),
                screen_size=product_data.get("screen_size", ""),
                battery_health=product_data.get("battery_health", ""),
                charging_type=product_data.get("charging_type", ""),
            )

            # 创建占位图片（使用纯色图片）
            try:
                from PIL import Image
                import io

                # 创建占位图片
                img = Image.new('RGB', (400, 400), color=(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)))
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)

                image_file = ContentFile(img_io.read(), name=f"{product.id}_main.jpg")
                VerifiedProductImage.objects.create(
                    product=product,
                    image=image_file,
                    is_primary=True
                )
                created_count += 1
                self.stdout.write(f"  ✓ 创建: {product.title}")
            except ImportError:
                # 如果没有PIL，跳过图片
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ 创建: {product.title} (无图片，需要安装Pillow)")
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n完成！共创建 {created_count} 条测试数据")
        )

