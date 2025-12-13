from app.secondhand_app.models import Product

print('详细验证分类修复结果：')
print('=' * 60)

# 1. 验证之前错误的具体商品
print('\n1. 验证之前错误的具体商品：')

# 验证ID为1594的大疆无人机
product = Product.objects.get(id=1594)
print(f'  商品1594：{product.title[:40]}...')
print(f'    之前分类：台式电脑 -> 现在分类：{product.category.name}')

# 验证ID为1592的GX无人机
product = Product.objects.get(id=1592)
print(f'  商品1592：{product.title[:40]}...')
print(f'    之前分类：手机 -> 现在分类：{product.category.name}')

# 验证ID为1567的蓝牙键盘
product = Product.objects.get(id=1567)
print(f'  商品1567：{product.title[:40]}...')
print(f'    之前分类：其他数码 -> 现在分类：{product.category.name}')

# 验证ID为1566的机械键盘
product = Product.objects.get(id=1566)
print(f'  商品1566：{product.title[:40]}...')
print(f'    之前分类：其他数码 -> 现在分类：{product.category.name}')

# 2. 统计各分类商品数量
print('\n2. 各分类商品数量：')
from django.db.models import Count
category_counts = Product.objects.values('category__name').annotate(count=Count('category__name')).order_by('-count')
for item in category_counts:
    print(f'  {item["category__name"]}: {item["count"]} 个商品')

print('\n' + '=' * 60)
print('验证完成！')
