"""
测试公开API服务
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.secondhand_app.public_api_service import public_api_service

def test_public_api():
    """测试公开API服务"""
    print("=" * 60)
    print("公开API服务测试")
    print("=" * 60)
    
    test_cases = [
        {
            'device_type': '手机',
            'brand': '苹果',
            'model': 'iPhone 15 Pro Max',
            'storage': '256GB',
            'condition': 'good'
        },
        {
            'device_type': '手机',
            'brand': '华为',
            'model': 'Mate 60 Pro',
            'storage': '512GB',
            'condition': 'good'
        }
    ]
    
    for case in test_cases:
        print(f"\n测试: {case['brand']} {case['model']} {case['storage']}")
        try:
            price = public_api_service.estimate(
                case['device_type'],
                case['brand'],
                case['model'],
                case['storage'],
                case['condition']
            )
            if price:
                print(f"✓ 获取到价格: ¥{price}")
            else:
                print("✗ 未获取到价格（可能需要配置API密钥）")
        except Exception as e:
            print(f"✗ 错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n提示：")
    print("1. 如果未获取到价格，需要在settings.py中配置API密钥")
    print("2. 推荐使用聚合数据（Juhe.cn）或RapidAPI")
    print("3. 查看 公开API接入指南.md 了解详细配置方法")

if __name__ == '__main__':
    test_public_api()

