"""
测试支付宝签名，对比我们的签名原文和支付宝期望的格式
"""
import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.secondhand_app.alipay_client import AlipayClient

def test_signature():
    """测试签名格式"""
    print("=" * 70)
    print("支付宝签名格式测试")
    print("=" * 70)
    print()
    
    alipay = AlipayClient()
    
    # 模拟创建支付订单的参数
    biz_content = {
        'out_trade_no': 'normal_90',
        'product_code': 'FAST_INSTANT_TRADE_PAY',
        'total_amount': '195.00',
        'subject': '累计降价4.00元',
    }
    
    # 构建请求参数（与 create_trade 方法中的逻辑一致）
    params = {
        'app_id': alipay.app_id,
        'method': 'alipay.trade.page.pay',
        'charset': 'utf-8',
        'sign_type': 'RSA2',  # sign_type 需要参与签名
        'timestamp': '2025-12-06 21:39:56',
        'version': '1.0',
        'biz_content': json.dumps(biz_content, ensure_ascii=False, separators=(',', ':')),
        'notify_url': 'http://127.0.0.1:8000/api/payment/alipay/notify/',
        'return_url': 'http://localhost:5173/order/90',
    }
    
    # 生成签名（使用实际的方法）
    params['sign'] = alipay._sign(params)
    
    # 生成签名原文（使用实际的签名方法，但不包含sign）
    filtered_data = {}
    for k, v in params.items():
        if k == 'sign':  # 只排除 sign，sign_type 参与签名
            continue
        if v is None or v == '':
            continue
        filtered_data[k] = str(v)
    
    # 按字典序排序
    sorted_data = sorted(filtered_data.items())
    sign_str = '&'.join([f'{k}={v}' for k, v in sorted_data])
    
    print("我们的签名原文：")
    print(sign_str)
    print()
    print("支付宝期望的验签字符串（从错误信息中提取）：")
    print("app_id=9021000158624650&biz_content={\"out_trade_no\":\"normal_90\",\"product_code\":\"FAST_INSTANT_TRADE_PAY\",\"total_amount\":\"195.00\",\"subject\":\"累计降价4.00元\"}&charset=utf-8&method=alipay.trade.page.pay&notify_url=http://127.0.0.1:8000/api/payment/alipay/notify/&return_url=http://localhost:5173/order/90&sign_type=RSA2&timestamp=2025-12-06 21:39:56&version=1.0")
    print()
    
    # 对比
    expected_str = "app_id=9021000158624650&biz_content={\"out_trade_no\":\"normal_90\",\"product_code\":\"FAST_INSTANT_TRADE_PAY\",\"total_amount\":\"195.00\",\"subject\":\"累计降价4.00元\"}&charset=utf-8&method=alipay.trade.page.pay&notify_url=http://127.0.0.1:8000/api/payment/alipay/notify/&return_url=http://localhost:5173/order/90&sign_type=RSA2&timestamp=2025-12-06 21:39:56&version=1.0"
    
    # 注意：支付宝错误信息中的 &amp; 和 &quot; 是HTML编码，实际验签时应该使用原始字符
    expected_str = expected_str.replace('&amp;', '&').replace('&quot;', '"')
    
    print("对比结果：")
    if sign_str == expected_str:
        print("✓ 签名原文完全匹配！")
    else:
        print("❌ 签名原文不匹配")
        print()
        print("差异分析：")
        print(f"我们的长度: {len(sign_str)}")
        print(f"期望的长度: {len(expected_str)}")
        print()
        
        # 检查每个参数
        our_params = dict(sorted_data)
        expected_params = {}
        for item in expected_str.split('&'):
            if '=' in item:
                k, v = item.split('=', 1)
                expected_params[k] = v
        
        print("参数对比：")
        all_keys = set(our_params.keys()) | set(expected_params.keys())
        for key in sorted(all_keys):
            our_val = our_params.get(key, '')
            exp_val = expected_params.get(key, '')
            if our_val == exp_val:
                print(f"  ✓ {key}: 匹配")
            else:
                print(f"  ❌ {key}:")
                print(f"     我们的: {our_val[:100]}")
                print(f"     期望的: {exp_val[:100]}")
                if 'biz_content' in key:
                    print(f"     我们的JSON: {json.loads(our_val) if our_val.startswith('{') else 'N/A'}")
                    print(f"     期望的JSON: {json.loads(exp_val) if exp_val.startswith('{') else 'N/A'}")

if __name__ == '__main__':
    test_signature()

