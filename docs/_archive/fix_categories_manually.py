from app.secondhand_app.models import Product, Category

# 获取所有分类对象
categories = {
    '摄影摄像': Category.objects.get(name='摄影摄像'),
    '数码配件': Category.objects.get(name='数码配件'),
    '游戏设备': Category.objects.get(name='游戏设备')
}

print('开始手动修复分类错误...')

# 1. 修复Product 1596 - 四轴无人机
print('\n1. 修复Product 1596 - 四轴无人机')
product = Product.objects.get(id=1596)
print(f'  原分类: {product.category.name}')
product.category = categories['摄影摄像']
product.save()
print(f'  新分类: 摄影摄像')

# 2. 修复Product 1595 - 航拍无人机
print('\n2. 修复Product 1595 - 航拍无人机')
product = Product.objects.get(id=1595)
print(f'  原分类: {product.category.name}')
product.category = categories['摄影摄像']
product.save()
print(f'  新分类: 摄影摄像')

# 3. 修复Product 1594 - 大疆精灵无人机
print('\n3. 修复Product 1594 - 大疆精灵无人机')
product = Product.objects.get(id=1594)
print(f'  原分类: {product.category.name}')
product.category = categories['摄影摄像']
product.save()
print(f'  新分类: 摄影摄像')

# 4. 修复Product 1593 - 航拍无人机
print('\n4. 修复Product 1593 - 航拍无人机')
product = Product.objects.get(id=1593)
print(f'  原分类: {product.category.name}')
product.category = categories['摄影摄像']
product.save()
print(f'  新分类: 摄影摄像')

# 5. 修复Product 1592 - GX超清双摄无人机
print('\n5. 修复Product 1592 - GX超清双摄无人机')
product = Product.objects.get(id=1592)
print(f'  原分类: {product.category.name}')
product.category = categories['摄影摄像']
product.save()
print(f'  新分类: 摄影摄像')

# 6. 修复Product 1590 - 大疆航拍无人机
print('\n6. 修复Product 1590 - 大疆航拍无人机')
product = Product.objects.get(id=1590)
print(f'  原分类: {product.category.name}')
product.category = categories['摄影摄像']
product.save()
print(f'  新分类: 摄影摄像')

# 7. 修复Product 1589 - 儿童无人机
print('\n7. 修复Product 1589 - 儿童无人机')
product = Product.objects.get(id=1589)
print(f'  原分类: {product.category.name}')
product.category = categories['摄影摄像']
product.save()
print(f'  新分类: 摄影摄像')

# 8. 修复Product 1588 - 航拍无人机
print('\n8. 修复Product 1588 - 航拍无人机')
product = Product.objects.get(id=1588)
print(f'  原分类: {product.category.name}')
product.category = categories['摄影摄像']
product.save()
print(f'  新分类: 摄影摄像')

# 9. 修复Product 1575 - 电竞显示屏（已经正确，确认一下）
print('\n9. 确认Product 1575 - 电竞显示屏')
product = Product.objects.get(id=1575)
print(f'  当前分类: {product.category.name}')
print(f'  分类正确，无需修改')

# 修复其他可能的错误
print('\n10. 修复其他无人机相关商品')
# 查找所有包含"无人机"的商品
for keyword in ['无人机', '航拍', '大疆', 'DJI']:
    products = Product.objects.filter(title__icontains=keyword)
    if products.exists():
        for p in products:
            if p.category.name != '摄影摄像':
                print(f'  修复了商品ID {p.id} - 从{product.category.name}到摄影摄像')
                p.category = categories['摄影摄像']
                p.save()

print('\n\n所有分类修复完成！')

# 验证修复结果
print('\n验证修复结果：')
drone_products = Product.objects.filter(title__icontains='无人机')[:5]
for p in drone_products:
    print(f'商品ID {p.id}: {p.title[:30]}... -> {p.category.name}')
