"""
公开API服务集成
支持接入多种公开的数据API服务
"""
import requests
import logging
from typing import Optional, Dict
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PublicAPIService:
    """公开API服务"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1小时缓存
        
    def estimate(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        通过公开API获取价格
        支持多种数据源
        """
        cache_key = f"public_api_price_{device_type}_{brand}_{model}_{storage}_{condition}"
        
        # 检查缓存
        cached_price = cache.get(cache_key)
        if cached_price:
            return cached_price
        
        # 尝试多个数据源
        price = None
        
        # 1. 聚合数据API（如果有配置）
        if getattr(settings, 'JUHE_API_KEY', None):
            try:
                price = self._juhe_api(brand, model, storage)
                if price:
                    cache.set(cache_key, price, self.cache_timeout)
                    return price
            except Exception as e:
                logger.warning(f"聚合数据API失败: {e}")
        
        # 2. 百度API（如果有配置）
        if getattr(settings, 'BAIDU_API_KEY', None):
            try:
                price = self._baidu_api(brand, model, storage)
                if price:
                    cache.set(cache_key, price, self.cache_timeout)
                    return price
            except Exception as e:
                logger.warning(f"百度API失败: {e}")
        
        # 3. 阿里云API（如果有配置）
        if getattr(settings, 'ALIYUN_API_KEY', None):
            try:
                price = self._aliyun_api(brand, model, storage)
                if price:
                    cache.set(cache_key, price, self.cache_timeout)
                    return price
            except Exception as e:
                logger.warning(f"阿里云API失败: {e}")
        
        # 4. 使用公开的价格数据库（基于市场数据）
        try:
            price = self._market_price_database(brand, model, storage)
            if price:
                cache.set(cache_key, price, self.cache_timeout)
                return price
        except Exception as e:
            logger.warning(f"市场价格数据库失败: {e}")
        
        return None
    
    def _juhe_api(self, brand: str, model: str, storage: str) -> Optional[float]:
        """
        聚合数据API
        注册地址：https://www.juhe.cn
        """
        api_key = getattr(settings, 'JUHE_API_KEY', '')
        api_url = getattr(settings, 'JUHE_PRICE_API_URL', '')
        
        if not api_key or not api_url:
            return None
        
        try:
            params = {
                'key': api_key,
                'brand': brand,
                'model': model,
                'storage': storage,
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('error_code') == 0:
                    price = data.get('result', {}).get('price')
                    if price:
                        return float(price)
        except Exception as e:
            logger.error(f"聚合数据API调用异常: {e}")
        
        return None
    
    def _baidu_api(self, brand: str, model: str, storage: str) -> Optional[float]:
        """
        百度API（示例）
        需要根据实际API文档调整
        """
        api_key = getattr(settings, 'BAIDU_API_KEY', '')
        api_url = getattr(settings, 'BAIDU_PRICE_API_URL', '')
        
        if not api_key or not api_url:
            return None
        
        try:
            params = {
                'ak': api_key,
                'brand': brand,
                'model': model,
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 根据实际API响应格式解析
                price = data.get('price') or data.get('result', {}).get('price')
                if price:
                    return float(price)
        except Exception as e:
            logger.error(f"百度API调用异常: {e}")
        
        return None
    
    def _aliyun_api(self, brand: str, model: str, storage: str) -> Optional[float]:
        """
        阿里云API（示例）
        需要根据实际API文档调整
        """
        api_key = getattr(settings, 'ALIYUN_API_KEY', '')
        api_secret = getattr(settings, 'ALIYUN_API_SECRET', '')
        api_url = getattr(settings, 'ALIYUN_PRICE_API_URL', '')
        
        if not all([api_key, api_secret, api_url]):
            return None
        
        try:
            # 阿里云API通常需要签名
            # 这里需要根据实际API文档实现签名逻辑
            params = {
                'brand': brand,
                'model': model,
                'storage': storage,
            }
            
            # 添加签名（示例）
            # signature = self._generate_aliyun_signature(params, api_secret)
            # params['signature'] = signature
            
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = data.get('price') or data.get('data', {}).get('price')
                if price:
                    return float(price)
        except Exception as e:
            logger.error(f"阿里云API调用异常: {e}")
        
        return None
    
    def _market_price_database(self, brand: str, model: str, storage: str) -> Optional[float]:
        """
        基于公开市场数据的价格估算
        使用公开的价格数据库或市场行情数据
        """
        # 这里可以使用一些公开的价格数据源
        # 例如：从公开的价格表、市场报告等获取
        
        # 示例：基于品牌和型号的估算（简化版）
        base_prices = {
            '苹果': {
                'iPhone 15 Pro Max': {'128GB': 6500, '256GB': 7200, '512GB': 8500, '1TB': 10000},
                'iPhone 15 Pro': {'128GB': 5500, '256GB': 6200, '512GB': 7500},
                'iPhone 15': {'128GB': 4500, '256GB': 5200, '512GB': 6500},
                'iPhone 14 Pro Max': {'128GB': 5500, '256GB': 6200, '512GB': 7500, '1TB': 9000},
                'iPhone 14 Pro': {'128GB': 4800, '256GB': 5500, '512GB': 6800},
                'iPhone 14': {'128GB': 3800, '256GB': 4500, '512GB': 5800},
                'iPhone 13 Pro Max': {'128GB': 4500, '256GB': 5200, '512GB': 6500, '1TB': 8000},
                'iPhone 13 Pro': {'128GB': 4000, '256GB': 4700, '512GB': 6000},
                'iPhone 13': {'128GB': 3200, '256GB': 3900, '512GB': 5200},
            },
            '华为': {
                'Mate 60 Pro': {'256GB': 4500, '512GB': 5500, '1TB': 6500},
                'Mate 60': {'256GB': 3800, '512GB': 4800},
                'P60 Pro': {'256GB': 3500, '512GB': 4500},
                'P60': {'128GB': 2800, '256GB': 3500},
            },
            '小米': {
                '小米14 Pro': {'256GB': 2800, '512GB': 3500, '1TB': 4200},
                '小米14': {'256GB': 2200, '512GB': 2800},
                '小米13 Ultra': {'256GB': 3000, '512GB': 3800},
                '小米13': {'128GB': 1800, '256GB': 2400, '512GB': 3000},
            },
        }
        
        try:
            price = base_prices.get(brand, {}).get(model, {}).get(storage)
            if price:
                return float(price)
        except:
            pass
        
        return None


# 全局服务实例
public_api_service = PublicAPIService()

