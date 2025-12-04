import re
from django.core.management.base import BaseCommand
from app.secondhand_app.models import Product, Category


class Command(BaseCommand):
    help = "修复商品分类，根据商品标题重新分配正确的分类"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示会修改的商品，不实际修改',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 获取所有分类
        categories = {}
        for cat in Category.objects.all():
            categories[cat.name] = cat
        
        # 确保所有分类都存在
        needed_categories = [
            "手机数码", "摄影摄像", "平板/笔记本", 
            "电脑办公", "耳机音响", "游戏设备",
            "智能穿戴", "数码配件", "智能家居", "存储设备"
        ]
        for name in needed_categories:
            if name not in categories:
                cat, _ = Category.objects.get_or_create(name=name, defaults={"description": name})
                categories[name] = cat
        
        # 获取所有商品
        products = Product.objects.all()
        fixed_count = 0
        
        for product in products:
            title_lower = product.title.lower()
            old_category = product.category.name if product.category else "无"
            new_category_name = self._map_category(product.title, title_lower)
            
            if new_category_name and new_category_name in categories:
                new_category = categories[new_category_name]
                
                # 如果分类不同，需要更新
                if not product.category or product.category.name != new_category_name:
                    fixed_count += 1
                    if dry_run:
                        self.stdout.write(
                            f"将修改: {product.title[:40]}... "
                            f"从 [{old_category}] -> [{new_category_name}]"
                        )
                    else:
                        product.category = new_category
                        product.save()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n预览模式：共找到 {fixed_count} 个需要修改的商品"))
            self.stdout.write(self.style.WARNING("运行时不加 --dry-run 参数来实际修改"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✓ 成功修复 {fixed_count} 个商品的分类"))

    def _map_category(self, title: str, title_lower: str) -> str:
        """根据商品标题智能映射分类"""
        # 优先匹配更具体的分类，避免误判
        
        # 跳过无效标题
        if len(title.strip()) < 5 or "累计降价" in title or title.startswith("累计"):
            return "手机数码"  # 无效标题默认分类
        
        # 智能穿戴类（必须在最前面，避免被其他分类误判）
        if any(k in title_lower for k in ["手表", "watch", "手环", "band", "智能手表", "智能手环", "gt3", "gt4", "gt5", "表盘", "watch fit", "apple watch"]):
            return "智能穿戴"
        # 数码配件类
        elif any(k in title_lower for k in ["充电器", "数据线", "手机壳", "保护膜", "移动电源", "充电宝", "保护壳", "充电线", "typec", "lightning", "磁吸", "无线充", "充电头", "快充"]):
            return "数码配件"
        # 存储设备类
        elif any(k in title_lower for k in ["u盘", "移动硬盘", "内存卡", "ssd", "固态硬盘", "tf卡", "sd卡", "cf卡", "存储卡", "硬盘盒", "nvme"]):
            return "存储设备"
        # 智能家居类
        elif any(k in title_lower for k in ["智能音箱", "智能门锁", "智能摄像头", "智能开关", "小爱", "天猫精灵", "小度", "homepod", "nest", "智能灯", "智能插座", "智能窗帘"]):
            return "智能家居"
        # 无人机类（必须在最前面，避免被其他分类误判）
        elif any(k in title_lower for k in ["无人机", "drone", "大疆", "dji", "云台", "gimbal", "航拍"]):
            return "摄影摄像"
        # 游戏类（必须在前面，避免被手机误判）
        elif any(k in title_lower for k in ["switch", "ps5", "xbox", "playstation", "nintendo", "模拟器", "游戏账号", "第五人格", "游戏", "yuzu", "steam deck"]):
            return "游戏设备"
        # 相机类（包括索尼A7系列）
        elif any(k in title_lower for k in ["相机", "camera", "索尼a7", "索尼a", "a7m", "a7r", "a7s", "尼康z", "尼康d", "佳能r", "佳能eos", "单反", "微单", "镜头", "富士", "快门", "全画幅", "机身"]):
            return "摄影摄像"
        # 手机类（必须在电脑类之前，避免被误判）
        elif any(k in title_lower for k in ["iphone", "手机", "华为mate", "华为p", "小米", "oppo", "vivo", "三星", "荣耀", "一加", "realme", "红米"]) and "手表" not in title_lower and "手环" not in title_lower:
            return "手机数码"
        # 键盘鼠标类（必须在电脑类之前）
        elif any(k in title_lower for k in ["键盘", "keyboard", "鼠标", "mouse", "机械键盘", "机械轴", "ikbc", "罗技mx", "罗技m", "罗技g", "青轴", "红轴", "茶轴"]):
            return "电脑办公"
        # 显示器类
        elif any(k in title_lower for k in ["显示器", "monitor", "屏幕", "屏", "aoc", "戴尔显示器", "lg显示器", "24寸", "27寸", "显示器"]) and "手机" not in title_lower:
            return "电脑办公"
        # 路由器类
        elif any(k in title_lower for k in ["路由器", "router", "wifi", "ax", "ac", "小米路由器"]):
            return "电脑办公"
        # 音频类（必须在手机类之前，避免耳机被误判为手机）
        elif any(k in title_lower for k in ["airpods", "耳机", "headphone", "音响", "speaker", "bose", "索尼wh", "索尼wf", "beats", "森海", "jbl", "linkbuds"]):
            return "耳机音响"
        # 平板类（必须在手机类之前）
        elif any(k in title_lower for k in ["ipad", "平板", "tablet", "matepad", "pad air", "pad pro", "vivo pad"]):
            return "平板/笔记本"
        # 电脑类（排除手机相关关键词）
        elif any(k in title_lower for k in ["macbook", "笔记本", "电脑", "thinkpad", "laptop", "联想小新", "联想", "戴尔xps", "华硕", "xps"]) and "手机" not in title_lower:
            return "电脑办公"
        # 默认返回手机数码（但应该尽量匹配到具体分类）
        else:
            return "手机数码"

