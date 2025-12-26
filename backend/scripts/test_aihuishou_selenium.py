"""
使用Selenium自动化浏览器获取爱回收价格
需要先安装: pip install selenium
并下载ChromeDriver: https://chromedriver.chromium.org/
"""
import time
import sys
import os

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_with_selenium():
    """使用Selenium获取价格"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("错误: 未安装selenium，请运行: pip install selenium")
        return None
    
    url = "https://m.aihuishou.com/n/#/inquiry?productId=225361"
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式（可选）
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15')
    
    driver = None
    try:
        print(f"正在启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print(f"正在访问: {url}")
        driver.get(url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)
        
        # 尝试多种选择器查找价格
        price_selectors = [
            "[class*='price']",
            "[class*='Price']",
            "[id*='price']",
            "[id*='Price']",
            ".price",
            ".estimated-price",
            "[data-price]",
            "span.price",
            "div.price",
        ]
        
        price = None
        for selector in price_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if text and ('元' in text or '¥' in text or any(c.isdigit() for c in text)):
                        print(f"找到可能的价格元素: {text}")
                        # 提取数字
                        import re
                        price_match = re.search(r'[\d,]+', text.replace(',', ''))
                        if price_match:
                            price_value = float(price_match.group().replace(',', ''))
                            if 100 <= price_value <= 50000:
                                price = price_value
                                print(f"[成功] 提取到价格: {price} 元")
                                return price
            except Exception as e:
                continue
        
        # 如果没找到，打印页面源码的一部分用于调试
        print("\n页面标题:", driver.title)
        print("\n页面源码片段（前1000字符）:")
        print(driver.page_source[:1000])
        
        return None
        
    except Exception as e:
        print(f"错误: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭")


def _fill_questionnaire_best_values(page):
    """自动填写问卷，选择不影响价格的最佳值"""
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
        
        # 排除包含问题编号的文本（如"1.使用情况"）
        import re
        question_number_pattern = re.compile(r'^\d+\.')
        
        # 查找所有选项元素（多种选择器）
        option_selectors = [
            'button',
            '[role="button"]',
            '.option',
            '[class*="option"]',
            '[class*="Option"]',
            'label',
            'div[class*="item"]',
            '[class*="choice"]',
            '[class*="Choice"]',
        ]
        
        clicked_count = 0
        max_clicks = 20  # 最多点击20次，避免无限循环
        
        # 滚动页面确保所有元素可见
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        
        # 多次尝试，因为页面可能动态加载
        # 每次选择后，页面可能会显示新的问题，所以需要多次循环
        for attempt in range(5):  # 增加尝试次数
            previous_count = clicked_count
            
            for selector in option_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for elem in elements:
                        if clicked_count >= max_clicks:
                            break
                            
                        text = elem.inner_text().strip()
                        if not text or len(text) < 2:
                            continue
                        
                        # 排除问题标题（包含编号的，如"1.使用情况"）
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
                                    time.sleep(0.3)
                                    
                                    elem.click()
                                    clicked_count += 1
                                    print(f"  [{clicked_count}] 选择最佳选项: {text[:50]}")
                                    
                                    # 等待选项响应和页面更新（可能显示新问题）
                                    time.sleep(1.5)  # 增加等待时间
                                    
                                    # 滚动到底部，确保新问题可见
                                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                    time.sleep(0.5)
                            except Exception as e:
                                continue
                except:
                    continue
            
            # 如果这一轮没有新的选择，说明已经填完所有问题
            if clicked_count == previous_count:
                if clicked_count > 0:
                    break
                # 如果还没选择任何选项，继续尝试
                if attempt < 4:
                    time.sleep(2)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1)
                    page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(1)
        
        if clicked_count > 0:
            print(f"  已选择 {clicked_count} 个最佳选项")
        else:
            print("  未找到最佳选项，跳过自动填写")
    except Exception as e:
        print(f"  自动填写问卷失败: {e}")


def test_with_playwright(headless=False):
    """使用Playwright获取价格（更现代的选择）"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("错误: 未安装playwright，请运行: pip install playwright")
        print("然后运行: playwright install chromium")
        return None
    
    url = "https://m.aihuishou.com/n/#/inquiry?productId=225361"
    
    with sync_playwright() as p:
        try:
            print("正在启动浏览器...")
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                viewport={'width': 375, 'height': 667},  # 移动端尺寸
            )
            page = context.new_page()
            
            # 监听网络请求，查找API调用
            api_calls = []
            def handle_response(response):
                url = response.url
                if 'api' in url.lower() or 'price' in url.lower() or 'inquiry' in url.lower():
                    api_calls.append(url)
                    print(f"发现API请求: {url}")
            page.on("response", handle_response)
            
            print(f"正在访问: {url}")
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 等待页面加载和JavaScript执行
            print("等待页面加载...")
            time.sleep(5)  # 等待初始加载
            
            # 自动填写问卷（选择不影响价格的最佳值）
            print("自动填写问卷（选择最佳值）...")
            _fill_questionnaire_best_values(page)
            
            # 等待价格更新
            print("等待价格更新...")
            time.sleep(3)
            
            # 等待特定元素出现（尝试多种可能的选择器）
            print("等待价格元素出现...")
            try:
                # 尝试等待常见的价格元素
                page.wait_for_selector("text=/价格|元|¥|估价/", timeout=10000)
            except:
                pass
            
            # 获取页面所有文本内容用于调试
            all_text = page.inner_text('body')
            print(f"\n页面文本内容预览（前500字符）:")
            print(all_text[:500])
            
            # 尝试多种价格选择器
            price_selectors = [
                # 常见的选择器
                "[class*='price']",
                "[class*='Price']",
                "[class*='PRICE']",
                "[id*='price']",
                "[id*='Price']",
                ".price",
                ".estimated-price",
                ".price-value",
                ".price-text",
                "[data-price]",
                "[data-amount]",
                # 更具体的选择器
                "span.price",
                "div.price",
                "p.price",
                ".price-num",
                ".price-number",
                # 可能的Vue组件类名
                "[class*='Price']",
                "[class*='Amount']",
                "[class*='Money']",
            ]
            
            found_elements = []
            for selector in price_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for elem in elements:
                        text = elem.inner_text().strip()
                        if text:
                            found_elements.append((selector, text))
                            print(f"找到元素 [{selector}]: {text}")
                            
                            # 检查是否包含价格相关关键词
                            if any(keyword in text for keyword in ['元', '¥', '价格', '估价', '回收价']):
                                import re
                                # 提取数字（支持小数点）
                                price_match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
                                if price_match:
                                    price_value = float(price_match.group().replace(',', ''))
                                    if 100 <= price_value <= 50000:
                                        print(f"[成功] 提取到价格: {price_value} 元 (选择器: {selector})")
                                        return price_value
                except Exception as e:
                    continue
            
            # 如果没找到，尝试从所有文本中提取价格
            print("\n尝试从页面文本中提取价格...")
            import re
            # 查找包含"元"或"¥"的数字
            price_patterns = [
                r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*元',
                r'¥\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                r'价格[：:]\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                r'估价[：:]\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                r'回收价[：:]\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, all_text)
                for match in matches:
                    try:
                        price_value = float(match.replace(',', ''))
                        if 100 <= price_value <= 50000:
                            print(f"[成功] 从文本中提取到价格: {price_value} 元")
                            return price_value
                    except:
                        continue
            
            # 打印找到的所有元素用于调试
            if found_elements:
                print(f"\n找到的所有元素（共{len(found_elements)}个）:")
                for selector, text in found_elements[:20]:  # 只显示前20个
                    print(f"  [{selector}]: {text[:100]}")
            
            # 打印页面内容用于调试
            print("\n页面标题:", page.title())
            print("\n页面HTML片段（查找包含'price'的部分）:")
            html_content = page.content()
            # 查找包含price的部分
            import re
            price_sections = re.findall(r'<[^>]*(?:price|Price|PRICE)[^>]*>.*?</[^>]+>', html_content, re.IGNORECASE | re.DOTALL)
            for section in price_sections[:5]:  # 只显示前5个
                print(section[:200])
            
            # 打印发现的API调用并尝试获取价格
            if api_calls:
                print(f"\n发现的API调用（共{len(api_calls)}个）:")
                for api_url in api_calls[:10]:  # 只显示前10个
                    print(f"  {api_url}")
                    # 特别关注包含inquiry或price的API
                    if 'inquiry' in api_url.lower() or 'price' in api_url.lower():
                        try:
                            # 使用page.request获取响应
                            response = page.request.get(api_url)
                            if response.ok:
                                try:
                                    data = response.json()
                                    print(f"    JSON响应预览: {str(data)[:500]}")
                                    # 尝试从响应中提取价格
                                    price = extract_price_from_data(data)
                                    if price:
                                        print(f"[成功] 从API响应提取到价格: {price} 元")
                                        browser.close()
                                        return price
                                except Exception as e:
                                    print(f"    解析JSON失败: {e}")
                        except Exception as e:
                            print(f"    请求失败: {e}")
            
            browser.close()
            return None
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    import sys
    
    print("="*60)
    print("爱回收价格获取测试 - Selenium/Playwright版本")
    print("="*60)
    
    # 检查是否使用headless模式
    headless = '--headless' in sys.argv or '-h' in sys.argv
    
    # 优先尝试Playwright（更现代）
    print("\n[方法1] 尝试使用Playwright...")
    if not headless:
        print("提示: 使用 --headless 参数可以无头模式运行")
    price = test_with_playwright(headless=headless)
    
    if not price:
        # 如果Playwright失败，尝试Selenium
        print("\n[方法2] 尝试使用Selenium...")
        price = test_with_selenium()
    
    if price:
        print(f"\n[最终结果] 成功获取价格: {price} 元")
    else:
        print("\n[最终结果] 未能获取价格")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 确认ChromeDriver或Playwright已正确安装")
        print("3. 尝试不使用headless模式运行，查看实际页面: python scripts/test_aihuishou_selenium.py")
        print("4. 使用浏览器开发者工具分析网络请求，找到API端点")
        print("5. 检查页面是否需要登录或其他认证")


if __name__ == "__main__":
    main()

