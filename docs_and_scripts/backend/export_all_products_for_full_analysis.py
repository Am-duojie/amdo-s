from app.secondhand_app.models import Product

# 导出所有商品数据到一个详细的文本文件
with open('all_products_full_analysis.txt', 'w', encoding='utf-8') as f:
    all_products = Product.objects.all()
    f.write(f'总共有 {all_products.count()} 个商品\n')
    f.write('=' * 100 + '\n\n')
    
    # 按分类分组导出
    f.write('商品分类分布：\n')
    from django.db.models import Count
    category_counts = Product.objects.values('category__name').annotate(count=Count('category__name')).order_by('-count')
    for item in category_counts:
        f.write(f'  {item["category__name"]}: {item["count"]} 个商品\n')
    
    f.write('\n' + '=' * 100 + '\n')
    f.write('所有商品详细信息：\n')
    f.write('=' * 100 + '\n\n')
    
    # 导出所有商品的详细信息
    for i, p in enumerate(all_products, 1):
        f.write(f'商品 {i}/{all_products.count()}:\n')
        f.write(f'ID: {p.id}\n')
        f.write(f'标题: {p.title}\n')
        f.write(f'分类: {p.category.name}\n')
        f.write(f'描述: {p.description[:200]}...\n')
        f.write('-' * 80 + '\n')
    
    f.write('\n' + '=' * 100 + '\n')
    f.write('导出完成，共导出所有458个商品的详细信息\n')

print('已导出所有商品数据到 all_products_full_analysis.txt')
