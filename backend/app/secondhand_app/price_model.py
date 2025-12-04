"""
智能估价算法模型
包含市面上主流手机的价格数据和估价逻辑
"""
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PriceEstimateModel:
    """价格估算模型"""
    
    def __init__(self):
        # 品牌系数（品牌保值率）
        self.brand_multipliers = {
            '苹果': 1.0,      # 基准
            '华为': 0.85,
            '小米': 0.75,
            'OPPO': 0.70,
            'vivo': 0.70,
            '荣耀': 0.75,
            '三星': 0.80,
            '一加': 0.75,
            'realme': 0.65,
            '红米': 0.65,
        }
        
        # 成色系数
        self.condition_multipliers = {
            'new': 1.0,           # 全新
            'like_new': 0.85,     # 几乎全新
            'good': 0.70,         # 良好
            'fair': 0.50,         # 一般
            'poor': 0.30,         # 较差
        }
        
        # 存储容量系数（相对于128GB）
        self.storage_multipliers = {
            '64GB': 0.85,
            '128GB': 1.0,
            '256GB': 1.15,
            '512GB': 1.35,
            '1TB': 1.60,
            '2TB': 2.0,
        }
        
    def estimate(self, brand: str, model: str, storage: str, condition: str, 
                 release_year: Optional[int] = None) -> float:
        """
        估算价格
        
        参数:
            brand: 品牌
            model: 型号
            storage: 存储容量
            condition: 成色
            release_year: 发布年份（可选）
        
        返回:
            估算价格（元）
        """
        # 1. 获取基础价格
        base_price = self._get_base_price(brand, model, storage)
        if base_price == 0:
            logger.warning(f"未找到 {brand} {model} {storage} 的价格数据")
            return 0
        
        # 2. 应用存储系数
        storage_mult = self.storage_multipliers.get(storage, 1.0)
        adjusted_price = base_price * storage_mult
        
        # 3. 应用品牌系数
        brand_mult = self.brand_multipliers.get(brand, 0.75)
        adjusted_price = adjusted_price * brand_mult
        
        # 4. 应用成色系数
        condition_mult = self.condition_multipliers.get(condition, 0.7)
        adjusted_price = adjusted_price * condition_mult
        
        # 5. 应用时间衰减（如果提供了发布年份）
        if release_year:
            age_mult = self._calculate_age_multiplier(release_year)
            adjusted_price = adjusted_price * age_mult
        
        return round(adjusted_price, 2)
    
    def _get_base_price(self, brand: str, model: str, storage: str) -> float:
        """获取基础价格（128GB版本的价格）"""
        # 标准化型号名称
        model_normalized = self._normalize_model(model)
        
        # 查找价格数据
        brand_data = self.price_database.get(brand, {})
        model_data = brand_data.get(model_normalized, {})
        
        # 优先使用128GB作为基准
        base_storage = '128GB'
        base_price = model_data.get(base_storage, 0)
        
        # 如果没有128GB，尝试其他存储
        if base_price == 0:
            for storage_key in ['256GB', '512GB', '64GB', '1TB']:
                if storage_key in model_data:
                    # 反向计算128GB价格
                    storage_mult = self.storage_multipliers.get(storage_key, 1.0)
                    base_price = model_data[storage_key] / storage_mult
                    break
        
        return base_price
    
    def _normalize_model(self, model: str) -> str:
        """标准化型号名称"""
        # 统一格式，去除多余空格
        model = model.strip()
        # 统一iPhone命名
        if 'iphone' in model.lower():
            model = model.replace('iPhone', 'iPhone').replace('iphone', 'iPhone')
        return model
    
    def _calculate_age_multiplier(self, release_year: int) -> float:
        """计算时间衰减系数"""
        current_year = datetime.now().year
        age = current_year - release_year
        
        # 根据使用年限计算衰减
        if age <= 0:
            return 1.0
        elif age == 1:
            return 0.85
        elif age == 2:
            return 0.70
        elif age == 3:
            return 0.55
        elif age == 4:
            return 0.40
        else:
            return max(0.25, 1.0 - age * 0.15)
    
    # 价格数据库（2024年12月市场价格，单位：元）
    price_database = {
        '苹果': {
            # iPhone 15 系列
            'iPhone 15 Pro Max': {
                '128GB': 6500, '256GB': 7200, '512GB': 8500, '1TB': 10000
            },
            'iPhone 15 Pro': {
                '128GB': 5500, '256GB': 6200, '512GB': 7500, '1TB': 9000
            },
            'iPhone 15 Plus': {
                '128GB': 4800, '256GB': 5500, '512GB': 6800
            },
            'iPhone 15': {
                '128GB': 4200, '256GB': 4900, '512GB': 6200
            },
            
            # iPhone 14 系列
            'iPhone 14 Pro Max': {
                '128GB': 5500, '256GB': 6200, '512GB': 7500, '1TB': 9000
            },
            'iPhone 14 Pro': {
                '128GB': 4800, '256GB': 5500, '512GB': 6800, '1TB': 8200
            },
            'iPhone 14 Plus': {
                '128GB': 4000, '256GB': 4700, '512GB': 6000
            },
            'iPhone 14': {
                '128GB': 3500, '256GB': 4200, '512GB': 5500
            },
            
            # iPhone 13 系列
            'iPhone 13 Pro Max': {
                '128GB': 4500, '256GB': 5200, '512GB': 6500, '1TB': 8000
            },
            'iPhone 13 Pro': {
                '128GB': 4000, '256GB': 4700, '512GB': 6000, '1TB': 7500
            },
            'iPhone 13': {
                '128GB': 3200, '256GB': 3900, '512GB': 5200
            },
            'iPhone 13 mini': {
                '128GB': 2800, '256GB': 3500, '512GB': 4800
            },
            
            # iPhone 12 系列
            'iPhone 12 Pro Max': {
                '128GB': 3500, '256GB': 4200, '512GB': 5500
            },
            'iPhone 12 Pro': {
                '128GB': 3000, '256GB': 3700, '512GB': 5000
            },
            'iPhone 12': {
                '128GB': 2500, '256GB': 3200, '512GB': 4500
            },
            'iPhone 12 mini': {
                '128GB': 2200, '256GB': 2900
            },
            
            # iPhone 11 系列
            'iPhone 11 Pro Max': {
                '64GB': 2800, '256GB': 3500, '512GB': 4800
            },
            'iPhone 11 Pro': {
                '64GB': 2400, '256GB': 3100, '512GB': 4400
            },
            'iPhone 11': {
                '64GB': 1800, '128GB': 2200, '256GB': 2900
            },
        },
        
        '华为': {
            # Mate 60 系列
            'Mate 60 Pro': {
                '256GB': 4500, '512GB': 5500, '1TB': 6500
            },
            'Mate 60': {
                '256GB': 3800, '512GB': 4800
            },
            'Mate 60 Pro+': {
                '512GB': 6000, '1TB': 7000
            },
            
            # Mate 50 系列
            'Mate 50 Pro': {
                '256GB': 3500, '512GB': 4500
            },
            'Mate 50': {
                '128GB': 2800, '256GB': 3500, '512GB': 4500
            },
            
            # P60 系列
            'P60 Pro': {
                '256GB': 3500, '512GB': 4500, '1TB': 5500
            },
            'P60': {
                '128GB': 2800, '256GB': 3500, '512GB': 4500
            },
            'P60 Art': {
                '512GB': 5000, '1TB': 6000
            },
            
            # P50 系列
            'P50 Pro': {
                '128GB': 2500, '256GB': 3200, '512GB': 4200
            },
            'P50': {
                '128GB': 2000, '256GB': 2700
            },
            
            # nova 系列
            'nova 12': {
                '256GB': 2000, '512GB': 2800
            },
            'nova 11': {
                '128GB': 1500, '256GB': 2200
            },
        },
        
        '小米': {
            # 小米14 系列
            '小米14 Pro': {
                '256GB': 2800, '512GB': 3500, '1TB': 4200
            },
            '小米14': {
                '256GB': 2200, '512GB': 2800, '1TB': 3500
            },
            '小米14 Ultra': {
                '512GB': 3800, '1TB': 4500
            },
            
            # 小米13 系列
            '小米13 Ultra': {
                '256GB': 3000, '512GB': 3800, '1TB': 4500
            },
            '小米13 Pro': {
                '256GB': 2500, '512GB': 3200
            },
            '小米13': {
                '128GB': 1800, '256GB': 2400, '512GB': 3000
            },
            
            # 小米12 系列
            '小米12S Ultra': {
                '256GB': 2500, '512GB': 3200
            },
            '小米12 Pro': {
                '128GB': 1800, '256GB': 2400
            },
            '小米12': {
                '128GB': 1500, '256GB': 2000
            },
        },
        
        'vivo': {
            # X100 系列
            'X100 Pro': {
                '256GB': 3200, '512GB': 4000, '1TB': 4800
            },
            'X100': {
                '256GB': 2500, '512GB': 3200, '1TB': 4000
            },
            
            # X90 系列
            'X90 Pro+': {
                '256GB': 2800, '512GB': 3600
            },
            'X90 Pro': {
                '256GB': 2400, '512GB': 3200
            },
            'X90': {
                '128GB': 2000, '256GB': 2600
            },
            
            # S 系列
            'S18 Pro': {
                '256GB': 2000, '512GB': 2800
            },
            'S17 Pro': {
                '256GB': 1800, '512GB': 2500
            },
        },
        
        'OPPO': {
            # Find X 系列
            'Find X7 Ultra': {
                '256GB': 3000, '512GB': 3800, '1TB': 4600
            },
            'Find X6 Pro': {
                '256GB': 3000, '512GB': 3800
            },
            'Find X6': {
                '256GB': 2400, '512GB': 3000
            },
            'Find X5 Pro': {
                '256GB': 2200, '512GB': 3000
            },
            
            # Reno 系列
            'Reno11 Pro': {
                '256GB': 2000, '512GB': 2800
            },
            'Reno10 Pro': {
                '256GB': 1800, '512GB': 2500
            },
        },
        
        '荣耀': {
            # Magic 系列
            'Magic6 Pro': {
                '256GB': 2800, '512GB': 3600, '1TB': 4400
            },
            'Magic5 Pro': {
                '256GB': 2500, '512GB': 3300
            },
            'Magic4 Pro': {
                '256GB': 2000, '512GB': 2800
            },
            
            # 数字系列
            '100 Pro': {
                '256GB': 2000, '512GB': 2800
            },
            '90 Pro': {
                '256GB': 1800, '512GB': 2500
            },
        },
        
        '三星': {
            # S 系列
            'Galaxy S24 Ultra': {
                '256GB': 3500, '512GB': 4500, '1TB': 5500
            },
            'Galaxy S24+': {
                '256GB': 2800, '512GB': 3600
            },
            'Galaxy S24': {
                '128GB': 2200, '256GB': 2800
            },
            'Galaxy S23 Ultra': {
                '256GB': 3000, '512GB': 4000, '1TB': 5000
            },
            'Galaxy S23+': {
                '256GB': 2500, '512GB': 3300
            },
            'Galaxy S23': {
                '128GB': 2000, '256GB': 2600
            },
            
            # Note 系列
            'Galaxy Note20 Ultra': {
                '256GB': 2500, '512GB': 3500
            },
        },
        
        '一加': {
            'OnePlus 12': {
                '256GB': 2500, '512GB': 3200, '1TB': 4000
            },
            'OnePlus 11': {
                '256GB': 2200, '512GB': 3000
            },
            'OnePlus Ace 3': {
                '256GB': 2000, '512GB': 2800
            },
        },
        
        'realme': {
            'GT5 Pro': {
                '256GB': 2000, '512GB': 2800, '1TB': 3600
            },
            'GT Neo6': {
                '256GB': 1800, '512GB': 2500
            },
        },
        
        '红米': {
            'Redmi K70 Pro': {
                '256GB': 2000, '512GB': 2800
            },
            'Redmi K70': {
                '256GB': 1800, '512GB': 2500
            },
            'Redmi Note 13 Pro': {
                '256GB': 1500, '512GB': 2200
            },
        },
    }


# 全局模型实例
price_model = PriceEstimateModel()

