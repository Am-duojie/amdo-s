"""
测试爬取服务
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.secondhand_app.scraper_service import scraper_service
import requests
from bs4 import BeautifulSoup

def test_aihuishou():
    """测试爱回收网站"""
    print("\n=== 测试爱回收 ===")
    try:
        url = "https://www.aihuishou.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)} 字符")
        
        # 查找可能的API端点
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        print(f"找到 {len(scripts)} 个script标签")
        
        # 查找包含api或price的script
        for script in scripts[:5]:
            if script.string and ('api' in script.string.lower() or 'price' in script.string.lower()):
                print(f"发现相关script: {script.string[:200]}...")
        
    except Exception as e:
        print(f"错误: {e}")

def test_huishoubao():
    """测试回收宝网站"""
    print("\n=== 测试回收宝 ===")
    try:
        url = "https://www.huishoubao.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)} 字符")
        
    except Exception as e:
        print(f"错误: {e}")

def test_search_api():
    """测试搜索API端点"""
    print("\n=== 测试搜索功能 ===")
    
    # 测试iPhone 15 Pro Max搜索
    test_cases = [
        {
            'device_type': '手机',
            'brand': '苹果',
            'model': 'iPhone 15 Pro Max',
            'storage': '256GB',
            'condition': 'good'
        }
    ]
    
    for case in test_cases:
        print(f"\n测试: {case['brand']} {case['model']} {case['storage']}")
        try:
            price = scraper_service.estimate(
                case['device_type'],
                case['brand'],
                case['model'],
                case['storage'],
                case['condition']
            )
            if price:
                print(f"✓ 获取到价格: ¥{price}")
            else:
                print("✗ 未获取到价格")
        except Exception as e:
            print(f"✗ 错误: {e}")

def analyze_network_requests():
    """分析网络请求（需要手动在浏览器中查看）"""
    print("\n=== 网络请求分析指南 ===")
    print("""
    要找到实际的API端点，请按以下步骤操作：
    
    1. 打开浏览器，访问 https://www.aihuishou.com
    2. 按F12打开开发者工具
    3. 切换到 Network（网络）标签页
    4. 在网站上搜索一个商品（如：iPhone 15 Pro Max）
    5. 在Network标签页中查找：
       - XHR/Fetch 请求（通常是API调用）
       - 查找包含 'price', 'estimate', 'search' 的请求
       - 查看请求URL和响应数据
    
    示例API端点可能是：
    - https://www.aihuishou.com/api/v1/search
    - https://www.aihuishou.com/api/v1/estimate
    - https://www.aihuishou.com/api/price/query
    
    找到后，可以在 scraper_service.py 中更新URL和解析逻辑。
    """)

if __name__ == '__main__':
    print("=" * 50)
    print("爬取服务测试")
    print("=" * 50)
    
    # 测试网站可访问性
    test_aihuishou()
    test_huishoubao()
    
    # 测试爬取服务
    test_search_api()
    
    # 提供分析指南
    analyze_network_requests()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
    print("\n提示：")
    print("1. 如果未获取到价格，需要分析网站的实际API端点")
    print("2. 使用浏览器开发者工具查找真实的API接口")
    print("3. 更新 scraper_service.py 中的URL和解析逻辑")

