from app.secondhand_app.models import Product

# 导出所有商品数据到CSV文件
with open('all_products.csv', 'w', encoding='utf-8') as f:
    # 写入表头
    f.write('id,title,description,current_category\n')
    
    # 写入所有商品数据
    all_products = Product.objects.all()
    for p in all_products:
        # 清理数据，避免CSV格式问题
        title = p.title.replace(',', '，')
        description = p.description.replace(',', '，').replace('\n', ' ')
        current_category = p.category.name
        f.write(f'{p.id},{title},{description},{current_category}\n')

print(f'已导出 {all_products.count()} 个产品到 all_products.csv')
