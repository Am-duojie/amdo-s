# 国内回收估价网站爬取分析

> **注意**：爬取第三方网站可能违反服务条款，仅供学习研究使用。建议优先使用官方API接口。

## 一、主要回收平台（按爬取难度排序）

### ⭐⭐⭐ 简单（HTML静态页面，可直接爬取）

#### 1. **回收宝** (https://www.huishoubao.com)
- **难度**：⭐⭐（简单）
- **特点**：
  - 传统HTML页面，结构相对简单
  - 价格信息可能在HTML中直接可见
  - 需要模拟搜索或选择机型
- **爬取方式**：
  - 直接HTTP请求 + BeautifulSoup解析
  - 可能需要处理搜索表单
- **注意事项**：
  - 可能有简单的反爬机制
  - 需要正确的User-Agent和Referer

#### 2. **京回收** (https://shouji.jhuishou.com)
- **难度**：⭐⭐（简单）
- **特点**：
  - 相对简单的页面结构
  - 价格信息可能直接显示
- **爬取方式**：
  - HTTP请求 + HTML解析
- **注意事项**：
  - 可能需要选择城市等参数

#### 3. **苏宁回收** (https://hx.suning.com)
- **难度**：⭐⭐⭐（中等）
- **特点**：
  - 苏宁易购的回收频道
  - 可能需要登录或Cookie
- **爬取方式**：
  - HTTP请求 + HTML解析
  - 可能需要处理登录状态
- **注意事项**：
  - 可能有反爬机制
  - 价格可能需要填写问卷后显示

### ⭐⭐⭐⭐ 中等（SPA应用，需要浏览器自动化）

#### 4. **爱回收** (https://www.aihuishou.com / https://m.aihuishou.com)
- **难度**：⭐⭐⭐⭐（中等偏难）
- **特点**：
  - 移动端是SPA应用（Vue.js）
  - 价格通过JavaScript动态加载
  - 需要填写问卷才能获取价格
- **爬取方式**：
  - ✅ **推荐**：Playwright/Selenium浏览器自动化
  - 已实现：`backend/app/secondhand_app/aihuishou_scraper.py`
  - 自动填写问卷选择最佳值
- **API端点**（已发现）：
  - `https://dubai.aihuishou.com/dubai-gateway/recycle-products/inquiry/{productId}`
- **注意事项**：
  - 需要等待JavaScript执行
  - 需要自动填写问卷
  - 价格在页面文本中或API响应中

#### 5. **京东回收** (https://huishou.m.jd.com)
- **难度**：⭐⭐⭐⭐（中等偏难）
- **特点**：
  - 京东的回收频道
  - 可能是SPA应用
  - 需要选择机型和填写问卷
- **爬取方式**：
  - Playwright/Selenium浏览器自动化
  - 可能需要处理登录（京东账号）
- **注意事项**：
  - 可能需要登录
  - 反爬机制较强
  - 价格可能需要填写完整问卷

### ⭐⭐⭐⭐⭐ 困难（需要登录/复杂反爬）

#### 6. **转转回收** (https://www.zhuanzhuan.com)
- **难度**：⭐⭐⭐⭐⭐（困难）
- **特点**：
  - 转转的回收服务
  - 可能需要登录
  - 反爬机制较强
- **爬取方式**：
  - 浏览器自动化 + 可能需要登录
  - 分析API端点
- **注意事项**：
  - 需要处理登录状态
  - 可能有验证码
  - 反爬机制复杂

#### 7. **闲鱼** (https://www.goofish.com / https://2.taobao.com)
- **难度**：⭐⭐⭐⭐（中等）
- **特点**：
  - C2C平台，价格波动大
  - 可以作为市场参考价
  - 搜索页面相对简单
- **爬取方式**：
  - HTTP请求 + HTML解析
  - 可以获取多个商品价格，计算平均值
- **注意事项**：
  - 价格是C2C价格，不是回收价
  - 需要计算平均价格
  - 可能有反爬机制

### ⭐⭐⭐⭐⭐ 非常困难（不推荐）

#### 8. **其他平台**
- **有得卖** (https://www.youde.com)
- **换换回收** (https://www.huanhuan.com)
- **速回收** (https://www.suhuishou.com)
- **难度**：⭐⭐⭐⭐⭐（非常困难）
- **特点**：
  - 反爬机制强
  - 可能需要复杂的认证
  - 不推荐爬取

## 二、爬取难度对比表

| 平台 | 网址 | 难度 | 推荐方式 | 是否需要登录 | 反爬强度 |
|------|------|------|----------|--------------|----------|
| 回收宝 | huishoubao.com | ⭐⭐ | HTTP+BS4 | 否 | 低 |
| 京回收 | shouji.jhuishou.com | ⭐⭐ | HTTP+BS4 | 否 | 低 |
| 苏宁回收 | hx.suning.com | ⭐⭐⭐ | HTTP+BS4 | 可能 | 中 |
| 爱回收 | aihuishou.com | ⭐⭐⭐⭐ | Playwright | 否 | 中 |
| 京东回收 | huishou.m.jd.com | ⭐⭐⭐⭐ | Playwright | 可能 | 中高 |
| 闲鱼 | goofish.com | ⭐⭐⭐⭐ | HTTP+BS4 | 否 | 中 |
| 转转 | zhuanzhuan.com | ⭐⭐⭐⭐⭐ | Playwright+登录 | 是 | 高 |

## 三、推荐爬取方案

### 方案1：简单HTTP爬取（推荐用于快速测试）

**适用平台**：回收宝、京回收、苏宁回收

```python
import requests
from bs4 import BeautifulSoup

def scrape_simple_platform(url, search_query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, params={'q': search_query}, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 解析价格...
```

### 方案2：浏览器自动化（推荐用于SPA应用）

**适用平台**：爱回收、京东回收

```python
from playwright.sync_api import sync_playwright

def scrape_spa_platform(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        # 等待加载、填写问卷、提取价格...
```

## 四、已实现的爬虫

### 1. 爱回收爬虫 ✅
- **文件**：`backend/app/secondhand_app/aihuishou_scraper.py`
- **方式**：Playwright浏览器自动化
- **功能**：
  - 自动填写问卷（选择最佳值）
  - 从页面文本或API响应提取价格
  - 支持缓存

### 2. 通用爬虫服务 ✅
- **文件**：`backend/app/secondhand_app/scraper_service.py`
- **支持平台**：
  - 爱回收（需要改进）
  - 回收宝（基础实现）
  - 闲鱼（基础实现）

## 五、爬取建议

### 1. 优先使用官方API
- 如果平台提供官方API，优先使用
- 更稳定、更合规

### 2. 遵守robots.txt
- 检查网站的robots.txt
- 尊重网站的爬取规则

### 3. 控制请求频率
- 添加请求延迟（建议2-5秒）
- 避免过于频繁的请求
- 使用缓存机制

### 4. 处理反爬机制
- 使用真实的User-Agent
- 设置合理的请求头
- 可能需要处理Cookie、验证码等

### 5. 错误处理
- 完善的异常处理
- 失败时返回None，不影响主流程
- 记录日志便于调试

## 六、实现示例

### 添加新平台爬虫

在 `scraper_service.py` 中添加新方法：

```python
def _scrape_new_platform(self, device_type, brand, model, storage, condition):
    """爬取新平台价格"""
    try:
        # 构建URL
        url = f"https://example.com/search?q={brand} {model}"
        
        # 发送请求
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找价格元素（需要根据实际HTML结构调整）
        price_elements = soup.select('.price-selector')
        
        for element in price_elements:
            text = element.get_text(strip=True)
            price_match = re.search(r'[\d,]+', text.replace(',', ''))
            if price_match:
                price = float(price_match.group().replace(',', ''))
                if 100 <= price <= 50000:
                    logger.info(f"从新平台获取价格: {price}")
                    return price
    except Exception as e:
        logger.error(f"爬取新平台异常: {e}")
    
    return None
```

然后在 `estimate` 方法中调用：

```python
# 4. 尝试新平台
try:
    price = self._scrape_new_platform(device_type, brand, model, storage, condition)
    if price:
        cache.set(cache_key, price, self.cache_timeout)
        return price
except Exception as e:
    logger.warning(f"爬取新平台失败: {e}")
```

## 七、法律与合规提醒

1. **遵守服务条款**：爬取前检查网站的服务条款
2. **合理使用**：仅用于学习研究，不要用于商业用途
3. **尊重版权**：不要大量复制网站内容
4. **保护隐私**：不要爬取用户个人信息
5. **建议**：优先联系平台获取官方API接口

## 八、总结

**推荐爬取的平台**（按优先级）：
1. ✅ **回收宝** - 最简单，HTML页面
2. ✅ **京回收** - 简单，HTML页面
3. ✅ **爱回收** - 已实现，Playwright自动化
4. ⚠️ **京东回收** - 中等难度，可能需要登录
5. ⚠️ **闲鱼** - 作为市场参考价，价格波动大

**不推荐爬取**：
- 转转（反爬强，需要登录）
- 其他小平台（反爬机制复杂）

**最佳实践**：
- 使用缓存减少请求
- 添加请求延迟
- 完善的错误处理
- 记录日志便于调试


