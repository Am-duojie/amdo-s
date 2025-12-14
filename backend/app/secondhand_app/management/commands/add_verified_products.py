"""
添加官方验商品测试数据
使用方法: python manage.py add_verified_products
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from secondhand_app.models import VerifiedProduct, Category
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = '添加官方验商品测试数据'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始添加官方验商品测试数据...'))

        # 获取或创建测试用户
        seller, created = User.objects.get_or_create(
            username='verified_seller',
            defaults={
                'email': 'verified@example.com',
                'is_active': True
            }
        )
        if created:
            seller.set_password('password123')
            seller.save()
            self.stdout.write(self.style.SUCCESS(f'创建测试卖家: {seller.username}'))

        # 获取或创建分类
        category, _ = Category.objects.get_or_create(
            name='手机数码',
            defaults={'description': '手机、平板等数码产品'}
        )

        # 测试商品数据
        products_data = [
            {
                'title': 'Apple iPhone 14 Pro Max 256GB 深空黑 官方验货',
                'brand': 'Apple',
                'model': 'iPhone 14 Pro Max',
                'storage': '256GB',
                'color': '深空黑',
                'screen_size': '6.7英寸',
                'battery_health': '98%',
                'price': 6899.00,
                'original_price': 8999.00,
                'condition': 'like_new',
                'description': '''【官方验货】Apple iPhone 14 Pro Max 256GB 深空黑色

✅ 验货保障：
- 平台专业质检，100%正品保证
- 外观99成新，几乎无使用痕迹
- 功能完好，所有检测项通过
- 电池健康度98%，续航优秀

📱 产品亮点：
- A16仿生芯片，性能强劲
- 4800万像素主摄，拍照出色
- 灵动岛设计，交互体验升级
- 支持卫星通信，安全可靠

📦 包装配件：
- 原装充电线
- 取卡针
- 说明书

🔒 售后保障：
- 7天无理由退换
- 180天质保服务
- 支持验机复检''',
                'location': '北京市朝阳区',
                'tags': ['官方验货', '99新', '正品保证', '质保180天'],
                'inspection_result': 'pass',
                'inspection_note': '外观检测：99新，屏幕完美无划痕\n功能检测：全部通过\n电池健康：98%',
                'stock': 3
            },
            {
                'title': 'Apple iPhone 13 128GB 粉色 官方验货 95新',
                'brand': 'Apple',
                'model': 'iPhone 13',
                'storage': '128GB',
                'color': '粉色',
                'screen_size': '6.1英寸',
                'battery_health': '92%',
                'price': 3899.00,
                'original_price': 5999.00,
                'condition': 'good',
                'description': '''【官方验货】Apple iPhone 13 128GB 粉色

✅ 验货保障：
- 平台专业质检，正品保证
- 外观95成新，轻微使用痕迹
- 功能完好，检测全部通过
- 电池健康度92%

📱 产品特点：
- A15芯片，流畅运行
- 双摄系统，拍照清晰
- 超视网膜XDR显示屏
- 支持5G网络

📦 包装配件：
- 充电线
- 取卡针

🔒 售后保障：
- 7天无理由退换
- 90天质保服务''',
                'location': '上海市浦东新区',
                'tags': ['官方验货', '95新', '性价比高'],
                'inspection_result': 'pass',
                'inspection_note': '外观检测：95新，背面有轻微划痕\n功能检测：全部正常\n电池健康：92%',
                'stock': 5
            },
            {
                'title': 'Apple iPhone 12 Pro 256GB 海蓝色 官方验货',
                'brand': 'Apple',
                'model': 'iPhone 12 Pro',
                'storage': '256GB',
                'color': '海蓝色',
                'screen_size': '6.1英寸',
                'battery_health': '89%',
                'price': 3599.00,
                'original_price': 7999.00,
                'condition': 'good',
                'description': '''【官方验货】Apple iPhone 12 Pro 256GB 海蓝色

✅ 验货保障：
- 官方质检认证
- 外观95新
- 功能完好
- 电池健康89%

📱 产品亮点：
- A14仿生芯片
- 三摄系统+激光雷达
- 超瓷晶面板
- 支持5G

📦 配件齐全

🔒 90天质保''',
                'location': '深圳市南山区',
                'tags': ['官方验货', 'Pro版本', '三摄'],
                'inspection_result': 'pass',
                'inspection_note': '外观检测：95新\n功能检测：正常\n电池健康：89%',
                'stock': 2
            },
            {
                'title': 'Apple iPad Air 5 256GB WiFi版 星光色 官方验货',
                'brand': 'Apple',
                'model': 'iPad Air 5',
                'storage': '256GB',
                'color': '星光色',
                'screen_size': '10.9英寸',
                'battery_health': '96%',
                'price': 4299.00,
                'original_price': 5499.00,
                'condition': 'like_new',
                'description': '''【官方验货】Apple iPad Air 5 256GB WiFi版 星光色

✅ 验货保障：
- 平台专业质检
- 外观99新，几乎全新
- 功能完美
- 电池健康96%

📱 产品特点：
- M1芯片，性能强大
- 10.9英寸液态视网膜显示屏
- 支持Apple Pencil 2
- 适合办公学习

📦 包装配件：
- 原装充电器
- 数据线

🔒 180天质保''',
                'location': '广州市天河区',
                'tags': ['官方验货', '平板', 'M1芯片', '99新'],
                'inspection_result': 'pass',
                'inspection_note': '外观检测：99新，无划痕\n功能检测：完美\n电池健康：96%',
                'stock': 4
            },
            {
                'title': 'Apple iPhone 15 Pro 256GB 原色钛金属 官方验货',
                'brand': 'Apple',
                'model': 'iPhone 15 Pro',
                'storage': '256GB',
                'color': '原色钛金属',
                'screen_size': '6.1英寸',
                'battery_health': '100%',
                'price': 7899.00,
                'original_price': 8999.00,
                'condition': 'new',
                'description': '''【官方验货】Apple iPhone 15 Pro 256GB 原色钛金属

✅ 验货保障：
- 全新未激活
- 官方质检认证
- 原封未拆
- 电池健康100%

📱 产品亮点：
- A17 Pro芯片，3nm工艺
- 钛金属边框，轻盈坚固
- 4800万像素主摄
- 动作按钮，自定义操作
- USB-C接口

📦 全新包装：
- 原装配件齐全
- 未激活

🔒 1年官方质保''',
                'location': '北京市海淀区',
                'tags': ['官方验货', '全新', '未激活', 'Pro版本'],
                'inspection_result': 'pass',
                'inspection_note': '全新未激活，原封包装',
                'stock': 1
            },
            {
                'title': 'Apple MacBook Air M2 256GB 午夜色 官方验货',
                'brand': 'Apple',
                'model': 'MacBook Air M2',
                'storage': '256GB',
                'color': '午夜色',
                'screen_size': '13.6英寸',
                'battery_health': '95%',
                'price': 7299.00,
                'original_price': 9499.00,
                'condition': 'like_new',
                'description': '''【官方验货】Apple MacBook Air M2 256GB 午夜色

✅ 验货保障：
- 官方质检认证
- 外观99新
- 功能完美
- 电池循环次数少于50次

💻 产品特点：
- M2芯片，性能强劲
- 13.6英寸液态视网膜显示屏
- 轻薄便携，仅1.24kg
- 续航长达18小时

📦 包装配件：
- 原装充电器
- 数据线

🔒 180天质保''',
                'location': '杭州市西湖区',
                'tags': ['官方验货', '笔记本', 'M2芯片', '99新'],
                'inspection_result': 'pass',
                'inspection_note': '外观检测：99新\n功能检测：完美\n电池循环：48次',
                'stock': 2
            }
        ]

        created_count = 0
        for data in products_data:
            # 移除不属于模型的字段
            color = data.pop('color', '')  # VerifiedProduct 模型没有 color 字段
            
            # 检查是否已存在
            existing = VerifiedProduct.objects.filter(
                title=data['title']
            ).first()
            
            if existing:
                self.stdout.write(self.style.WARNING(f'商品已存在: {data["title"]}'))
                continue

            # 创建商品 - 使用原始 SQL 以支持数据库中存在但模型中不存在的字段
            from django.db import connection
            import json
            
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO secondhand_app_verifiedproduct 
                    (seller_id, category_id, title, description, price, original_price, 
                     `condition`, status, location, brand, model, storage, screen_size, 
                     battery_health, charging_type, inspection_result, inspection_note, 
                     stock, tags, pricing_coefficient, source_tag, created_at, updated_at, 
                     view_count, sales_count, verified_at, inspection_date, inspection_staff, 
                     published_at, cover_image, detail_images, inspection_reports,
                     contact_phone, contact_wechat, shop_id, verified_by_id, removed_reason)
                    VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                     1.0, 'manual', NOW(), NOW(), %s, %s, %s, %s, %s, %s, '', '[]', '[]', '', '', NULL, NULL, '')
                    """,
                    [
                        seller.id, category.id, data['title'], data['description'],
                        data['price'], data.get('original_price'), data['condition'],
                        'active', data['location'], data['brand'], data['model'],
                        data['storage'], data['screen_size'], data['battery_health'],
                        'Lightning' if 'iPhone' in data['model'] and '15' not in data['model'] else 'USB-C',
                        data['inspection_result'], data['inspection_note'], data['stock'],
                        json.dumps(data['tags']), random.randint(100, 1000), random.randint(0, 10),
                        datetime.now() - timedelta(days=random.randint(1, 30)),
                        datetime.now().date() - timedelta(days=random.randint(1, 30)),
                        '张质检', datetime.now() - timedelta(days=random.randint(1, 15))
                    ]
                )
                product_id = cursor.lastrowid
            
            # 重新获取创建的对象
            product = VerifiedProduct.objects.get(id=product_id)

            # 添加封面图（使用占位图）
            product.cover_image = f'https://via.placeholder.com/600x600/667eea/ffffff?text={product.brand}+{product.model}'
            
            # 添加详情图
            product.detail_images = [
                f'https://via.placeholder.com/800x600/667eea/ffffff?text=Detail+1',
                f'https://via.placeholder.com/800x600/764ba2/ffffff?text=Detail+2',
                f'https://via.placeholder.com/800x600/f093fb/ffffff?text=Detail+3',
            ]
            
            # 添加质检报告（模拟）
            product.inspection_reports = [
                {
                    'name': '外观检测报告',
                    'url': '#',
                    'date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                },
                {
                    'name': '功能检测报告',
                    'url': '#',
                    'date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                }
            ]
            
            product.save()
            created_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'✓ 创建商品: {product.title}'))

        self.stdout.write(self.style.SUCCESS(f'\n成功添加 {created_count} 个官方验商品！'))
        self.stdout.write(self.style.SUCCESS('可以访问前端页面查看效果'))
