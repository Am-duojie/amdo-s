"""
测试脚本：尝试获取爱回收移动端页面的估价
URL: https://m.aihuishou.com/n/#/inquiry?productId=225361
"""
import requests
import json
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def test_aihuishou_mobile_api():
    """尝试通过API获取爱回收价格"""
    
    # 从URL中提取productId
    url = "https://m.aihuishou.com/n/#/inquiry?productId=225361"
    product_id = "225361"
    
    print(f"正在尝试获取产品ID: {product_id} 的估价...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://m.aihuishou.com/',
        'Origin': 'https://m.aihuishou.com',
    }
    
    # 尝试可能的API端点
    api_endpoints = [
        # 方式1: 直接查询产品信息
        f"https://m.aihuishou.com/api/product/{product_id}",
        f"https://m.aihuishou.com/api/v1/product/{product_id}",
        f"https://api.aihuishou.com/product/{product_id}",
        f"https://api.aihuishou.com/v1/product/{product_id}",
        
        # 方式2: 查询接口
        f"https://m.aihuishou.com/api/inquiry/{product_id}",
        f"https://m.aihuishou.com/api/v1/inquiry/{product_id}",
        f"https://api.aihuishou.com/inquiry/{product_id}",
        
        # 方式3: 价格查询
        f"https://m.aihuishou.com/api/price/{product_id}",
        f"https://m.aihuishou.com/api/v1/price/{product_id}",
    ]
    
    for endpoint in api_endpoints:
        try:
            print(f"\n尝试端点: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"成功获取JSON数据:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # 尝试提取价格
                    price = extract_price_from_data(data)
                    if price:
                        print(f"\n✅ 找到价格: {price} 元")
                        return price
                except:
                    print(f"响应不是JSON格式，内容预览: {response.text[:200]}")
            else:
                print(f"请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"请求异常: {e}")
    
    return None


def test_aihuishou_mobile_html():
    """尝试通过HTML解析获取价格"""
    
    url = "https://m.aihuishou.com/n/#/inquiry?productId=225361"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        print(f"\n尝试访问HTML页面: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找script标签中的JSON数据
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # 查找包含price或价格的数据
                    if 'price' in script.string.lower() or '价格' in script.string:
                        print(f"\n找到可能包含价格的script标签:")
                        print(script.string[:500])
                        
                        # 尝试提取JSON
                        json_matches = re.findall(r'\{[^{}]*"price"[^{}]*\}', script.string)
                        for match in json_matches:
                            try:
                                data = json.loads(match)
                                print(f"提取的JSON: {data}")
                                price = extract_price_from_data(data)
                                if price:
                                    return price
                            except:
                                pass
            
            # 查找价格相关的HTML元素
            price_elements = soup.select('[class*="price"], [class*="Price"], [id*="price"], [id*="Price"]')
            for elem in price_elements:
                text = elem.get_text(strip=True)
                price_match = re.search(r'[\d,]+', text.replace(',', ''))
                if price_match:
                    price = float(price_match.group().replace(',', ''))
                    if 100 <= price <= 50000:
                        print(f"\n✅ 从HTML找到价格: {price} 元")
                        return price
        
    except Exception as e:
        print(f"HTML解析异常: {e}")
    
    return None


def extract_price_from_data(data):
    """从数据中提取价格"""
    if isinstance(data, dict):
        # 尝试多个可能的字段名
        price_fields = ['price', 'Price', 'amount', 'Amount', 'estimated_price', 
                        'estimatedPrice', 'totalPrice', 'total_price', 'value', 'Value']
        
        for field in price_fields:
            if field in data:
                price = data[field]
                if isinstance(price, (int, float)):
                    return float(price)
                elif isinstance(price, str):
                    price_match = re.search(r'[\d.]+', price.replace(',', ''))
                    if price_match:
                        return float(price_match.group())
        
        # 递归查找嵌套字典
        for value in data.values():
            if isinstance(value, dict):
                result = extract_price_from_data(value)
                if result:
                    return result
    
    elif isinstance(data, list):
        for item in data:
            result = extract_price_from_data(item)
            if result:
                return result
    
    return None


def test_aihuishou_network_analysis():
    """分析网络请求，尝试找到API端点"""
    
    print("\n" + "="*60)
    print("网络请求分析建议:")
    print("="*60)
    print("""
要找到爱回收的实际API端点，建议：
1. 使用浏览器开发者工具（F12）
2. 打开 Network（网络）标签
3. 访问 https://m.aihuishou.com/n/#/inquiry?productId=225361
4. 查看XHR/Fetch请求，找到返回价格数据的API
5. 常见的API端点可能是：
   - /api/product/inquiry
   - /api/v1/product/price
   - /api/inquiry/estimate
   - /api/product/{productId}/price
   
6. 查看请求头，可能需要：
   - Authorization token
   - 特定的User-Agent
   - Referer头
   - Cookie
    """)


def main():
    print("="*60)
    print("爱回收移动端价格获取测试")
    print("="*60)
    
    # 方法1: 尝试API端点
    print("\n【方法1】尝试直接访问API端点")
    price = test_aihuishou_mobile_api()
    
    if not price:
        # 方法2: 尝试HTML解析
        print("\n【方法2】尝试HTML解析")
        price = test_aihuishou_mobile_html()
    
    if price:
        print(f"\n[成功] 成功获取价格: {price} 元")
    else:
        print("\n[失败] 未能获取价格")
        test_aihuishou_network_analysis()
        
        print("\n" + "="*60)
        print("建议使用Selenium或Playwright进行浏览器自动化:")
        print("="*60)
        print("""
# 安装依赖
pip install selenium playwright

# 使用Selenium示例
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://m.aihuishou.com/n/#/inquiry?productId=225361")
# 等待页面加载
time.sleep(5)
# 查找价格元素
price_element = driver.find_element(By.CSS_SELECTOR, "[class*='price']")
print(price_element.text)
driver.quit()
        """)


if __name__ == "__main__":
    main()

