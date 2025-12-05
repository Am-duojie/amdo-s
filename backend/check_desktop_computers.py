from app.secondhand_app.models import Product, Category

print('检查台式电脑分类下的商品...')

# 获取台式电脑分类
desktop_category = Category.objects.get(name='台式电脑')

# 获取所有台式电脑分类下的商品
desktop_products = Product.objects.filter(category=desktop_category)

print(f'\n台式电脑分类下共有 {desktop_products.count()} 个商品：')

# 显示每个商品的详细信息
for i, p in enumerate(desktop_products, 1):
    print(f'\n商品 {i}/{desktop_products.count()}:')
    print(f'ID: {p.id}')
    print(f'标题: {p.title}')
    print(f'描述: {p.description[:200]}...')
    print(f'当前分类: {p.category.name}')
    
    # 判断分类是否正确
    content = f'{p.title} {p.description}'
    if any(keyword in content for keyword in ['台式', '主机', '台式机', '组装机', 'DIY电脑']):
        print(f'分类判断: ✓ 正确')
    else:
        print(f'分类判断: ✗ 错误 - 建议分类: 其他数码')

print('\n\n检查完成！')
