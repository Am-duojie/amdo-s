# 手动配置API端点指南

## 为什么需要手动配置？

大多数回收平台的API端点：
1. **需要认证**：需要API密钥或Token
2. **动态生成**：URL可能包含动态参数
3. **加密保护**：可能使用加密签名
4. **反爬虫**：检测自动化请求

因此，**最佳方案是联系平台获取官方API**。

## 如何找到API端点（手动分析）

### 步骤1：打开浏览器开发者工具

1. 访问目标网站（如：https://www.aihuishou.com）
2. 按 `F12` 打开开发者工具
3. 切换到 **Network（网络）** 标签页
4. 勾选 **Preserve log（保留日志）**

### 步骤2：执行搜索操作

1. 在网站上搜索一个商品（如：iPhone 15 Pro Max）
2. 观察Network标签页中的请求

### 步骤3：查找API请求

查找以下类型的请求：
- **XHR** 或 **Fetch** 请求（通常是API调用）
- 请求URL包含：`api`, `search`, `price`, `estimate`
- 响应类型是 `application/json`

### 步骤4：分析请求详情

点击请求，查看：
- **Request URL**：完整的API地址
- **Request Method**：GET 或 POST
- **Request Headers**：需要的请求头
- **Request Payload**：POST请求的参数
- **Response**：返回的数据格式

### 步骤5：复制API信息

记录以下信息：
```json
{
  "url": "https://www.aihuishou.com/api/v1/search",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer xxx"
  },
  "params": {
    "brand": "苹果",
    "model": "iPhone 15 Pro Max",
    "storage": "256GB"
  },
  "response_format": {
    "price": 7200.0
  }
}
```

## 配置到系统中

### 方法1：在settings.py中配置

```python
# settings.py

# 爬取服务API配置
SCRAPER_API_URL = 'https://www.aihuishou.com/api/v1/search'  # 您找到的API地址
SCRAPER_API_METHOD = 'POST'  # GET 或 POST

# 如果需要认证
SCRAPER_API_KEY = 'your_api_key'
SCRAPER_API_SECRET = 'your_api_secret'
```

### 方法2：更新scraper_service.py

找到 `_call_configured_api` 方法，根据实际API格式调整：

```python
def _call_configured_api(self, api_url, ...):
    # 根据实际API调整请求格式
    params = {
        'brand': brand,
        'model': model,
        # ... 根据实际API文档调整
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',  # 如果需要认证
        # ... 其他必要的请求头
    }
    
    response = requests.post(api_url, json=params, headers=headers)
    # ... 解析响应
```

## 实际示例

### 示例1：爱回收API（假设）

如果找到的API是这样的：

**请求：**
```http
POST https://www.aihuishou.com/api/v1/estimate
Content-Type: application/json
Authorization: Bearer your_token

{
  "brand": "苹果",
  "model": "iPhone 15 Pro Max",
  "storage": "256GB",
  "condition": "good"
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "estimated_price": 7200.0,
    "currency": "CNY"
  }
}
```

**配置代码：**
```python
# settings.py
SCRAPER_API_URL = 'https://www.aihuishou.com/api/v1/estimate'
SCRAPER_API_METHOD = 'POST'
SCRAPER_API_KEY = 'your_token'

# scraper_service.py 中调整解析逻辑
def _extract_price_from_json(self, data):
    if data.get('code') == 200:
        return data.get('data', {}).get('estimated_price')
    return None
```

### 示例2：需要签名的API

如果API需要签名：

```python
import hmac
import hashlib
import time

def generate_signature(params, secret):
    # 根据API文档生成签名
    sorted_params = sorted(params.items())
    sign_string = '&'.join([f'{k}={v}' for k, v in sorted_params])
    sign_string += f'&key={secret}'
    signature = hashlib.md5(sign_string.encode()).hexdigest().upper()
    return signature

# 在请求中使用
params = {
    'brand': brand,
    'model': model,
    'timestamp': int(time.time()),
}
params['sign'] = generate_signature(params, api_secret)
```

## 常见问题

### Q1: API返回403 Forbidden？
A: 可能需要：
- 添加正确的User-Agent
- 添加Referer头
- 使用Cookie/Session
- 添加API认证信息

### Q2: API返回的数据格式不同？
A: 调整 `_extract_price_from_json` 方法中的字段名

### Q3: 需要登录才能访问？
A: 使用Session保持登录状态：
```python
session = requests.Session()
# 先登录
session.post('https://example.com/login', data={'username': '...', 'password': '...'})
# 然后使用session访问API
response = session.get('https://example.com/api/...')
```

### Q4: API有频率限制？
A: 添加请求延迟和缓存：
```python
import time
time.sleep(2)  # 延迟2秒
```

## 测试配置

创建测试脚本：

```python
# test_api.py
import requests

api_url = 'https://your-api-endpoint.com/api/v1/estimate'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your_token'
}
params = {
    'brand': '苹果',
    'model': 'iPhone 15 Pro Max',
    'storage': '256GB'
}

response = requests.post(api_url, json=params, headers=headers)
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
```

## 重要提醒

1. **优先使用官方API**：联系平台获取官方API文档
2. **遵守服务条款**：不要违反网站的使用条款
3. **设置合理频率**：避免对服务器造成负担
4. **做好错误处理**：API可能随时变化
5. **保护API密钥**：不要将密钥提交到代码仓库

## 总结

手动配置API的步骤：
1. ✅ 使用浏览器开发者工具找到API端点
2. ✅ 分析请求格式和响应格式
3. ✅ 在settings.py中配置API地址
4. ✅ 调整解析逻辑匹配实际响应格式
5. ✅ 测试API调用是否正常

如果找不到公开的API端点，**强烈建议联系平台获取官方API**。

