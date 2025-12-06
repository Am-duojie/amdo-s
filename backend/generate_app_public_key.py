"""
生成应用公钥工具
从应用私钥生成应用公钥，用于上传到支付宝开放平台
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

def generate_public_key():
    """从应用私钥生成应用公钥"""
    print('=' * 70)
    print('生成应用公钥（用于上传到支付宝开放平台）')
    print('=' * 70)
    print()
    
    try:
        alipay = AlipaySandboxClient()
        
        # 获取并格式化私钥
        private_key_str = alipay._format_private_key(alipay.app_private_key)
        if not private_key_str:
            print('❌ 无法格式化应用私钥')
            return False
        
        # 加载私钥
        private_key = RSA.import_key(private_key_str)
        print(f'✓ 应用私钥加载成功（{private_key.size_in_bits()}位）')
        print()
        
        # 从私钥生成公钥
        public_key = private_key.publickey()
        
        # 导出公钥（PEM格式）
        public_key_pem = public_key.export_key(format='PEM').decode('utf-8')
        
        print('=' * 70)
        print('应用公钥（请复制以下内容上传到支付宝开放平台）')
        print('=' * 70)
        print()
        print(public_key_pem)
        print()
        print('=' * 70)
        print('上传步骤')
        print('=' * 70)
        print()
        print('1. 登录支付宝开放平台沙箱控制台：')
        print('   https://openhome.alipay.com/develop/sandbox/app')
        print()
        print('2. 选择您的应用（APPID: {})'.format(alipay.app_id))
        print()
        print('3. 点击"接口加签方式" -> "设置"')
        print()
        print('4. 选择"公钥"模式（沙箱环境仅支持公钥模式）')
        print()
        print('5. 将上面显示的公钥内容（包含头尾标记）复制到"应用公钥"输入框')
        print()
        print('6. 点击"保存"')
        print()
        print('7. 保存后，支付宝会返回"支付宝公钥"，请复制并更新到 settings.py 中的')
        print('   ALIPAY_SANDBOX_PUBLIC_KEY')
        print()
        print('=' * 70)
        print('注意事项')
        print('=' * 70)
        print()
        print('⚠️  确保上传的公钥与代码中使用的私钥匹配')
        print('⚠️  上传公钥后，需要等待几分钟才能生效')
        print('⚠️  如果上传的公钥与私钥不匹配，会导致签名验证失败')
        print()
        
        # 同时保存到文件
        output_file = 'app_public_key.pem'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(public_key_pem)
        print(f'✓ 公钥已保存到文件: {output_file}')
        print()
        
        return True
        
    except Exception as e:
        print(f'❌ 生成公钥失败: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = generate_public_key()
    sys.exit(0 if success else 1)


