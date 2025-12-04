from django.core.management.base import BaseCommand
from app.secondhand_app.models import Category


class Command(BaseCommand):
    help = "添加闲鱼风格的数码产品分类"

    def handle(self, *args, **options):
        # 闲鱼风格的数码产品分类
        categories = [
            {
                "name": "手机数码",
                "description": "智能手机、功能机、手机配件等"
            },
            {
                "name": "摄影摄像",
                "description": "相机、镜头、无人机、云台等摄影设备"
            },
            {
                "name": "平板/笔记本",
                "description": "iPad、安卓平板、笔记本电脑等"
            },
            {
                "name": "电脑办公",
                "description": "台式机、显示器、键盘鼠标、路由器等"
            },
            {
                "name": "耳机音响",
                "description": "耳机、音响、音箱等音频设备"
            },
            {
                "name": "游戏设备",
                "description": "游戏机、游戏手柄、VR设备等"
            },
            {
                "name": "智能穿戴",
                "description": "智能手表、智能手环、运动手环等"
            },
            {
                "name": "数码配件",
                "description": "充电器、数据线、手机壳、保护膜、移动电源等"
            },
            {
                "name": "智能家居",
                "description": "智能音箱、智能门锁、智能摄像头、智能开关等"
            },
            {
                "name": "存储设备",
                "description": "U盘、移动硬盘、内存卡、SSD固态硬盘等"
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建分类: {cat_data["name"]}')
                )
            else:
                # 更新已存在分类的描述
                if category.description != cat_data["description"]:
                    category.description = cat_data["description"]
                    category.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ 更新分类: {cat_data["name"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'○ 分类已存在: {cat_data["name"]}')
                    )
        
        self.stdout.write(self.style.SUCCESS(
            f'\n完成！创建 {created_count} 个分类，更新 {updated_count} 个分类'
        ))

