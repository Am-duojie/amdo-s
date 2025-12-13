from app.secondhand_app.models import Product, Category

# 先获取所有分类
categories = {
    '手机': Category.objects.get(name='手机'),
    '平板': Category.objects.get(name='平板'),
    '笔记本电脑': Category.objects.get(name='笔记本电脑'),
    '台式电脑': Category.objects.get(name='台式电脑'),
    '摄影摄像': Category.objects.get(name='摄影摄像'),
    '智能手表': Category.objects.get(name='智能手表'),
    '耳机音响': Category.objects.get(name='耳机音响'),
    '游戏设备': Category.objects.get(name='游戏设备'),
    '数码配件': Category.objects.get(name='数码配件'),
    '其他数码': Category.objects.get(name='其他数码')
}

# 定义精确的分类匹配规则，基于实际商品分析
category_rules = {
    '手机': ['小米', '华为', 'mate', 'iPhone', '苹果手机', '智能手机', '手机', '安卓'],
    '平板': ['iPad', '平板', '平板电脑', 'iPad Pro'],
    '笔记本电脑': ['MacBook', 'macbook', '笔记本', '笔记本电脑', '游戏本', '轻薄本', 'ThinkPad', '拯救者'],
    '台式电脑': ['台式', '主机', '台式机', '组装机', 'DIY电脑'],
    '摄影摄像': ['尼康', '索尼', '相机', '微单', '单反', '镜头', '摄影', '摄像', '佳能', '富士', '无人机', '航拍', '大疆', 'DJI'],
    '智能手表': ['手表', 'Watch', '智能手表', '手环', 'Apple Watch', '华为手表'],
    '耳机音响': ['耳机', '音响', 'AirPods', '音箱', '蓝牙耳机', '降噪耳机', '头戴式耳机'],
    '游戏设备': ['游戏', '手柄', 'Switch', 'PS5', 'Xbox', '游戏机', '电竞', '显示屏', '显示器'],
    '数码配件': ['配件', '电池', '充电器', '数据线', '保护膜', '保护壳', '内存卡', 'U盘', '移动硬盘'],
    '其他数码': ['数码']
}

# 获取所有产品（包括已分类的，重新匹配）
all_products = Product.objects.all()
print(f'找到 {all_products.count()} 个产品，开始重新分配分类')

# 为所有产品重新分配分类
assigned_count = 0
for product in all_products:
    title = product.title
    description = product.description
    assigned = False
    
    # 合并标题和描述，同时检查
    content = f'{title} {description}'
    
    # 按优先级匹配分类（手机优先，然后平板，以此类推）
    for category_name, keywords in category_rules.items():
        for keyword in keywords:
            if keyword in content:
                product.category = categories[category_name]
                product.save()
                assigned_count += 1
                assigned = True
                break
        if assigned:
            break
    
    # 如果没有匹配到，分配到其他数码
    if not assigned:
        product.category = categories['其他数码']
        product.save()
        assigned_count += 1

print(f'已重新分配 {assigned_count} 个产品的分类')

# 统计各分类产品数量
print('\n各分类产品数量：')
for category_name, category in categories.items():
    count = Product.objects.filter(category=category).count()
    print(f'{category_name}: {count} 个产品')
