# 爱回收价格爬取说明

## 问题分析

爱回收移动端（`https://m.aihuishou.com`）是一个单页应用（SPA），价格数据通过JavaScript动态加载，直接HTTP请求无法获取价格。

## 解决方案

### 方案1：使用浏览器自动化（推荐）

#### 使用Selenium

1. **安装依赖**：
```bash
pip install selenium
```

2. **下载ChromeDriver**：
   - 访问：https://chromedriver.chromium.org/
   - 下载与Chrome版本匹配的驱动
   - 将驱动放到PATH环境变量中

3. **运行测试脚本**：
```bash
python scripts/test_aihuishou_selenium.py
```

#### 使用Playwright（更现代，推荐）

1. **安装依赖**：
```bash
pip install playwright
playwright install chromium
```

2. **运行测试脚本**：
```bash
python scripts/test_aihuishou_selenium.py
```

### 方案2：分析网络请求找到API端点

1. **使用浏览器开发者工具**：
   - 打开Chrome/Firefox
   - 按F12打开开发者工具
   - 切换到Network（网络）标签
   - 访问：https://m.aihuishou.com/n/#/inquiry?productId=225361
   - 筛选XHR/Fetch请求
   - 查找返回价格数据的API请求

2. **常见的API端点可能是**：
   - `/api/product/inquiry`
   - `/api/v1/product/price`
   - `/api/inquiry/estimate`
   - `/api/product/{productId}/price`

3. **查看请求详情**：
   - 请求URL
   - 请求方法（GET/POST）
   - 请求头（可能需要Authorization token）
   - 请求参数
   - 响应数据格式

### 方案3：使用现有的爬虫服务

项目中的 `scraper_service.py` 已经实现了基础的爱回收爬取功能，但需要根据实际网站结构调整选择器。

## 使用示例

### 更新scraper_service.py

如果找到了实际的API端点或价格元素选择器，可以更新 `backend/app/secondhand_app/scraper_service.py` 中的 `_scrape_aihuishou` 方法。

### 集成到价格服务

价格服务会自动调用爬虫服务：

```python
from app.secondhand_app.scraper_service import scraper_service

price = scraper_service.estimate(
    device_type="手机",
    brand="苹果",
    model="iPhone 13",
    storage="256GB",
    condition="good"
)
```

## 注意事项

1. **遵守robots.txt**：检查爱回收的robots.txt，确保爬取行为合规
2. **请求频率**：避免过于频繁的请求，建议添加延迟
3. **缓存机制**：已实现缓存机制，避免重复请求
4. **错误处理**：网络异常时返回None，不影响主流程
5. **法律风险**：爬取第三方网站可能违反服务条款，建议优先使用官方API

## 测试脚本

- `test_aihuishou_price.py`：基础HTTP请求测试
- `test_aihuishou_selenium.py`：浏览器自动化测试（Selenium/Playwright）

## 下一步

1. 使用浏览器开发者工具分析实际API端点
2. 如果找到API，更新 `scraper_service.py` 中的实现
3. 如果使用浏览器自动化，确保ChromeDriver/Playwright已正确安装
4. 测试并验证价格获取功能

