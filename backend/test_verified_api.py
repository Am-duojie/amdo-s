"""测试官方验商品API"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
import json

client = Client()
response = client.get('/api/verified-products/', {
    'status': 'active',
    'page_size': 10
})

print(f"状态码: {response.status_code}")
data = json.loads(response.content)
print(f"数据格式: {type(data)}")

if isinstance(data, dict):
    print(f"总数: {data.get('count', 0)}")
    results = data.get('results', [])
    print(f"返回商品数: {len(results)}")
    for item in results[:3]:
        print(f"  - {item.get('title', 'N/A')} (ID: {item.get('id')})")
elif isinstance(data, list):
    print(f"返回商品数: {len(data)}")
    for item in data[:3]:
        print(f"  - {item.get('title', 'N/A')} (ID: {item.get('id')})")
else:
    print(f"数据: {data}")

