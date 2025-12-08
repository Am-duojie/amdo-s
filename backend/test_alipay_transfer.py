"""
测试支付宝商家转账功能
"""
import os
import sys
import django
import time

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.secondhand_app.alipay_client import AlipayClient

def test_transfer():
    """测试转账功能"""
    print("=" * 70)
    print("支付宝商家转账功能测试")
    print("=" * 70)
    print()
    
    alipay = AlipayClient()
    
    # 验证配置
    is_valid, error_msg = alipay.validate_config()
    if not is_valid:
        print(f"❌ 配置验证失败: {error_msg}")
        print()
        print("请检查 settings.py 中的支付宝配置")
        return False
    
    print("✓ 配置验证通过")
    print()
    
    # 测试参数（请根据实际情况修改）
    print("=" * 70)
    print("转账测试参数")
    print("=" * 70)
    print()
    print("⚠️  注意：这是真实转账测试，会实际转账到指定账户")
    print()
    
    # 从用户输入获取测试参数
    payee_account = input("请输入收款方支付宝账号（手机号或邮箱）: ").strip()
    if not payee_account:
        print("❌ 收款账户不能为空")
        return False
    
    payee_real_name = input("请输入收款方真实姓名（可选，建议填写）: ").strip()
    
    amount_str = input("请输入转账金额（元）: ").strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("❌ 转账金额必须大于0")
            return False
    except ValueError:
        print("❌ 转账金额格式错误")
        return False
    
    remark = input("请输入转账备注（可选）: ").strip()
    
    # 生成商户订单号
    out_biz_no = f'test_{int(time.time())}'
    
    print()
    print("=" * 70)
    print("转账信息确认")
    print("=" * 70)
    print(f"商户订单号: {out_biz_no}")
    print(f"收款账户: {payee_account}")
    if payee_real_name:
        print(f"收款方姓名: {payee_real_name}")
    print(f"转账金额: {amount:.2f} 元")
    if remark:
        print(f"转账备注: {remark}")
    print()
    
    confirm = input("确认执行转账？(yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消转账")
        return False
    
    print()
    print("正在执行转账...")
    print()
    
    # 调用转账接口
    result = alipay.transfer_to_account(
        out_biz_no=out_biz_no,
        payee_account=payee_account,
        amount=amount,
        payee_real_name=payee_real_name if payee_real_name else None,
        remark=remark if remark else ''
    )
    
    print("=" * 70)
    print("转账结果")
    print("=" * 70)
    print()
    
    if result.get('success'):
        print("✓ 转账成功！")
        print()
        print("转账详情：")
        print(f"  支付宝订单号: {result.get('order_id')}")
        print(f"  资金流水号: {result.get('pay_fund_order_id')}")
        print(f"  商户订单号: {result.get('out_biz_no')}")
        print(f"  转账状态: {result.get('status')}")
        if result.get('trans_date'):
            print(f"  转账日期: {result.get('trans_date')}")
        print()
        print("✓ 转账已完成，请检查收款方支付宝账户")
        return True
    else:
        print("❌ 转账失败")
        print()
        print("错误详情：")
        print(f"  错误码: {result.get('code')}")
        print(f"  错误信息: {result.get('msg')}")
        if result.get('sub_code'):
            print(f"  子错误码: {result.get('sub_code')}")
        if result.get('sub_msg'):
            print(f"  子错误信息: {result.get('sub_msg')}")
        print()
        print("常见错误解决方案：")
        print("  - PAYEE_NOT_EXIST: 收款账户不存在，请检查账号是否正确")
        print("  - PAYEE_USER_INFO_ERROR: 收款方信息错误，请检查账号和姓名是否匹配")
        print("  - INSUFFICIENT_BALANCE: 账户余额不足，请检查企业支付宝账户余额")
        print("  - PERMISSION_DENIED: 权限不足，请检查是否已开通商家转账功能")
        return False

if __name__ == '__main__':
    try:
        success = test_transfer()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n已取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)










