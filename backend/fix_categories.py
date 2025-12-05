from app.secondhand_app.models import Product, Category

# 获取所有分类对象
categories = {
    '摄影摄像': Category.objects.get(name='摄影摄像'),
    '数码配件': Category.objects.get(name='数码配件'),
    '游戏设备': Category.objects.get(name='游戏设备')
}

print('开始修复分类错误...')

# 1. 修复无人机分类错误
print('\n1. 修复无人机分类...')
# 查找所有无人机相关商品
for keyword in ['无人机', '航拍', '大疆', 'DJI']:
    products = Product.objects.filter(title__icontains=keyword)
    if products.exists():
        count = products.update(category=categories['摄影摄像'])
        print(f'  修复了 {count} 个包含"{keyword}"的商品分类为摄影摄像')

# 2. 修复键盘分类错误
print('\n2. 修复键盘分类...')
# 查找所有键盘相关商品
for keyword in ['键盘', '机械键盘', '蓝牙键盘']:
    products = Product.objects.filter(title__icontains=keyword)
    if products.exists():
        count = products.update(category=categories['数码配件'])
        print(f'  修复了 {count} 个包含"{keyword}"的商品分类为数码配件')

# 3. 修复显示器分类（已经大部分正确，确认一下）
print('\n3. 确认显示器分类...')
products = Product.objects.filter(title__icontains='显示器') | Product.objects.filter(title__icontains='显示屏')
if products.exists():
    count = products.update(category=categories['游戏设备'])
    print(f'  确认了 {count} 个显示器/显示屏商品分类为游戏设备')

# 4. 修复其他明显错误
print('\n4. 修复其他明显错误...')

# 修复ID为1594的大疆无人机（之前是台式电脑）
try:
    product = Product.objects.get(id=1594)
    if product.category.name != '摄影摄像':
        product.category = categories['摄影摄像']
        product.save()
        print('  修复了商品1594：大疆精灵W321无人机 - 从台式电脑改为摄影摄像')
except Product.DoesNotExist:
    pass

# 修复ID为1592的GX无人机（之前是手机）
try:
    product = Product.objects.get(id=1592)
    if product.category.name != '摄影摄像':
        product.category = categories['摄影摄像']
        product.save()
        print('  修复了商品1592：GX超清双摄无人机 - 从手机改为摄影摄像')
except Product.DoesNotExist:
    pass

# 修复ID为1567的蓝牙键盘（之前是其他数码）
try:
    product = Product.objects.get(id=1567)
    if product.category.name != '数码配件':
        product.category = categories['数码配件']
        product.save()
        print('  修复了商品1567：航世蓝牙键盘 - 从其他数码改为数码配件')
except Product.DoesNotExist:
    pass

# 修复ID为1566的机械键盘（之前是其他数码）
try:
    product = Product.objects.get(id=1566)
    if product.category.name != '数码配件':
        product.category = categories['数码配件']
        product.save()
        print('  修复了商品1566：机械键盘 - 从其他数码改为数码配件')
except Product.DoesNotExist:
    pass

print('\n分类修复完成！')

# 验证修复结果
print('\n验证修复结果：')
# 验证无人机分类
print('\n无人机分类验证：')
drone_products = Product.objects.filter(title__icontains='无人机')[:3]
for p in drone_products:
    print(f'  {p.title[:30]}... -> {p.category.name}')

# 验证键盘分类
print('\n键盘分类验证：')
keyboard_products = Product.objects.filter(title__icontains='键盘')[:3]
for p in keyboard_products:
    print(f'  {p.title[:30]}... -> {p.category.name}')
