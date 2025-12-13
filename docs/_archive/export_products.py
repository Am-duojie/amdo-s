from app.secondhand_app.models import Product

# 导出前10个商品的详细信息到文件
with open('product_samples.txt', 'w', encoding='utf-8') as f:
    products = Product.objects.all()[:10]
    for p in products:
        f.write(f'Product {p.id}:\n')
        f.write(f'  Title: {p.title}\n')
        f.write(f'  Description: {p.description}\n')
        f.write(f'  Current Category: {p.category.name}\n')
        f.write('\n')

print('已导出10个商品样本到 product_samples.txt')
