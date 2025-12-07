"""
测试打款功能
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.secondhand_app.models import RecycleOrder, Wallet, WalletTransaction, User
from decimal import Decimal

# 查找一个已完成的订单
order = RecycleOrder.objects.filter(
    status__in=['completed', 'inspected'],
    final_price__isnull=False
).first()

if not order:
    print("❌ 没有找到符合条件的订单（已完成或已检测，且有最终价格）")
    exit(1)

print(f"✅ 找到订单: #{order.id}")
print(f"   用户: {order.user.username}")
print(f"   状态: {order.status}")
print(f"   最终价格: ¥{order.final_price}")
print(f"   加价: ¥{order.bonus}")
print(f"   打款状态: {order.payment_status}")

# 检查用户钱包
wallet, created = Wallet.objects.get_or_create(user=order.user)
print(f"\n💰 钱包信息:")
print(f"   钱包已存在: {not created}")
print(f"   当前余额: ¥{wallet.balance}")

# 计算打款总额
total_amount = Decimal(str(order.final_price)) + Decimal(str(order.bonus or 0))
print(f"\n💵 打款信息:")
print(f"   打款总额: ¥{total_amount}")

# 测试 add_balance 方法
print(f"\n🧪 测试 add_balance 方法...")
try:
    old_balance = wallet.balance
    wallet.add_balance(
        amount=float(total_amount),
        transaction_type='income',
        related_order=order,
        note=f'测试打款 - 回收订单#{order.id}'
    )
    wallet.refresh_from_db()
    print(f"   ✅ 成功!")
    print(f"   原余额: ¥{old_balance}")
    print(f"   新余额: ¥{wallet.balance}")
    print(f"   增加金额: ¥{wallet.balance - old_balance}")
    
    # 检查交易记录
    transaction = WalletTransaction.objects.filter(
        wallet=wallet,
        related_order=order
    ).order_by('-created_at').first()
    if transaction:
        print(f"\n📝 交易记录:")
        print(f"   交易类型: {transaction.get_transaction_type_display()}")
        print(f"   金额: ¥{transaction.amount}")
        print(f"   交易后余额: ¥{transaction.balance_after}")
        print(f"   备注: {transaction.note}")
    
except Exception as e:
    print(f"   ❌ 失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n✅ 测试完成")






