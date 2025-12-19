"""
第三方估价服务接口（支持接入多个第三方估价 API）。

说明：
- 机型模板与基础价格最终存储在数据库：`admin_api.RecycleDeviceTemplate.base_prices`。
- 为避免“代码里的价目表”和“数据库里的模板”口径不一致，本模块不再内置本地价格表。
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)



# 可选：启用爬取服务（仅学习研究，不建议用于生产）
ENABLE_SCRAPER = getattr(settings, "ENABLE_PRICE_SCRAPER", False)
if ENABLE_SCRAPER:
    try:
        from .scraper_service import scraper_service
    except ImportError:
        scraper_service = None
        logger.warning("爬取服务导入失败：请确保已安装 beautifulsoup4")
else:
    scraper_service = None


# 可选：启用公开 API 服务
ENABLE_PUBLIC_API = getattr(settings, "ENABLE_PUBLIC_API", False)
if ENABLE_PUBLIC_API:
    try:
        from .public_api_service import public_api_service
    except ImportError:
        public_api_service = None
        logger.warning("公开 API 服务导入失败")
else:
    public_api_service = None


class PriceEstimateService:
    """估价服务基类"""

    def __init__(self):
        self.api_enabled = getattr(settings, "PRICE_API_ENABLED", False)
        self.api_provider = getattr(settings, "PRICE_API_PROVIDER", "local")  # local, aihuishou, huishoubao, custom
        self.cache_timeout = getattr(settings, "PRICE_CACHE_TIMEOUT", 3600)

    def estimate(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Tuple[float, bool]:
        """
        估价方法

        Returns:
          (price, from_third_party)
        """
        device_type = (device_type or "").strip()
        brand = (brand or "").strip()
        model = (model or "").strip()
        storage = (storage or "").strip()
        condition = (condition or "").strip()

        cache_key = f"price::{self.api_provider}::{device_type}::{brand}::{model}::{storage}::{condition}"
        cached = cache.get(cache_key)
        if cached is not None:
            return float(cached), True

        # 1) 第三方/自定义 API
        if self.api_enabled:
            try:
                api_price = self._call_third_party_api(device_type, brand, model, storage, condition)
                if api_price is not None and api_price > 0:
                    adjusted = self._adjust_by_condition(float(api_price), condition)
                    cache.set(cache_key, adjusted, self.cache_timeout)
                    return adjusted, True
            except Exception as e:
                logger.warning(f"第三方 API 估价失败: {e}，降级到本地/模板价格")

        # 2) 可选爬取（仅研究用途）
        if scraper_service:
            try:
                price = scraper_service.get_price(device_type, brand, model, storage, condition)  # type: ignore
                if price and float(price) > 0:
                    adjusted = self._adjust_by_condition(float(price), condition)
                    cache.set(cache_key, adjusted, self.cache_timeout)
                    return adjusted, True
            except Exception as e:
                logger.warning(f"爬取服务失败: {e}，降级到数据库模板价格")

        # 3) 数据库模板价格（主口径）
        price = self._get_local_price(device_type, brand, model, storage, condition)
        if price > 0:
            cache.set(cache_key, price, self.cache_timeout)
        return price, False

    def _call_third_party_api(
        self, device_type: str, brand: str, model: str, storage: str, condition: str
    ) -> Optional[float]:
        """调用第三方 API"""
        if self.api_provider == "aihuishou":
            return self._call_aihuishou_api(device_type, brand, model, storage, condition)
        if self.api_provider == "huishoubao":
            return self._call_huishoubao_api(device_type, brand, model, storage, condition)
        if self.api_provider == "custom":
            return self._call_custom_api(device_type, brand, model, storage, condition)
        return None

    def _call_aihuishou_api(
        self, device_type: str, brand: str, model: str, storage: str, condition: str
    ) -> Optional[float]:
        """调用爱回收 API（示例实现，需自行配置真实端点与鉴权信息）"""
        api_url = getattr(settings, "AIHUISHOU_API_URL", "")
        api_key = getattr(settings, "AIHUISHOU_API_KEY", "")
        api_secret = getattr(settings, "AIHUISHOU_API_SECRET", "")
        if not all([api_url, api_key, api_secret]):
            logger.warning("爱回收 API 配置不完整")
            return None

        params = {"device_type": device_type, "brand": brand, "model": model, "storage": storage, "condition": condition}
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(api_url, json=params, headers=headers, timeout=5)
            if response.status_code != 200:
                logger.warning(f"爱回收 API 返回错误: {response.status_code} - {response.text}")
                return None
            data = response.json()
            price = data.get("price") or data.get("estimated_price") or data.get("amount")
            return float(price) if price else None
        except Exception as e:
            logger.error(f"调用爱回收 API 异常: {e}")
            return None

    def _call_huishoubao_api(
        self, device_type: str, brand: str, model: str, storage: str, condition: str
    ) -> Optional[float]:
        """调用回收宝 API（示例实现，需自行配置真实端点与鉴权信息）"""
        api_url = getattr(settings, "HUISHOUBAO_API_URL", "")
        api_key = getattr(settings, "HUISHOUBAO_API_KEY", "")
        api_secret = getattr(settings, "HUISHOUBAO_API_SECRET", "")
        if not all([api_url, api_key, api_secret]):
            logger.warning("回收宝 API 配置不完整")
            return None

        params = {"device_type": device_type, "brand": brand, "model": model, "storage": storage, "condition": condition}
        headers = {"X-API-Key": api_key, "X-API-Secret": api_secret, "Content-Type": "application/json"}
        try:
            response = requests.post(api_url, json=params, headers=headers, timeout=5)
            if response.status_code != 200:
                logger.warning(f"回收宝 API 返回错误: {response.status_code} - {response.text}")
                return None
            data = response.json()
            price = data.get("price") or data.get("estimated_price") or data.get("amount")
            return float(price) if price else None
        except Exception as e:
            logger.error(f"调用回收宝 API 异常: {e}")
            return None

    def _call_custom_api(
        self, device_type: str, brand: str, model: str, storage: str, condition: str
    ) -> Optional[float]:
        """调用自定义 API（通用实现，通过 settings 配置端点）"""
        api_url = getattr(settings, "CUSTOM_PRICE_API_URL", "")
        api_key = getattr(settings, "CUSTOM_PRICE_API_KEY", "")
        api_method = getattr(settings, "CUSTOM_PRICE_API_METHOD", "POST").upper()
        api_auth_type = getattr(settings, "CUSTOM_PRICE_API_AUTH_TYPE", "bearer")  # bearer, header, query

        if not api_url:
            logger.warning("自定义 API URL 未配置")
            return None

        params = {"device_type": device_type, "brand": brand, "model": model, "storage": storage, "condition": condition}
        headers = {"Content-Type": "application/json"}

        if api_auth_type == "bearer" and api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        elif api_auth_type == "header" and api_key:
            headers["X-API-Key"] = api_key
        elif api_auth_type == "query" and api_key:
            params["api_key"] = api_key

        try:
            if api_method == "POST":
                response = requests.post(api_url, json=params, headers=headers, timeout=5)
            else:
                response = requests.get(api_url, params=params, headers=headers, timeout=5)

            if response.status_code != 200:
                logger.warning(f"自定义 API 返回错误: {response.status_code} - {response.text}")
                return None

            data = response.json()
            price = (
                data.get("price")
                or data.get("estimated_price")
                or data.get("amount")
                or data.get("data", {}).get("price")
                or data.get("result", {}).get("price")
            )
            return float(price) if price else None
        except Exception as e:
            logger.error(f"调用自定义 API 异常: {e}")
            return None

    def _adjust_by_condition(self, base_price: float, condition: str) -> float:
        """根据成色调整价格"""
        condition_multipliers = {"new": 1.0, "like_new": 0.85, "good": 0.7, "fair": 0.5, "poor": 0.3}
        multiplier = condition_multipliers.get(condition, 0.7)
        return float(base_price) * multiplier

    def _get_local_price(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> float:
        """从数据库机型模板获取基础价格（如缺失则兜底）。"""
        base_price = 0.0
        try:
            from app.admin_api.models import RecycleDeviceTemplate

            template = RecycleDeviceTemplate.objects.filter(
                device_type=device_type,
                brand=brand,
                model=model,
                is_active=True,
            ).first()
            if template and isinstance(template.base_prices, dict):
                base_price = float(template.base_prices.get(storage) or 0)

            # 模糊匹配（同品牌下型号相近）
            if base_price <= 0:
                candidates = RecycleDeviceTemplate.objects.filter(device_type=device_type, brand=brand, is_active=True)
                for t in candidates:
                    if not t.model:
                        continue
                    if str(t.model) in str(model) or str(model) in str(t.model):
                        if isinstance(t.base_prices, dict):
                            base_price = float(t.base_prices.get(storage) or 0)
                            if base_price > 0:
                                break
        except Exception as e:  # pragma: no cover
            logger.warning(f"从数据库读取机型模板价格失败: {e}")
            base_price = 0.0

        if base_price <= 0:
            base_price = 1000.0  # 兜底默认值

        return self._adjust_by_condition(base_price, condition)


# 全局服务实例
price_service = PriceEstimateService()

