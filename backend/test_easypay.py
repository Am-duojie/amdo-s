"""
易支付接口测试脚本
使用方法：
1. 确保已激活虚拟环境
2. cd E:\桌面\毕业设计\backend
3. python test_easypay.py
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.secondhand_app.easypay import EasyPayClient


def test_config():
    """测试配置"""
    print("\n========== 测试易支付配置 ==========")
    
    easypay = EasyPayClient()
    
    print(f"商户ID: {easypay.pid}")
    print(f"商户密钥: {easypay.key[:10]}..." if easypay.key else "未配置")
    print(f"提交接口: {easypay.submit_url}")
    print(f"MAPI接口: {easypay.mapi_url}")
    print(f"API接口: {easypay.api_url}")
    print(f"异步通知地址: {easypay.notify_url}")
    print(f"同步跳转地址: {easypay.return_url}")
    
    is_valid, msg = easypay.validate_config()
    if is_valid:
        print("\n✅ 配置验证通过")
    else:
        print(f"\n❌ 配置错误: {msg}")
    
    return is_valid


def test_sign():
    """测试签名生成"""
    print("\n========== 测试签名生成 ==========")
    
    easypay = EasyPayClient()
    
    params = {
        'pid': easypay.pid,
        'type': 'alipay',
        'out_trade_no': '12345',
        'notify_url': 'http://example.com/notify',
        'return_url': 'http://example.com/return',
        'name': '测试商品',
        'money': '0.01',
        'param': 'test',
        'sign_type': 'MD5',
    }
    
    sign = easypay.generate_sign(params)
    
    print(f"测试参数: {params}")
    print(f"生成签名: {sign}")
    
    return sign


def test_create_payment():
    """测试创建支付订单"""
    print("\n========== 测试创建支付订单 ==========")
    
    easypay = EasyPayClient()
    
    # 测试API支付
    result = easypay.create_payment_api(
        order_id=99999,
        order_name='测试商品',
        amount=0.01,
        client_ip='127.0.0.1',
        pay_type='alipay'
    )
    
    print("\n--- API支付结果 ---")
    print(f"返回结果: {result}")
    
    if result.get('code') == 1:
        print("✅ 支付订单创建成功")
        print(f"支付二维码: {result.get('qrcode')}")
        print(f"支付页面: {result.get('payurl')}")
    else:
        print(f"❌ 创建失败: {result.get('msg')}")
    
    return result


def test_query_order():
    """测试查询订单"""
    print("\n========== 测试查询订单 ==========")
    
    order_id = input("请输入要查询的订单号（直接回车跳过）: ").strip()
    
    if not order_id:
        print("跳过查询测试")
        return
    
    easypay = EasyPayClient()
    result = easypay.query_order(order_id)
    
    print(f"\n查询结果: {result}")
    
    if result.get('code') == 1:
        status = result.get('status')
        if status == 1:
            print("✅ 订单已支付")
        else:
            print("⏳ 订单未支付")
    else:
        print(f"❌ 查询失败: {result.get('msg')}")


def main():
    """主测试函数"""
    print("=" * 50)
    print("易支付接口测试")
    print("=" * 50)
    
    # 1. 测试配置
    if not test_config():
        print("\n请先在 settings.py 中配置 EASYPAY_PID 和 EASYPAY_KEY")
        return
    
    # 2. 测试签名
    test_sign()
    
    # 3. 测试创建支付
    print("\n是否测试创建支付订单？（会调用真实接口）")
    choice = input("输入 y 继续，其他键跳过: ").strip().lower()
    
    if choice == 'y':
        test_create_payment()
    
    # 4. 测试查询订单
    test_query_order()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()



















