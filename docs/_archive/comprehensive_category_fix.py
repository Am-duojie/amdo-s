from app.secondhand_app.models import Product, Category

# 获取所有分类对象
all_categories = {cat.name: cat for cat in Category.objects.all()}

print('开始全面分析和修复商品分类...')

# 1. 导出所有商品数据
print('\n1. 导出所有商品数据到分析文件...')
with open('category_analysis.csv', 'w', encoding='utf-8') as f:
    f.write('id,title,current_category,correct_category\n')
    
    # 处理所有商品
    all_products = Product.objects.all()
    
    for i, p in enumerate(all_products, 1):
        title = p.title
        current_category = p.category.name
        correct_category = current_category  # 默认为当前分类，后续修改
        
        # 根据标题和描述判断正确分类
        content = f'{title} {p.description}'
        
        # 确定正确分类
        if any(keyword in content for keyword in ['手机', '小米', '华为', 'mate', 'iPhone', '苹果手机', '智能手机']):
            correct_category = '手机'
        elif any(keyword in content for keyword in ['平板', 'iPad', '平板电脑']):
            correct_category = '平板'
        elif any(keyword in content for keyword in ['笔记本', 'MacBook', 'macbook', '笔记本电脑', '游戏本', '轻薄本']):
            correct_category = '笔记本电脑'
        elif any(keyword in content for keyword in ['台式', '主机', '台式机', '组装机']):
            correct_category = '台式电脑'
        elif any(keyword in content for keyword in ['相机', '微单', '单反', '镜头', '尼康', '索尼', '佳能', '富士', '无人机', '航拍', '大疆', 'DJI']):
            correct_category = '摄影摄像'
        elif any(keyword in content for keyword in ['手表', '智能手表', '手环', 'Apple Watch']):
            correct_category = '智能手表'
        elif any(keyword in content for keyword in ['耳机', '音响', 'AirPods', '音箱', '蓝牙耳机']):
            correct_category = '耳机音响'
        elif any(keyword in content for keyword in ['游戏', '手柄', 'Switch', 'PS5', 'Xbox', '游戏机', '电竞', '显示器', '显示屏']):
            correct_category = '游戏设备'
        elif any(keyword in content for keyword in ['配件', '电池', '充电器', '数据线', '保护膜', '保护壳', '键盘', '鼠标', '内存卡', 'U盘', '移动硬盘']):
            correct_category = '数码配件'
        else:
            correct_category = '其他数码'
        
        # 写入分析结果
        title_clean = title.replace(',', '，')
        f.write(f'{p.id},{title_clean},{current_category},{correct_category}\n')
        
        # 进度显示
        if i % 50 == 0:
            print(f'  已分析 {i}/{all_products.count()} 个商品')

print(f'\n已导出 {all_products.count()} 个商品的分类分析结果到 category_analysis.csv')

# 2. 根据分析结果修复分类
print('\n2. 根据分析结果修复商品分类...')

# 读取分析文件并修复分类
with open('category_analysis.csv', 'r', encoding='utf-8') as f:
    next(f)  # 跳过表头
    
    for line in f:
        parts = line.strip().split(',')
        if len(parts) >= 4:
            product_id = int(parts[0])
            current_category = parts[2]
            correct_category = parts[3]
            
            # 如果分类不正确，进行修复
            if current_category != correct_category:
                try:
                    product = Product.objects.get(id=product_id)
                    product.category = all_categories[correct_category]
                    product.save()
                    print(f'  修复商品 {product_id}: {current_category} -> {correct_category}')
                except Product.DoesNotExist:
                    print(f'  商品 {product_id} 不存在')

print('\n3. 验证修复结果...')

# 统计各分类商品数量
from django.db.models import Count
category_counts = Product.objects.values('category__name').annotate(count=Count('category__name')).order_by('-count')
for item in category_counts:
    print(f'  {item["category__name"]}: {item["count"]} 个商品')

print('\n\n全面分类修复完成！')
