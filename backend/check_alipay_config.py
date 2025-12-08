"""
检查支付宝配置和密钥匹配性
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from app.secondhand_app.alipay_client import AlipayClient
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

def check_config():
    """检查支付宝配置"""
    print("=" * 70)
    print("支付宝配置检查")
    print("=" * 70)
    print()
    
    alipay = AlipayClient()
    
    # 1. 检查基本配置
    print("1. 基本配置检查")
    print("-" * 70)
    print(f"APPID: {alipay.app_id}")
    print(f"网关地址: {alipay.gateway_url}")
    print()
    
    # 2. 验证配置
    is_valid, error_msg = alipay.validate_config()
    if not is_valid:
        print(f"❌ 配置验证失败: {error_msg}")
        return False
    else:
        print("✓ 配置验证通过")
    print()
    
    # 3. 检查密钥匹配性
    print("2. 密钥匹配性检查")
    print("-" * 70)
    
    try:
        # 格式化私钥
        private_key_str = alipay._format_private_key(alipay.app_private_key)
        private_key = RSA.import_key(private_key_str)
        print(f"✓ 应用私钥加载成功（{private_key.size_in_bits()}位）")
        
        # 从私钥生成公钥
        public_key_from_private = private_key.publickey()
        public_key_pem = public_key_from_private.export_key(format='PEM').decode('utf-8')
        
        # 格式化支付宝公钥
        alipay_public_key_str = alipay._format_public_key(alipay.alipay_public_key)
        alipay_public_key = RSA.import_key(alipay_public_key_str)
        print(f"✓ 支付宝公钥加载成功（{alipay_public_key.size_in_bits()}位）")
        print()
        
        # 4. 测试签名和验签
        print("3. 签名和验签测试")
        print("-" * 70)
        
        # 测试数据
        test_data = {
            'app_id': alipay.app_id,
            'method': 'alipay.trade.page.pay',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': '2025-12-06 21:33:43',
            'version': '1.0',
            'biz_content': '{"out_trade_no":"test_123","product_code":"FAST_INSTANT_TRADE_PAY","total_amount":"100.00","subject":"测试商品"}',
        }
        
        # 生成签名
        sign = alipay._sign(test_data)
        print(f"✓ 签名生成成功")
        print(f"  签名结果（前50字符）: {sign[:50]}...")
        print()
        
        # 验证签名（使用应用公钥）
        sign_str = '&'.join([f'{k}={v}' for k, v in sorted(test_data.items())])
        hash_obj = SHA256.new(sign_str.encode('utf-8'))
        signature = base64.b64decode(sign.encode('utf-8'))
        verifier = pkcs1_15.new(public_key_from_private)
        try:
            verifier.verify(hash_obj, signature)
            print("✓ 使用应用公钥验证签名成功（说明私钥和公钥匹配）")
        except Exception as e:
            print(f"❌ 使用应用公钥验证签名失败: {e}")
            print("   这说明应用私钥和公钥不匹配！")
            print()
            print("解决方案：")
            print("1. 检查应用私钥是否正确")
            print("2. 从应用私钥生成应用公钥：")
            print("   " + public_key_pem.replace('\n', '\n   '))
            print("3. 将应用公钥上传到支付宝开放平台")
            print("4. 从支付宝平台获取支付宝公钥并配置")
            return False
        print()
        
        # 5. 显示应用公钥（用于上传到支付宝）
        print("4. 应用公钥（需要上传到支付宝开放平台）")
        print("-" * 70)
        print(public_key_pem)
        print()
        print("上传步骤：")
        print("1. 登录支付宝开放平台：https://open.alipay.com/")
        print("2. 进入应用管理 -> 选择您的应用")
        print("3. 点击'接口加签方式' -> '设置'")
        print("4. 选择'公钥'模式")
        print("5. 将上面的应用公钥（包含头尾标记）复制粘贴到'应用公钥'输入框")
        print("6. 点击'保存'")
        print("7. 保存后，支付宝会返回'支付宝公钥'，请复制并更新到 settings.py 中的 ALIPAY_PUBLIC_KEY")
        print()
        
        print("=" * 70)
        print("✓ 所有检查通过！")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ 检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_config()
    sys.exit(0 if success else 1)










