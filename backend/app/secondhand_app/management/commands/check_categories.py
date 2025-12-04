from django.core.management.base import BaseCommand
from app.secondhand_app.models import Product, Category
from django.db.models import Q


class Command(BaseCommand):
    help = "检查所有商品的分类是否正确"

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='自动修复误分类的商品',
        )

    def handle(self, *args, **options):
        fix = options['fix']
        
        # 获取所有分类
        categories = {}
        for cat in Category.objects.all():
            categories[cat.name] = cat
        
        # 检查规则：定义每个分类应该包含和不应该包含的关键词
        # 注意：should_not_contain 是严格禁止的，如果出现这些词，说明分类错误
        category_rules = {
            '手机数码': {
                'should_contain': ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo', '三星', '荣耀', '一加', 'realme', '红米'],
                'should_not_contain': ['笔记本', '电脑', 'laptop', 'thinkpad', 'macbook', '相机', 'camera', '镜头', '单反', '微单', 'airpods', '耳机', 'headphone', 'switch', 'ps5', 'xbox', 'playstation']
            },
            '电脑办公': {
                'should_contain': ['笔记本', '电脑', 'thinkpad', 'laptop', 'macbook', '键盘', 'keyboard', '鼠标', 'mouse', '显示器', 'monitor', '路由器', 'router'],
                'should_not_contain': ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo', '相机', 'camera', '镜头', '单反', '微单', 'airpods', '耳机', 'headphone']
            },
            '摄影摄像': {
                'should_contain': ['相机', 'camera', '镜头', '单反', '微单', '无人机', 'drone', '大疆', 'dji', '云台', 'gimbal'],
                'should_not_contain': ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo', '笔记本', '电脑', 'laptop', 'thinkpad', 'macbook', 'airpods', '耳机', 'headphone']
            },
            '游戏设备': {
                'should_contain': ['switch', 'ps5', 'xbox', 'playstation', 'nintendo', 'steam deck'],
                'should_not_contain': ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo', '笔记本', '电脑', 'thinkpad', 'macbook', '相机', 'camera']
            },
            '耳机音响': {
                'should_contain': ['airpods', '耳机', 'headphone', '音响', 'speaker', 'bose', '索尼wh', '索尼wf', 'beats', '森海', 'jbl'],
                'should_not_contain': ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo', '笔记本', '电脑', 'thinkpad', 'macbook', '相机', 'camera']
            },
            '智能穿戴': {
                'should_contain': ['手表', 'watch', '手环', 'band', '智能手表', '智能手环', 'gt3', 'gt4', 'gt5', '表盘', 'watch fit', 'apple watch'],
                'should_not_contain': ['笔记本', '电脑', 'laptop', 'thinkpad', 'macbook', '相机', 'camera']
            },
            '数码配件': {
                'should_contain': ['充电器', '数据线', '手机壳', '保护膜', '移动电源', '充电宝', '保护壳', '充电线', 'typec', 'lightning', '磁吸', '无线充'],
                'should_not_contain': ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo', '笔记本', '电脑', 'thinkpad', 'macbook', '相机', 'camera', '镜头', '单反', '微单']
            },
            '平板/笔记本': {
                'should_contain': ['ipad', '平板', 'tablet', 'matepad', 'pad air', 'pad pro'],
                'should_not_contain': ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo', 'thinkpad', 'laptop', 'macbook', '笔记本', '电脑']
            },
            '智能家居': {
                'should_contain': ['智能音箱', '智能门锁', '智能摄像头', '智能开关', '小爱', '天猫精灵', '小度', 'homepod', 'nest', '智能灯', '智能插座'],
                'should_not_contain': ['手机', 'iphone', '笔记本', '电脑', 'thinkpad', 'macbook']
            },
            '存储设备': {
                'should_contain': ['u盘', '移动硬盘', '内存卡', 'ssd', '固态硬盘', 'tf卡', 'sd卡', 'cf卡', '存储卡', '硬盘盒', 'nvme'],
                'should_not_contain': ['手机', 'iphone', '笔记本', '电脑', 'thinkpad', 'macbook', 'laptop']
            },
        }
        
        # 获取所有活跃商品
        products = Product.objects.filter(status='active').select_related('category')
        
        errors = []
        total_checked = 0
        
        for product in products:
            total_checked += 1
            if not product.category:
                errors.append({
                    'product': product,
                    'current': '无分类',
                    'issue': '商品没有分类',
                    'suggested': None
                })
                continue
            
            category_name = product.category.name
            if category_name not in category_rules:
                continue
            
            rules = category_rules[category_name]
            title_lower = product.title.lower()
            
            # 检查是否包含不应该包含的关键词（严格检查）
            should_not_contain = rules.get('should_not_contain', [])
            for keyword in should_not_contain:
                if keyword in title_lower:
                    # 特殊情况排除
                    # 1. 无人机标题中的"无需手机"是正常的
                    if category_name == '摄影摄像' and '无人机' in title_lower and ('无需手机' in title_lower or '不需要手机' in title_lower):
                        continue
                    
                    # 2. 数码配件中的"手机壳"等配件是正常的
                    if category_name == '数码配件' and any(k in title_lower for k in ['充电器', '数据线', '手机壳', '保护膜', '移动电源', '充电宝', '保护壳', '充电线', 'typec', 'lightning']):
                        continue
                    
                    # 3. 游戏设备中的游戏账号、模拟器可能提到手机/电脑，但商品本身是游戏相关
                    if category_name == '游戏设备' and any(k in title_lower for k in ['游戏', 'game', '模拟器', '账号', 'switch', 'ps5', 'xbox', 'playstation']):
                        # 但如果明确是手机或电脑商品（不是游戏相关），还是错误的
                        if any(k in title_lower for k in ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo']) and not any(k in title_lower for k in ['游戏', 'game', '模拟器', '账号', 'switch']):
                            suggested_category = self._find_correct_category(title_lower, category_rules)
                            if suggested_category != category_name:
                                errors.append({
                                    'product': product,
                                    'current': category_name,
                                    'issue': f'包含不应该包含的关键词: "{keyword}"',
                                    'suggested': suggested_category
                                })
                        continue
                    
                    # 4. 耳机音响中的"手机"可能是描述使用场景，但如果标题明确是手机商品，则是错误的
                    if category_name == '耳机音响' and '手机' in title_lower:
                        # 检查是否真的是手机商品
                        if any(k in title_lower for k in ['手机', 'iphone', '华为mate', '华为p', '小米', 'oppo', 'vivo']) and not any(k in title_lower for k in ['airpods', '耳机', 'headphone', '音响', 'speaker']):
                            suggested_category = self._find_correct_category(title_lower, category_rules)
                            if suggested_category != category_name:
                                errors.append({
                                    'product': product,
                                    'current': category_name,
                                    'issue': f'包含不应该包含的关键词: "{keyword}"',
                                    'suggested': suggested_category
                                })
                        continue
                    
                    # 找到应该属于的分类
                    suggested_category = self._find_correct_category(title_lower, category_rules)
                    # 只有当建议分类与当前分类不同时才报错
                    if suggested_category != category_name:
                        errors.append({
                            'product': product,
                            'current': category_name,
                            'issue': f'包含不应该包含的关键词: "{keyword}"',
                            'suggested': suggested_category
                        })
                    break
        
        # 输出检查结果
        self.stdout.write(self.style.SUCCESS(f'\n检查完成！共检查 {total_checked} 个商品\n'))
        
        if errors:
            self.stdout.write(self.style.WARNING(f'发现 {len(errors)} 个可能误分类的商品:\n'))
            
            # 按当前分类分组显示
            by_category = {}
            for error in errors:
                cat = error['current']
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(error)
            
            for cat_name, cat_errors in sorted(by_category.items()):
                self.stdout.write(self.style.ERROR(f'\n【{cat_name}】分类中的问题商品 ({len(cat_errors)}个):'))
                for i, error in enumerate(cat_errors[:10], 1):  # 只显示前10个
                    self.stdout.write(
                        f'  {i}. {error["product"].title[:60]}...'
                    )
                    self.stdout.write(
                        f'     问题: {error["issue"]}'
                    )
                    if error['suggested']:
                        self.stdout.write(
                            f'     建议分类: {error["suggested"]}'
                        )
                if len(cat_errors) > 10:
                    self.stdout.write(f'     ... 还有 {len(cat_errors) - 10} 个商品')
            
            if fix:
                self.stdout.write(self.style.WARNING('\n开始自动修复...'))
                fixed_count = 0
                for error in errors:
                    if error['suggested'] and error['suggested'] in categories:
                        error['product'].category = categories[error['suggested']]
                        error['product'].save()
                        fixed_count += 1
                self.stdout.write(self.style.SUCCESS(f'\n✓ 成功修复 {fixed_count} 个商品的分类'))
            else:
                self.stdout.write(self.style.WARNING('\n提示: 使用 --fix 参数可以自动修复这些误分类'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ 所有商品分类都正确！'))
    
    def _find_correct_category(self, title_lower, category_rules):
        """根据标题找到正确的分类"""
        # 按优先级检查各个分类（与 fix_categories.py 逻辑一致）
        # 智能穿戴类（必须在最前面）
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
        # 游戏类
        elif any(k in title_lower for k in ["switch", "ps5", "xbox", "playstation", "nintendo", "steam deck"]) and not any(k in title_lower for k in ["手机", "iphone", "华为mate", "华为p", "小米", "oppo", "vivo"]):
            return "游戏设备"
        # 相机类
        elif any(k in title_lower for k in ["相机", "camera", "索尼a7", "索尼a", "a7m", "a7r", "a7s", "尼康z", "尼康d", "佳能r", "佳能eos", "单反", "微单", "镜头", "富士", "无人机", "drone", "大疆", "dji", "云台"]):
            return "摄影摄像"
        # 音频类
        elif any(k in title_lower for k in ["airpods", "耳机", "headphone", "音响", "speaker", "bose", "索尼wh", "索尼wf", "beats", "森海", "jbl", "linkbuds"]):
            return "耳机音响"
        # 平板类
        elif any(k in title_lower for k in ["ipad", "平板", "tablet", "matepad", "pad air", "pad pro"]):
            return "平板/笔记本"
        # 手机类
        elif any(k in title_lower for k in ["iphone", "手机", "华为mate", "华为p", "小米", "oppo", "vivo", "三星", "荣耀", "一加", "realme", "红米"]) and "手表" not in title_lower and "手环" not in title_lower:
            return "手机数码"
        # 电脑类
        elif any(k in title_lower for k in ["macbook", "笔记本", "电脑", "thinkpad", "laptop", "联想小新", "联想", "戴尔xps", "华硕", "xps", "键盘", "keyboard", "鼠标", "mouse", "显示器", "monitor", "路由器", "router"]):
            return "电脑办公"
        # 默认
        else:
            return "手机数码"

