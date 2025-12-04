"""
更新价格数据库的管理命令
用于定期更新设备价格数据
"""
from django.core.management.base import BaseCommand
from app.secondhand_app.price_model import price_model
import json
import os


class Command(BaseCommand):
    help = "更新价格数据库"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='从JSON文件导入价格数据',
        )
        parser.add_argument(
            '--export',
            type=str,
            help='导出当前价格数据到JSON文件',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='列出所有支持的品牌和型号',
        )

    def handle(self, *args, **options):
        if options['export']:
            self.export_prices(options['export'])
        elif options['file']:
            self.import_prices(options['file'])
        elif options['list']:
            self.list_prices()
        else:
            self.stdout.write(self.style.WARNING('请指定操作：--export, --file, 或 --list'))

    def export_prices(self, filename):
        """导出价格数据到JSON文件"""
        data = price_model.price_database
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f'✓ 价格数据已导出到: {filename}'))

    def import_prices(self, filename):
        """从JSON文件导入价格数据"""
        if not os.path.exists(filename):
            self.stdout.write(self.style.ERROR(f'文件不存在: {filename}'))
            return
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新价格数据库
        price_model.price_database.update(data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ 价格数据已从 {filename} 导入'))
        self.stdout.write(self.style.WARNING('注意：需要重启服务才能生效'))

    def list_prices(self):
        """列出所有支持的品牌和型号"""
        self.stdout.write(self.style.SUCCESS('\n支持的品牌和型号：\n'))
        
        for brand, models in price_model.price_database.items():
            self.stdout.write(f'\n【{brand}】')
            for model, storages in models.items():
                storage_list = ', '.join(storages.keys())
                self.stdout.write(f'  - {model}: {storage_list}')

