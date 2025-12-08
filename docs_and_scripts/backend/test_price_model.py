"""
测试智能估价模型
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.secondhand_app.price_model import price_model

def test_price_model():
    """测试估价模型"""
    print("=" * 70)
    print("智能估价模型测试")
    print("=" * 70)
    
    test_cases = [
        # 苹果
        {'brand': '苹果', 'model': 'iPhone 15 Pro Max', 'storage': '256GB', 'condition': 'good'},
        {'brand': '苹果', 'model': 'iPhone 15 Pro', 'storage': '512GB', 'condition': 'like_new'},
        {'brand': '苹果', 'model': 'iPhone 14', 'storage': '128GB', 'condition': 'good'},
        {'brand': '苹果', 'model': 'iPhone 13', 'storage': '256GB', 'condition': 'fair'},
        
        # 华为
        {'brand': '华为', 'model': 'Mate 60 Pro', 'storage': '512GB', 'condition': 'good'},
        {'brand': '华为', 'model': 'P60 Pro', 'storage': '256GB', 'condition': 'like_new'},
        
        # 小米
        {'brand': '小米', 'model': '小米14 Pro', 'storage': '512GB', 'condition': 'good'},
        {'brand': '小米', 'model': '小米13 Ultra', 'storage': '256GB', 'condition': 'good'},
        
        # vivo
        {'brand': 'vivo', 'model': 'X100 Pro', 'storage': '512GB', 'condition': 'good'},
        
        # OPPO
        {'brand': 'OPPO', 'model': 'Find X6 Pro', 'storage': '256GB', 'condition': 'good'},
        
        # 荣耀
        {'brand': '荣耀', 'model': 'Magic6 Pro', 'storage': '512GB', 'condition': 'good'},
        
        # 三星
        {'brand': '三星', 'model': 'Galaxy S24 Ultra', 'storage': '512GB', 'condition': 'good'},
    ]
    
    print("\n【不同成色的价格对比】")
    print("-" * 70)
    print(f"{'品牌':<8} {'型号':<20} {'存储':<8} {'全新':<10} {'几乎全新':<10} {'良好':<10} {'一般':<10} {'较差':<10}")
    print("-" * 70)
    
    sample_cases = test_cases[:5]  # 显示前5个
    for case in sample_cases:
        brand = case['brand']
        model = case['model']
        storage = case['storage']
        
        prices = []
        for condition in ['new', 'like_new', 'good', 'fair', 'poor']:
            price = price_model.estimate(brand, model, storage, condition)
            prices.append(price)
        
        print(f"{brand:<8} {model:<20} {storage:<8} "
              f"¥{prices[0]:<9.0f} ¥{prices[1]:<9.0f} ¥{prices[2]:<9.0f} "
              f"¥{prices[3]:<9.0f} ¥{prices[4]:<9.0f}")
    
    print("\n【不同存储容量的价格对比】")
    print("-" * 70)
    print(f"{'品牌':<8} {'型号':<20} {'成色':<8} {'128GB':<10} {'256GB':<10} {'512GB':<10} {'1TB':<10}")
    print("-" * 70)
    
    sample_models = [
        {'brand': '苹果', 'model': 'iPhone 15 Pro Max'},
        {'brand': '华为', 'model': 'Mate 60 Pro'},
        {'brand': '小米', 'model': '小米14 Pro'},
    ]
    
    for case in sample_models:
        brand = case['brand']
        model = case['model']
        condition = 'good'
        
        prices = []
        for storage in ['128GB', '256GB', '512GB', '1TB']:
            price = price_model.estimate(brand, model, storage, condition)
            prices.append(price if price > 0 else 0)
        
        print(f"{brand:<8} {model:<20} {condition:<8} "
              f"¥{prices[0]:<9.0f} ¥{prices[1]:<9.0f} ¥{prices[2]:<9.0f} ¥{prices[3]:<9.0f}")
    
    print("\n【品牌保值率对比】")
    print("-" * 70)
    print(f"{'品牌':<10} {'保值率':<10} {'示例价格（256GB，良好）':<25}")
    print("-" * 70)
    
    brands = ['苹果', '华为', '小米', 'OPPO', 'vivo', '荣耀', '三星']
    for brand in brands:
        multiplier = price_model.brand_multipliers.get(brand, 0.75)
        # 使用iPhone 15 Pro Max作为基准
        base_price = price_model.price_database.get('苹果', {}).get('iPhone 15 Pro Max', {}).get('256GB', 7200)
        brand_price = base_price * multiplier
        
        print(f"{brand:<10} {multiplier*100:<9.1f}% ¥{brand_price:<24.0f}")
    
    print("\n【完整测试用例】")
    print("-" * 70)
    for i, case in enumerate(test_cases, 1):
        price = price_model.estimate(
            case['brand'],
            case['model'],
            case['storage'],
            case['condition']
        )
        print(f"{i:2d}. {case['brand']} {case['model']} {case['storage']} "
              f"({case['condition']}) → ¥{price:,.0f}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)
    print("\n估价模型特点：")
    print("1. ✓ 包含主流手机品牌和型号")
    print("2. ✓ 考虑品牌保值率")
    print("3. ✓ 考虑存储容量差异")
    print("4. ✓ 考虑成色影响")
    print("5. ✓ 支持时间衰减（如果提供发布年份）")

if __name__ == '__main__':
    test_price_model()

