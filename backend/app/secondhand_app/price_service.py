"""
第三方估价服务接口
支持接入多个第三方估价API提供商
"""
import requests
import logging
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# 尝试加载本地价格模型数据（手机价目表）
try:
    from .price_model import price_model  # type: ignore
    PHONE_PRICE_DATABASE = getattr(price_model, 'price_database', {})
except Exception as exc:  # pragma: no cover - 兜底
    logger.warning(f"加载本地价格模型失败: {exc}")
    price_model = None  # type: ignore
    PHONE_PRICE_DATABASE: Dict = {}

# 默认本地价格表（用于估价与目录下发）
DEFAULT_LOCAL_PRICE_TABLE = {
    '手机': {
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
        'vivo': {
            'X100 Pro': {'256GB': 3200, '512GB': 4000},
            'X100': {'256GB': 2500, '512GB': 3200},
        },
        'OPPO': {
            'Find X6 Pro': {'256GB': 3000, '512GB': 3800},
            'Find X6': {'256GB': 2400, '512GB': 3000},
        },
    },
    '平板': {
        '苹果': {
            'iPad Pro 12.9': {'128GB': 4500, '256GB': 5500, '512GB': 7000, '1TB': 9000},
            'iPad Pro 11': {'128GB': 3500, '256GB': 4500, '512GB': 6000, '1TB': 8000},
            'iPad Air': {'64GB': 2500, '256GB': 3500},
            'iPad': {'64GB': 1800, '256GB': 2800},
        },
        '华为': {
            'MatePad Pro': {'128GB': 2500, '256GB': 3200},
            'MatePad': {'64GB': 1200, '128GB': 1800},
        },
    },
    '笔记本': {
        '苹果': {
            'MacBook Pro 16': {'512GB': 8000, '1TB': 10000, '2TB': 12000},
            'MacBook Pro 14': {'512GB': 7000, '1TB': 9000, '2TB': 11000},
            'MacBook Air': {'256GB': 5500, '512GB': 7000, '1TB': 9000},
        },
        '联想': {
            'ThinkPad X1': {'512GB': 4500, '1TB': 5500},
            '小新16': {'512GB': 3000, '1TB': 4000},
        },
    },
}

# 合并价格模型中的手机价目表，确保目录与估价数据源一致
PHONE_PRICE_TABLE = {**DEFAULT_LOCAL_PRICE_TABLE.get('手机', {})}
for _brand, _models in PHONE_PRICE_DATABASE.items():
    merged_models = PHONE_PRICE_TABLE.get(_brand, {}).copy()
    merged_models.update(_models)
    PHONE_PRICE_TABLE[_brand] = merged_models

LOCAL_PRICE_TABLE = {**DEFAULT_LOCAL_PRICE_TABLE, '手机': PHONE_PRICE_TABLE}

# 可选：启用爬取服务（仅供学习研究，不推荐用于生产环境）
ENABLE_SCRAPER = getattr(settings, 'ENABLE_PRICE_SCRAPER', False)
if ENABLE_SCRAPER:
    try:
        from .scraper_service import scraper_service
    except ImportError:
        scraper_service = None
        logger.warning("爬取服务导入失败，请确保已安装beautifulsoup4")
else:
    scraper_service = None

# 可选：启用公开API服务
ENABLE_PUBLIC_API = getattr(settings, 'ENABLE_PUBLIC_API', False)
if ENABLE_PUBLIC_API:
    try:
        from .public_api_service import public_api_service
    except ImportError:
        public_api_service = None
        logger.warning("公开API服务导入失败")
else:
    public_api_service = None


class PriceEstimateService:
    """估价服务基类"""
    
    def __init__(self):
        self.api_enabled = getattr(settings, 'PRICE_API_ENABLED', False)
        self.api_provider = getattr(settings, 'PRICE_API_PROVIDER', 'local')  # local, aihuishou, huishoubao
        self.cache_timeout = getattr(settings, 'PRICE_CACHE_TIMEOUT', 3600)  # 1小时缓存
        
    def estimate(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Tuple[float, bool]:
        """
        估价方法
        返回: (价格, 是否来自API)
        """
        # 生成缓存key
        cache_key = f"price_estimate_{device_type}_{brand}_{model}_{storage}_{condition}"
        
        # 尝试从缓存获取
        cached_price = cache.get(cache_key)
        if cached_price is not None:
            logger.info(f"从缓存获取价格: {cache_key} = {cached_price}")
            return cached_price, False
        
        # 如果启用了API，尝试调用第三方接口
        if self.api_enabled and self.api_provider != 'local':
            try:
                price = self._call_third_party_api(device_type, brand, model, storage, condition)
                if price and price > 0:
                    # 根据成色调整价格
                    adjusted_price = self._adjust_by_condition(price, condition)
                    # 缓存结果
                    cache.set(cache_key, adjusted_price, self.cache_timeout)
                    logger.info(f"第三方API返回价格: {cache_key} = {adjusted_price}")
                    return adjusted_price, True
            except Exception as e:
                logger.warning(f"第三方API调用失败: {e}，降级到本地价格表")
        
        # 如果启用了公开API服务
        if ENABLE_PUBLIC_API and public_api_service:
            try:
                price = public_api_service.estimate(device_type, brand, model, storage, condition)
                if price and price > 0:
                    # 根据成色调整价格
                    adjusted_price = self._adjust_by_condition(price, condition)
                    # 缓存结果
                    cache.set(cache_key, adjusted_price, self.cache_timeout)
                    logger.info(f"公开API返回价格: {cache_key} = {adjusted_price}")
                    return adjusted_price, True
            except Exception as e:
                logger.warning(f"公开API失败: {e}，降级到本地价格表")
        
        # 如果启用了爬取服务（仅供学习研究）
        if ENABLE_SCRAPER and scraper_service:
            try:
                price = scraper_service.estimate(device_type, brand, model, storage, condition)
                if price and price > 0:
                    # 根据成色调整价格
                    adjusted_price = self._adjust_by_condition(price, condition)
                    # 缓存结果
                    cache.set(cache_key, adjusted_price, self.cache_timeout)
                    logger.info(f"爬取服务返回价格: {cache_key} = {adjusted_price}")
                    return adjusted_price, True
            except Exception as e:
                logger.warning(f"爬取服务失败: {e}，降级到本地价格表")
        
        # 降级到本地价格表
        price = self._get_local_price(device_type, brand, model, storage, condition)
        if price > 0:
            cache.set(cache_key, price, self.cache_timeout)
        return price, False
    
    def _call_third_party_api(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """调用第三方API"""
        if self.api_provider == 'aihuishou':
            return self._call_aihuishou_api(device_type, brand, model, storage, condition)
        elif self.api_provider == 'huishoubao':
            return self._call_huishoubao_api(device_type, brand, model, storage, condition)
        elif self.api_provider == 'custom':
            return self._call_custom_api(device_type, brand, model, storage, condition)
        return None
    
    def _call_aihuishou_api(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        调用爱回收API（示例实现）
        注意：需要联系爱回收获取实际的API文档和密钥
        """
        api_url = getattr(settings, 'AIHUISHOU_API_URL', '')
        api_key = getattr(settings, 'AIHUISHOU_API_KEY', '')
        api_secret = getattr(settings, 'AIHUISHOU_API_SECRET', '')
        
        if not all([api_url, api_key, api_secret]):
            logger.warning("爱回收API配置不完整")
            return None
        
        try:
            # 构建请求参数（根据实际API文档调整）
            params = {
                'device_type': device_type,
                'brand': brand,
                'model': model,
                'storage': storage,
                'condition': condition,
            }
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                api_url,
                json=params,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # 根据实际API返回格式解析价格
                price = data.get('price') or data.get('estimated_price') or data.get('amount')
                if price:
                    return float(price)
            
            logger.warning(f"爱回收API返回错误: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"调用爱回收API异常: {e}")
            return None
    
    def _call_huishoubao_api(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        调用回收宝API（示例实现）
        注意：需要联系回收宝获取实际的API文档和密钥
        """
        api_url = getattr(settings, 'HUISHOUBAO_API_URL', '')
        api_key = getattr(settings, 'HUISHOUBAO_API_KEY', '')
        api_secret = getattr(settings, 'HUISHOUBAO_API_SECRET', '')
        
        if not all([api_url, api_key, api_secret]):
            logger.warning("回收宝API配置不完整")
            return None
        
        try:
            # 构建请求参数（根据实际API文档调整）
            params = {
                'device_type': device_type,
                'brand': brand,
                'model': model,
                'storage': storage,
                'condition': condition,
            }
            
            headers = {
                'X-API-Key': api_key,
                'X-API-Secret': api_secret,
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                api_url,
                json=params,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                price = data.get('price') or data.get('estimated_price') or data.get('amount')
                if price:
                    return float(price)
            
            logger.warning(f"回收宝API返回错误: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"调用回收宝API异常: {e}")
            return None
    
    def _call_custom_api(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        调用自定义API（通用实现）
        支持通过配置文件自定义API端点
        """
        api_url = getattr(settings, 'CUSTOM_PRICE_API_URL', '')
        api_key = getattr(settings, 'CUSTOM_PRICE_API_KEY', '')
        api_method = getattr(settings, 'CUSTOM_PRICE_API_METHOD', 'POST').upper()
        api_auth_type = getattr(settings, 'CUSTOM_PRICE_API_AUTH_TYPE', 'bearer')  # bearer, header, query
        
        if not api_url:
            logger.warning("自定义API URL未配置")
            return None
        
        try:
            params = {
                'device_type': device_type,
                'brand': brand,
                'model': model,
                'storage': storage,
                'condition': condition,
            }
            
            headers = {'Content-Type': 'application/json'}
            
            # 根据认证类型设置认证信息
            if api_auth_type == 'bearer' and api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            elif api_auth_type == 'header' and api_key:
                headers['X-API-Key'] = api_key
            elif api_auth_type == 'query' and api_key:
                params['api_key'] = api_key
            
            if api_method == 'POST':
                response = requests.post(api_url, json=params, headers=headers, timeout=5)
            else:
                response = requests.get(api_url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # 支持多种返回格式
                price = (
                    data.get('price') or 
                    data.get('estimated_price') or 
                    data.get('amount') or 
                    data.get('data', {}).get('price') or
                    data.get('result', {}).get('price')
                )
                if price:
                    return float(price)
            
            logger.warning(f"自定义API返回错误: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"调用自定义API异常: {e}")
            return None
    
    def _adjust_by_condition(self, base_price: float, condition: str) -> float:
        """根据成色调整价格"""
        condition_multipliers = {
            'new': 1.0,
            'like_new': 0.85,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
        multiplier = condition_multipliers.get(condition, 0.7)
        return base_price * multiplier
    
    def _get_local_price(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> float:
        """从本地价格表获取价格"""
        # 优先使用智能估价模型
        try:
            if price_model and device_type == '手机':  # type: ignore
                price = price_model.estimate(brand, model, storage, condition)  # type: ignore
                if price > 0:
                    logger.info(f"使用智能估价模型: {brand} {model} {storage} = {price}")
                    return price
        except Exception as e:
            logger.warning(f"智能估价模型失败: {e}，降级到基础价格表")
        
        # 降级到基础价格表
        base_prices = LOCAL_PRICE_TABLE
        
        # 获取基础价格
        try:
            base_price = base_prices.get(device_type, {}).get(brand, {}).get(model, {}).get(storage, 0)
            if base_price == 0:
                # 如果没有找到精确匹配，尝试模糊匹配
                for key, value in base_prices.get(device_type, {}).get(brand, {}).items():
                    if key in model or model in key:
                        base_price = value.get(storage, list(value.values())[0] if value else 0)
                        break
        except:
            base_price = 1000  # 默认价格
        
        # 根据成色调整价格
        return self._adjust_by_condition(base_price, condition)


# 全局服务实例
price_service = PriceEstimateService()

