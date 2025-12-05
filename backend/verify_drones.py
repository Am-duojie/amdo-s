from app.secondhand_app.models import Product

# 验证无人机产品分类
print('验证无人机产品分类：')
drone_products = Product.objects.filter(title__icontains='无人机')[:5]
for p in drone_products:
    print(f'Product {p.id}:')
    print(f'  Title: {p.title[:50]}...')
    print(f'  Category: {p.category.name}')
    print()

# 验证特定的错误分类产品
print('验证特定产品分类：')
specific_products = Product.objects.filter(id__in=[1594, 1592])
for p in specific_products:
    print(f'Product {p.id}:')
    print(f'  Title: {p.title[:50]}...')
    print(f'  Category: {p.category.name}')
    print()
