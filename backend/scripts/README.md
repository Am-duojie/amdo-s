# 测试数据脚本使用说明

## 添加官方验商品测试数据

### 方法一：使用 Django 管理命令（推荐）

```bash
cd backend
python manage.py add_verified_products
```

### 方法二：直接运行 Python 脚本

```bash
cd backend
python scripts/add_verified_test_data.py
```

## 测试数据说明

脚本会创建以下 6 个官方验商品：

1. **Apple iPhone 14 Pro Max 256GB 深空黑**
   - 价格：¥6,899
   - 成色：99新
   - 电池健康：98%
   - 库存：3

2. **Apple iPhone 13 128GB 粉色**
   - 价格：¥3,899
   - 成色：95新
   - 电池健康：92%
   - 库存：5

3. **Apple iPhone 12 Pro 256GB 海蓝色**
   - 价格：¥3,599
   - 成色：95新
   - 电池健康：89%
   - 库存：2

4. **Apple iPad Air 5 256GB WiFi版 星光色**
   - 价格：¥4,299
   - 成色：99新
   - 电池健康：96%
   - 库存：4

5. **Apple iPhone 15 Pro 256GB 原色钛金属**
   - 价格：¥7,899
   - 成色：全新
   - 电池健康：100%
   - 库存：1

6. **Apple MacBook Air M2 256GB 午夜色**
   - 价格：¥7,299
   - 成色：99新
   - 电池健康：95%
   - 库存：2

## 数据特点

- ✅ 所有商品状态为"在售"（active）
- ✅ 包含完整的商品信息（品牌、型号、存储、颜色等）
- ✅ 包含质检报告和验货信息
- ✅ 使用占位图作为商品图片
- ✅ 随机生成浏览量和销量
- ✅ 包含详细的商品描述

## 查看效果

运行脚本后，访问以下页面查看：

- 官方验商品列表：http://localhost:5173/verified-products
- 商品详情页：点击任意商品查看

## 注意事项

1. 脚本会自动创建测试卖家账号：
   - 用户名：`verified_seller`
   - 密码：`password123`

2. 如果商品已存在，脚本会跳过创建

3. 图片使用占位图服务，实际使用时需要替换为真实图片

## 清理测试数据

如需清理测试数据，可以在 Django Admin 中删除，或使用以下命令：

```python
# 进入 Django shell
python manage.py shell

# 删除测试商品
from app.secondhand_app.models import VerifiedProduct
VerifiedProduct.objects.filter(seller__username='verified_seller').delete()

# 删除测试用户
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='verified_seller').delete()
```

## 扩展

如需添加更多测试数据，可以编辑脚本中的 `products_data` 列表，添加新的商品数据。

每个商品数据包含以下字段：

```python
{
    'title': '商品标题',
    'brand': '品牌',
    'model': '型号',
    'storage': '存储容量',
    'color': '颜色',
    'screen_size': '屏幕尺寸',
    'battery_health': '电池健康度',
    'price': 价格,
    'original_price': 原价,
    'condition': '成色',  # new, like_new, good, fair, poor
    'description': '商品描述',
    'location': '所在地',
    'tags': ['标签1', '标签2'],
    'inspection_result': 'pass',  # pass, warn, fail
    'inspection_note': '质检说明',
    'stock': 库存数量
}
```
