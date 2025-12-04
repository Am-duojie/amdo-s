"""
第三方平台价格爬取服务（仅供学习研究使用）
⚠️ 警告：爬取第三方平台可能违反服务条款，请谨慎使用
建议：优先使用官方API接口
"""
import requests
import re
import time
import logging
from typing import Optional, Dict
from bs4 import BeautifulSoup
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PriceScraperService:
    """价格爬取服务"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.cache_timeout = 3600  # 1小时缓存
        self.request_delay = 2  # 请求间隔（秒），避免过于频繁
        
    def estimate(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        通过爬取获取价格
        返回: 价格（元）或None
        """
        cache_key = f"scraped_price_{device_type}_{brand}_{model}_{storage}_{condition}"
        
        # 检查缓存
        cached_price = cache.get(cache_key)
        if cached_price:
            logger.info(f"从缓存获取爬取价格: {cache_key} = {cached_price}")
            return cached_price
        
        # 尝试多个平台
        price = None
        
        # 1. 尝试爱回收
        try:
            price = self._scrape_aihuishou(device_type, brand, model, storage, condition)
            if price:
                cache.set(cache_key, price, self.cache_timeout)
                return price
        except Exception as e:
            logger.warning(f"爬取爱回收失败: {e}")
        
        # 2. 尝试回收宝
        try:
            price = self._scrape_huishoubao(device_type, brand, model, storage, condition)
            if price:
                cache.set(cache_key, price, self.cache_timeout)
                return price
        except Exception as e:
            logger.warning(f"爬取回收宝失败: {e}")
        
        # 3. 尝试闲鱼（作为参考）
        try:
            price = self._scrape_xianyu(device_type, brand, model, storage, condition)
            if price:
                cache.set(cache_key, price, self.cache_timeout)
                return price
        except Exception as e:
            logger.warning(f"爬取闲鱼失败: {e}")
        
        return None
    
    def _scrape_aihuishou(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        爬取爱回收价格
        注意：网站结构可能随时变化，需要定期更新
        """
        try:
            # 构建搜索URL（示例，实际URL需要根据网站结构调整）
            search_query = f"{brand} {model} {storage}"
            # 爱回收的搜索URL格式（需要根据实际情况调整）
            url = f"https://www.aihuishou.com/search?q={search_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找价格元素（需要根据实际HTML结构调整选择器）
            # 示例选择器，实际需要检查网站HTML结构
            price_elements = soup.select('.price, .estimated-price, [class*="price"]')
            
            for element in price_elements:
                text = element.get_text(strip=True)
                # 提取数字
                price_match = re.search(r'[\d,]+', text.replace(',', ''))
                if price_match:
                    price = float(price_match.group().replace(',', ''))
                    # 验证价格合理性（通常在100-50000之间）
                    if 100 <= price <= 50000:
                        logger.info(f"从爱回收获取价格: {price}")
                        return price
            
            # 如果没找到，尝试其他选择器
            # 这里需要根据实际网站结构调整
            
        except Exception as e:
            logger.error(f"爬取爱回收异常: {e}")
        
        return None
    
    def _scrape_huishoubao(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        爬取回收宝价格
        """
        try:
            search_query = f"{brand} {model} {storage}"
            url = f"https://www.huishoubao.com/search?keyword={search_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找价格元素
            price_elements = soup.select('.price, .estimated-price, [class*="price"]')
            
            for element in price_elements:
                text = element.get_text(strip=True)
                price_match = re.search(r'[\d,]+', text.replace(',', ''))
                if price_match:
                    price = float(price_match.group().replace(',', ''))
                    if 100 <= price <= 50000:
                        logger.info(f"从回收宝获取价格: {price}")
                        return price
            
        except Exception as e:
            logger.error(f"爬取回收宝异常: {e}")
        
        return None
    
    def _scrape_xianyu(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        爬取闲鱼价格（作为市场参考价）
        注意：闲鱼是C2C平台，价格波动较大，仅供参考
        """
        try:
            search_query = f"{brand} {model} {storage}"
            # 闲鱼搜索URL
            url = f"https://s.2.taobao.com/list/list.htm?q={search_query}&sort=sale-desc"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找价格元素
            price_elements = soup.select('.price, .item-price, [class*="price"]')
            
            prices = []
            for element in price_elements[:10]:  # 取前10个价格
                text = element.get_text(strip=True)
                price_match = re.search(r'[\d.]+', text)
                if price_match:
                    price = float(price_match.group())
                    if 100 <= price <= 50000:
                        prices.append(price)
            
            if prices:
                # 计算平均价格（去除最高和最低）
                prices.sort()
                if len(prices) > 2:
                    prices = prices[1:-1]
                avg_price = sum(prices) / len(prices)
                logger.info(f"从闲鱼获取平均价格: {avg_price}")
                return avg_price
            
        except Exception as e:
            logger.error(f"爬取闲鱼异常: {e}")
        
        return None
    
    def _scrape_api_endpoint(self, url: str, params: Dict = None) -> Optional[Dict]:
        """
        尝试爬取API端点（如果发现未加密的API）
        注意：这需要分析网站的网络请求
        """
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 尝试解析JSON
            try:
                return response.json()
            except:
                pass
            
            # 尝试解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找JSON数据（可能在script标签中）
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'price' in script.string.lower():
                    # 尝试提取JSON
                    json_match = re.search(r'\{.*"price".*\}', script.string)
                    if json_match:
                        import json
                        try:
                            data = json.loads(json_match.group())
                            return data
                        except:
                            pass
            
        except Exception as e:
            logger.error(f"爬取API端点异常: {e}")
        
        return None


# 全局服务实例
scraper_service = PriceScraperService()

