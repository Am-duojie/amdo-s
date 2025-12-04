from django.core.management.base import BaseCommand
from app.secondhand_app.models import Product, ProductImage


class Command(BaseCommand):
    help = "清空所有商品数据"

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='确认删除所有商品数据',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '警告：此操作将删除所有商品数据！\n'
                    '如果确认删除，请添加 --confirm 参数'
                )
            )
            return

        # 统计数量
        product_count = Product.objects.count()
        image_count = ProductImage.objects.count()

        # 删除所有商品图片
        ProductImage.objects.all().delete()
        
        # 删除所有商品
        Product.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ 成功删除 {product_count} 个商品和 {image_count} 张图片'
            )
        )











