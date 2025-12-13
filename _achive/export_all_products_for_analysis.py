from app.secondhand_app.models import Product

# 导出所有商品数据到一个易于分析的文本文件
with open('all_products_detailed.txt', 'w', encoding='utf-8') as f:
    all_products = Product.objects.all()
    f.write(f'总共有 {all_products.count()} 个商品\n')
    f.write('=' * 100 + '\n\n')
    
    # 导出前20个商品作为样本
    for i, p in enumerate(all_products[:20], 1):
        f.write(f'商品 {i}/{all_products.count()}:\n')
        f.write(f'ID: {p.id}\n')
        f.write(f'标题: {p.title}\n')
        f.write(f'当前分类: {p.category.name}\n')
        f.write(f'描述: {p.description[:150]}...\n')
        f.write('-' * 80 + '\n')
    
    f.write('\n' + '=' * 100 + '\n')
    f.write('导出完成，共导出20个商品样本\n')

print('已导出20个商品样本到 all_products_detailed.txt')
