from app.secondhand_app.models import Product

# 验证无人机产品的分类
print('验证无人机产品分类：')
drone_products = Product.objects.filter(title__icontains='无人机')[:5]
for p in drone_products:
    print(f'Product {p.id}: {p.title[:50]}... -> {p.category.name}')

print('\n验证显示屏产品分类：')
display_products = Product.objects.filter(title__icontains='显示屏')[:5]
for p in display_products:
    print(f'Product {p.id}: {p.title[:50]}... -> {p.category.name}')

print('\n验证前10个产品分类：')
all_products = Product.objects.all()[:10]
for p in all_products:
    print(f'Product {p.id}: {p.title[:50]}... -> {p.category.name}')
