"""
导入现有机型数据和问卷步骤到模板系统
从 LOCAL_PRICE_TABLE 导入机型，从默认问卷步骤导入问卷内容
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from app.admin_api.models import (
    RecycleDeviceTemplate, RecycleQuestionTemplate, RecycleQuestionOption, AdminUser
)
try:
    from app.secondhand_app.price_service import LOCAL_PRICE_TABLE
except ImportError:
    LOCAL_PRICE_TABLE = {}

# 默认问卷步骤配置（从前端 RecycleEstimateWizard.vue 提取）
DEFAULT_QUESTIONS = [
    {
        'step_order': 1,
        'key': 'channel',
        'title': '购买渠道',
        'helper': '官方直营/运营商/第三方等',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'official', 'label': '官方/直营', 'desc': '官网/直营店', 'impact': '', 'option_order': 0},
            {'value': 'operator', 'label': '运营商/合约', 'desc': '', 'impact': '', 'option_order': 1},
            {'value': 'online', 'label': '第三方电商', 'desc': '', 'impact': '', 'option_order': 2},
            {'value': 'secondhand', 'label': '二手/转手', 'desc': '', 'impact': '', 'option_order': 3},
        ]
    },
    {
        'step_order': 2,
        'key': 'color',
        'title': '颜色',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'black', 'label': '黑/深色', 'desc': '', 'impact': '', 'option_order': 0},
            {'value': 'white', 'label': '白/浅色', 'desc': '', 'impact': '', 'option_order': 1},
            {'value': 'blue', 'label': '蓝/紫/冷色', 'desc': '', 'impact': '', 'option_order': 2},
            {'value': 'gold', 'label': '金/粉/暖色', 'desc': '', 'impact': '', 'option_order': 3},
            {'value': 'other', 'label': '其他颜色', 'desc': '', 'impact': '', 'option_order': 4},
        ]
    },
    {
        'step_order': 3,
        'key': 'storage',
        'title': '内存 / 存储',
        'helper': '选容量以便精准估价',
        'question_type': 'single',
        'is_required': True,
        'options': []  # 存储容量选项会从模板的 storages 字段动态生成
    },
    {
        'step_order': 4,
        'key': 'usage',
        'title': '使用情况',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'unopened', 'label': '全新未拆封', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'light', 'label': '几乎全新，使用很少', 'desc': '', 'impact': 'positive', 'option_order': 1},
            {'value': 'normal', 'label': '正常使用痕迹', 'desc': '', 'impact': 'minor', 'option_order': 2},
            {'value': 'heavy', 'label': '明显使用痕迹/重度使用', 'desc': '', 'impact': 'major', 'option_order': 3},
        ]
    },
    {
        'step_order': 5,
        'key': 'accessories',
        'title': '有无配件',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'full', 'label': '配件齐全（盒/充/线）', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'partial', 'label': '有部分配件', 'desc': '', 'impact': 'minor', 'option_order': 1},
            {'value': 'none', 'label': '仅裸机', 'desc': '', 'impact': 'minor', 'option_order': 2},
        ]
    },
    {
        'step_order': 6,
        'key': 'screen_appearance',
        'title': '屏幕外观',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'perfect', 'label': '完美无瑕', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'micro-scratch', 'label': '细微划痕', 'desc': '', 'impact': 'minor', 'option_order': 1},
            {'value': 'light-scratch', 'label': '轻微划痕', 'desc': '', 'impact': 'minor', 'option_order': 2},
            {'value': 'obvious-scratch', 'label': '明显划痕/磕碰', 'desc': '', 'impact': 'major', 'option_order': 3},
            {'value': 'broken', 'label': '碎裂/脱胶', 'desc': '', 'impact': 'critical', 'option_order': 4},
        ]
    },
    {
        'step_order': 7,
        'key': 'body',
        'title': '机身外壳',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'body-perfect', 'label': '完美无瑕', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'body-micro', 'label': '细微划痕', 'desc': '', 'impact': 'minor', 'option_order': 1},
            {'value': 'body-light', 'label': '轻微划痕/掉漆', 'desc': '', 'impact': 'minor', 'option_order': 2},
            {'value': 'body-obvious', 'label': '明显磕碰/掉漆', 'desc': '', 'impact': 'major', 'option_order': 3},
            {'value': 'body-crack', 'label': '碎裂/缺角', 'desc': '', 'impact': 'critical', 'option_order': 4},
        ]
    },
    {
        'step_order': 8,
        'key': 'display',
        'title': '屏幕显示',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'display-ok', 'label': '显示正常', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'display-spot', 'label': '色差/亮斑/坏点', 'desc': '', 'impact': 'minor', 'option_order': 1},
            {'value': 'display-shadow', 'label': '残影/烧屏', 'desc': '', 'impact': 'major', 'option_order': 2},
            {'value': 'display-leak', 'label': '漏液/花屏', 'desc': '', 'impact': 'critical', 'option_order': 3},
        ]
    },
    {
        'step_order': 9,
        'key': 'front_camera',
        'title': '前摄拍照',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'front-ok', 'label': '正常', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'front-spot', 'label': '有斑/坏点', 'desc': '', 'impact': 'major', 'option_order': 1},
            {'value': 'front-fail', 'label': '无法拍照/已维修', 'desc': '', 'impact': 'critical', 'option_order': 2},
        ]
    },
    {
        'step_order': 10,
        'key': 'rear_camera',
        'title': '后摄拍照',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'rear-ok', 'label': '正常', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'rear-spot', 'label': '有斑/坏点', 'desc': '', 'impact': 'major', 'option_order': 1},
            {'value': 'rear-fail', 'label': '无法拍照/已维修', 'desc': '', 'impact': 'critical', 'option_order': 2},
        ]
    },
    {
        'step_order': 11,
        'key': 'repair',
        'title': '维修情况（机身）',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'no-repair', 'label': '无拆修/无改', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'minor-repair', 'label': '后壳贴标/轻微溢胶', 'desc': '', 'impact': 'minor', 'option_order': 1},
            {'value': 'battery-repair', 'label': '维修或更换电池', 'desc': '', 'impact': 'major', 'option_order': 2},
            {'value': 'board-repair', 'label': '主板维修/扩容/进水', 'desc': '', 'impact': 'critical', 'option_order': 3},
        ]
    },
    {
        'step_order': 12,
        'key': 'screen_repair',
        'title': '屏幕维修情况',
        'helper': '',
        'question_type': 'single',
        'is_required': True,
        'options': [
            {'value': 'no-screen-repair', 'label': '无维修/无换屏', 'desc': '', 'impact': 'positive', 'option_order': 0},
            {'value': 'screen-repair', 'label': '已换屏/已维修', 'desc': '', 'impact': 'critical', 'option_order': 1},
        ]
    },
    {
        'step_order': 13,
        'key': 'functional',
        'title': '功能性问题（非必选，可多选）',
        'helper': '',
        'question_type': 'multi',
        'is_required': False,
        'options': [
            {'value': 'all_ok', 'label': '全部正常', 'desc': '未发现功能异常', 'impact': 'positive', 'option_order': 0},
            {'value': 'touch_issue', 'label': '触摸失灵/延迟', 'desc': '', 'impact': 'critical', 'option_order': 1},
            {'value': 'vibration_flash_issue', 'label': '振动/闪光灯异常', 'desc': '', 'impact': 'major', 'option_order': 2},
            {'value': 'biometric_issue', 'label': '指纹/面部识别异常', 'desc': '', 'impact': 'major', 'option_order': 3},
            {'value': 'audio_issue', 'label': '听筒/麦克风/扬声器异常', 'desc': '', 'impact': 'major', 'option_order': 4},
            {'value': 'sensor_issue', 'label': '重力/指南针等感应器异常', 'desc': '', 'impact': 'minor', 'option_order': 5},
            {'value': 'wifi_baseband_issue', 'label': 'WIFI异常/信号异常/不读卡/无基带', 'desc': '', 'impact': 'critical', 'option_order': 6},
            {'value': 'nfc_transit_issue', 'label': 'NFC异常/公交卡无法退出', 'desc': '', 'impact': 'major', 'option_order': 7},
            {'value': 'button_issue', 'label': '按键无反馈/失灵', 'desc': '', 'impact': 'major', 'option_order': 8},
            {'value': 'light_distance_sensor_issue', 'label': '光线、距离感应器异常', 'desc': '', 'impact': 'minor', 'option_order': 9},
            {'value': 'cannot_charge', 'label': '无法充电', 'desc': '', 'impact': 'critical', 'option_order': 10},
            {'value': 'water_damage', 'label': '机身进水', 'desc': '', 'impact': 'critical', 'option_order': 11},
        ]
    },
]


class Command(BaseCommand):
    help = '从 LOCAL_PRICE_TABLE 导入机型数据到模板系统，并创建默认问卷'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空现有模板数据（谨慎使用）',
        )
        parser.add_argument(
            '--device-type',
            type=str,
            help='只导入指定设备类型（如：手机、平板、笔记本）',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('清空现有模板数据...'))
            RecycleQuestionOption.objects.all().delete()
            RecycleQuestionTemplate.objects.all().delete()
            RecycleDeviceTemplate.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('已清空'))

        # 获取或创建管理员用户（用于 created_by）
        admin_user = AdminUser.objects.first()
        if not admin_user:
            self.stdout.write(self.style.WARNING('未找到管理员用户，created_by 将设置为 None'))

        device_types_to_import = [options['device_type']] if options['device_type'] else list(LOCAL_PRICE_TABLE.keys())

        total_templates = 0
        total_questions = 0
        total_options = 0

        for device_type in device_types_to_import:
            if device_type not in LOCAL_PRICE_TABLE:
                self.stdout.write(self.style.WARNING(f'设备类型 "{device_type}" 不存在于 LOCAL_PRICE_TABLE，跳过'))
                continue

            self.stdout.write(self.style.SUCCESS(f'\n导入设备类型: {device_type}'))

            device_data = LOCAL_PRICE_TABLE[device_type]
            for brand, models_dict in device_data.items():
                self.stdout.write(f'  品牌: {brand}')

                for model_name, storages_dict in models_dict.items():
                    # 获取存储容量列表
                    storages = sorted(storages_dict.keys())
                    
                    # 构建基础价格表（从价目表中提取）
                    # LOCAL_PRICE_TABLE 结构：{storage: price} 或 {storage: {condition: price}}
                    base_prices = {}
                    for storage, price_info in storages_dict.items():
                        base_price = None
                        if isinstance(price_info, dict):
                            # 如果是字典，优先使用 'good' 成色的价格作为基础价格
                            # 如果没有 'good'，使用第一个值
                            base_price = price_info.get('good') or (list(price_info.values())[0] if price_info.values() else None)
                        elif isinstance(price_info, (int, float)):
                            # 如果直接是数字，使用它作为基础价格（良好成色）
                            base_price = price_info
                        
                        if base_price and isinstance(base_price, (int, float)) and base_price > 0:
                            base_prices[storage] = float(base_price)

                    # 创建或获取机型模板
                    template, created = RecycleDeviceTemplate.objects.get_or_create(
                        device_type=device_type,
                        brand=brand,
                        model=model_name,
                        defaults={
                            'storages': storages,
                            'base_prices': base_prices,
                            'series': self._derive_series(model_name),
                            'is_active': True,
                            'created_by': admin_user,
                        }
                    )

                    if created:
                        total_templates += 1
                        self.stdout.write(f'    [OK] 创建模板: {model_name} (存储: {", ".join(storages)})')
                    else:
                        # 更新存储容量和基础价格
                        template.storages = storages
                        template.base_prices = base_prices
                        template.series = self._derive_series(model_name)
                        template.save()
                        self.stdout.write(f'    [UPDATE] 更新模板: {model_name} (存储: {", ".join(storages)}, 价格: {len(base_prices)}个)')

                    # 如果模板还没有问卷，创建默认问卷
                    if not template.questions.exists():
                        for q_data in DEFAULT_QUESTIONS:
                            # 如果是存储容量问题，动态生成选项
                            if q_data['key'] == 'storage':
                                question = RecycleQuestionTemplate.objects.create(
                                    device_template=template,
                                    step_order=q_data['step_order'],
                                    key=q_data['key'],
                                    title=q_data['title'],
                                    helper=q_data['helper'],
                                    question_type=q_data['question_type'],
                                    is_required=q_data['is_required'],
                                    is_active=True,
                                )
                                # 为存储容量问题创建选项
                                for storage in storages:
                                    RecycleQuestionOption.objects.create(
                                        question_template=question,
                                        value=storage.lower().replace('gb', 'gb').replace('tb', 'tb'),
                                        label=storage,
                                        desc='',
                                        impact='',
                                        option_order=storages.index(storage),
                                        is_active=True,
                                    )
                                    total_options += 1
                            else:
                                question = RecycleQuestionTemplate.objects.create(
                                    device_template=template,
                                    step_order=q_data['step_order'],
                                    key=q_data['key'],
                                    title=q_data['title'],
                                    helper=q_data['helper'],
                                    question_type=q_data['question_type'],
                                    is_required=q_data['is_required'],
                                    is_active=True,
                                )
                                total_questions += 1

                                # 创建选项
                                for opt_data in q_data['options']:
                                    RecycleQuestionOption.objects.create(
                                        question_template=question,
                                        value=opt_data['value'],
                                        label=opt_data['label'],
                                        desc=opt_data.get('desc', ''),
                                        impact=opt_data.get('impact', ''),
                                        option_order=opt_data['option_order'],
                                        is_active=True,
                                    )
                                    total_options += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n导入完成！\n'
            f'  机型模板: {total_templates} 个\n'
            f'  问卷问题: {total_questions} 个\n'
            f'  问卷选项: {total_options} 个'
        ))

    @staticmethod
    def _derive_series(model_name: str) -> str:
        """从型号名称推导系列"""
        import re
        m = re.search(r'(\d{2})', model_name)
        if m:
            return f"{m.group(1)}系列"
        return ''










