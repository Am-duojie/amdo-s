"""
验证截图中的密钥与配置文件中的密钥是否匹配
"""
import os
import django
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from app.secondhand_app.alipay_sandbox import AlipaySandboxClient
from Crypto.PublicKey import RSA

def verify_keys():
    """验证密钥匹配"""
    print('=' * 70)
    print('验证密钥匹配')
    print('=' * 70)
    print()
    
    alipay = AlipaySandboxClient()
    
    # 1. 从私钥生成应用公钥
    print('1. 从应用私钥生成应用公钥...')
    try:
        private_key_str = alipay._format_private_key(alipay.app_private_key)
        private_key = RSA.import_key(private_key_str)
        public_key_from_private = private_key.publickey()
        public_key_pem = public_key_from_private.export_key(format='PEM').decode('utf-8')
        
        # 提取Base64部分
        lines = [line.strip() for line in public_key_pem.split('\n') 
                 if line.strip() and not line.strip().startswith('-----')]
        public_key_base64 = ''.join(lines)
        
        print(f'   ✓ 应用公钥（从私钥生成）: {public_key_base64[:50]}...')
        print()
    except Exception as e:
        print(f'   ❌ 生成应用公钥失败: {str(e)}')
        return False
    
    # 2. 从截图描述中提取的应用公钥（需要用户确认）
    print('2. 请确认支付宝控制台显示的应用公钥:')
    print('   从截图中看到的应用公钥应该是:')
    print(f'   {public_key_base64[:50]}...')
    print()
    print('   ⚠️  请确认控制台显示的应用公钥是否与上面显示的公钥匹配')
    print('   如果不匹配，说明应用公钥未正确上传到支付宝平台')
    print()
    
    # 3. 检查配置文件中的支付宝公钥
    print('3. 配置文件中的支付宝公钥:')
    alipay_public_key = settings.ALIPAY_SANDBOX_PUBLIC_KEY.replace(' ', '').replace('\n', '')
    print(f'   {alipay_public_key[:50]}...')
    print()
    
    # 4. 从截图描述中提取的支付宝公钥（需要用户确认）
    print('4. 请确认支付宝控制台显示的支付宝公钥:')
    print('   从截图中看到的支付宝公钥应该是:')
    print(f'   {alipay_public_key[:50]}...')
    print()
    print('   ⚠️  请确认控制台显示的支付宝公钥是否与配置文件中的公钥匹配')
    print('   如果不匹配，需要更新配置文件中的 ALIPAY_SANDBOX_PUBLIC_KEY')
    print()
    
    # 5. 验证密钥对
    print('5. 验证密钥对匹配...')
    try:
        # 验证应用私钥和应用公钥匹配
        test_data = b'Hello, Alipay!'
        from Crypto.Signature import pkcs1_15
        from Crypto.Hash import SHA256
        import base64
        
        hash_obj = SHA256.new(test_data)
        signer = pkcs1_15.new(private_key)
        signature = signer.sign(hash_obj)
        
        verifier = pkcs1_15.new(public_key_from_private)
        verifier.verify(hash_obj, signature)
        print('   ✓ 应用私钥和应用公钥匹配')
    except Exception as e:
        print(f'   ❌ 应用私钥和应用公钥不匹配: {str(e)}')
        return False
    
    print()
    print('=' * 70)
    print('重要提示')
    print('=' * 70)
    print()
    print('如果签名验证仍然失败，请检查:')
    print('1. 支付宝控制台显示的应用公钥是否与上面显示的公钥匹配')
    print('   - 如果不匹配，需要重新上传应用公钥到支付宝平台')
    print('   - 上传步骤：接口加签方式 -> 设置 -> 粘贴应用公钥 -> 保存')
    print()
    print('2. 支付宝控制台显示的支付宝公钥是否与配置文件中的公钥匹配')
    print('   - 如果不匹配，需要更新 settings.py 中的 ALIPAY_SANDBOX_PUBLIC_KEY')
    print()
    print('3. 上传应用公钥后，需要等待 2-5 分钟才能生效')
    print()
    print('4. 确保使用的是正确的 APPID: 9021000158624650')
    print()
    print('=' * 70)
    
    return True

if __name__ == '__main__':
    verify_keys()

