"""
爱回收价格爬取服务（改进版）
基于Playwright浏览器自动化，支持移动端和PC端
"""
import re
import logging
import time
from typing import Optional, Dict
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AihuishouScraper:
    """爱回收爬虫服务"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1小时缓存
        self.request_delay = 2  # 请求间隔（秒）
    
    def get_price_by_product_id(self, product_id: str) -> Optional[float]:
        """
        通过产品ID获取价格
        
        Args:
            product_id: 爱回收产品ID（如 "225361"）
        
        Returns:
            价格（元）或None
        """
        cache_key = f"aihuishou_price_{product_id}"
        
        # 检查缓存
        cached_price = cache.get(cache_key)
        if cached_price:
            logger.info(f"从缓存获取爱回收价格: {cache_key} = {cached_price}")
            return cached_price
        
        # 尝试使用Playwright获取
        try:
            price = self._get_price_with_playwright(product_id)
            if price:
                cache.set(cache_key, price, self.cache_timeout)
                return price
        except Exception as e:
            logger.warning(f"Playwright获取价格失败: {e}")
        
        return None
    
    def _get_price_with_playwright(self, product_id: str) -> Optional[float]:
        """使用Playwright获取价格"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("未安装playwright，请运行: pip install playwright")
            return None
        
        url = f"https://m.aihuishou.com/n/#/inquiry?productId={product_id}"
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                    viewport={'width': 375, 'height': 667},
                )
                page = context.new_page()
                
                # 监听API请求
                api_data = {}
                def handle_response(response):
                    url = response.url
                    if 'inquiry' in url.lower() and 'dubai-gateway' in url.lower():
                        try:
                            if response.ok:
                                data = response.json()
                                api_data['inquiry'] = data
                        except:
                            pass
                
                page.on("response", handle_response)
                
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(5)  # 等待JavaScript执行
                
                # 自动填写问卷（选择不影响价格的最佳值）
                self._fill_questionnaire_with_best_values(page)
                
                # 等待价格更新
                time.sleep(3)
                
                # 方法1: 从API响应中提取价格
                if 'inquiry' in api_data:
                    price = self._extract_price_from_api_data(api_data['inquiry'])
                    if price:
                        browser.close()
                        return price
                
                # 方法2: 从页面文本中提取价格
                all_text = page.inner_text('body')
                price = self._extract_price_from_text(all_text)
                
                browser.close()
                return price
                
            except Exception as e:
                logger.error(f"Playwright获取价格异常: {e}")
                return None
    
    def _extract_price_from_api_data(self, data: Dict) -> Optional[float]:
        """从API响应数据中提取价格"""
        if not isinstance(data, dict):
            return None
        
        # 尝试多个可能的字段
        price_fields = [
            'price', 'Price', 'amount', 'Amount', 'estimatedPrice', 
            'estimated_price', 'totalPrice', 'total_price', 'maxPrice',
            'max_price', 'minPrice', 'min_price', 'value'
        ]
        
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
                result = self._extract_price_from_api_data(value)
                if result:
                    return result
        
        return None
    
    def _fill_questionnaire_with_best_values(self, page):
        """
        自动填写问卷，选择不影响价格的最佳值
        最佳值通常是：正常、良好、全新、无问题等
        """
        try:
            # 不影响价格的最佳关键词（优先级从高到低）
            best_keywords = [
                '正常进入桌面', '全新包装未拆封',  # 最高优先级
                '苹果个人账号可退出', '可退出', '已退出', '无账号',  # 账号相关（优先）
                '正常', '全新', '良好', '无问题', '全部正常', '完美', '无拆', '未拆',
                '无维修', '无拆修', '功能正常', '外观完美',
                '无瑕疵', '无划痕', '无损坏', '无故障',
            ]
            avoid_keywords = [
                '无法', '不能', '故障', '损坏', '维修', '拆修', 
                '无法回收', '无法开机', '无法进入桌面', '无法退出',
                '监管机', '有锁', '已锁定',
            ]
            
            # 等待问卷加载
            time.sleep(2)
            
            # 查找所有选项按钮/元素（排除标题和问题文本）
            option_selectors = [
                'button:not([class*="title"]):not([class*="question"])',
                '[role="button"]:not([class*="title"])',
                '.option:not([class*="title"])',
                '[class*="option"]:not([class*="title"]):not([class*="question"])',
                'label:not([class*="title"])',
                'div[class*="item"]:not([class*="title"])',
                '[class*="choice"]:not([class*="title"])',
            ]
            
            # 排除包含问题编号的文本
            import re
            question_number_pattern = re.compile(r'^\d+\.')
            
            clicked_count = 0
            max_clicks = 20  # 最多点击20次
            
            # 滚动页面确保所有元素可见
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            
            # 多次尝试，因为页面可能动态加载
            for attempt in range(3):
                for selector in option_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        for elem in elements:
                            if clicked_count >= max_clicks:
                                break
                                
                            text = elem.inner_text().strip()
                            if not text or len(text) < 2:
                                continue
                            
                            # 排除问题标题（包含编号的）
                            if question_number_pattern.match(text):
                                continue
                            
                            # 排除过长的文本（可能是问题描述）
                            if len(text) > 100:
                                continue
                            
                            # 检查是否包含最佳关键词
                            is_best = any(keyword in text for keyword in best_keywords)
                            is_avoid = any(keyword in text for keyword in avoid_keywords)
                            
                            # 如果是最佳选项且不是要避免的选项，点击它
                            if is_best and not is_avoid:
                                try:
                                    # 检查元素是否可见
                                    if not elem.is_visible():
                                        continue
                                    
                                    # 检查是否已经选中
                                    class_attr = elem.get_attribute('class') or ''
                                    aria_checked = elem.get_attribute('aria-checked')
                                    is_checked = (
                                        'active' in class_attr.lower() or 
                                        'selected' in class_attr.lower() or
                                        'checked' in class_attr.lower() or
                                        aria_checked == 'true'
                                    )
                                    
                                    if not is_checked:
                                        # 滚动到元素位置
                                        elem.scroll_into_view_if_needed()
                                        time.sleep(0.2)
                                        
                                        elem.click()
                                        clicked_count += 1
                                        logger.info(f"选择最佳选项: {text[:50]}")
                                        time.sleep(0.8)  # 等待选项响应和价格更新
                                        
                                        # 等待价格可能更新
                                        page.wait_for_timeout(500)
                                except Exception as e:
                                    logger.debug(f"点击选项失败: {text}, {e}")
                                    continue
                    except Exception as e:
                        logger.debug(f"查找选项失败: {selector}, {e}")
                        continue
                
                if clicked_count > 0:
                    break
                
                # 如果第一次没找到，等待一下再试
                if attempt < 2:
                    time.sleep(2)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1)
            
            logger.info(f"问卷填写完成，共选择 {clicked_count} 个选项")
            
        except Exception as e:
            logger.warning(f"自动填写问卷失败: {e}")
            # 失败不影响价格提取，继续执行
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """从页面文本中提取价格"""
        if not text:
            return None
        
        # 查找包含"元"或"¥"的价格
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*元',
            r'¥\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'价格[：:]\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'估价[：:]\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'回收价[：:]\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'至高[+＋]\s*¥\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',  # "至高+¥450"格式
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    price_value = float(match.replace(',', ''))
                    if 100 <= price_value <= 50000:
                        logger.info(f"从文本中提取到价格: {price_value} 元")
                        return price_value
                except:
                    continue
        
        return None
    
    def estimate(self, device_type: str, brand: str, model: str, storage: str, condition: str) -> Optional[float]:
        """
        通过设备信息估算价格（需要先找到对应的productId）
        注意：这个方法需要先通过搜索找到productId，然后调用get_price_by_product_id
        """
        # TODO: 实现通过设备信息搜索找到productId的逻辑
        # 目前先返回None，建议直接使用get_price_by_product_id
        logger.warning("estimate方法需要先实现搜索功能，建议使用get_price_by_product_id")
        return None


# 全局服务实例
aihuishou_scraper = AihuishouScraper()

