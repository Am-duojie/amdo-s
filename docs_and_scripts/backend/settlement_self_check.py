import os
import sys
from decimal import Decimal

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.utils import timezone
from app.secondhand_app.models import Order
from app.secondhand_app.alipay_client import AlipayClient

def check_and_fix(order_id: int):
    o = Order.objects.select_related('product__seller__profile').get(id=order_id)
    alipay = AlipayClient()
    trade_no = getattr(o, 'alipay_trade_no', '')
    seller_profile = getattr(o.product.seller, 'profile', None)
    seller_login_id = seller_profile.alipay_login_id if seller_profile else ''
    seller_amount = Decimal(str(o.product.price))
    commission_amount = Decimal(str(o.total_price)) - seller_amount
    if commission_amount < 0:
        commission_amount = Decimal('0.00')
    if not trade_no:
        q = alipay.query_trade(f'normal_{o.id}')
        if q.get('success'):
            trade_no = q.get('trade_no', '')
    print('TRADE_NO', trade_no)
    if not trade_no or not seller_login_id:
        print('SKIP', 'trade_no or seller_login_id missing')
        return
    out_request_no = f'self_check_settle_{o.id}_{int(timezone.now().timestamp())}'
    res = alipay.settle_order(
        trade_no=trade_no,
        out_request_no=out_request_no,
        splits=[{
            'trans_in': seller_login_id,
            'trans_in_type': 'ALIPAY_LOGON_ID',
            'amount': float(seller_amount),
            'desc': '易淘分账-自检'
        }]
    )
    print('SETTLE', res)
    if not res.get('success'):
        from django.conf import settings
        if getattr(settings, 'SETTLEMENT_FALLBACK_TO_TRANSFER', False):
            out_biz_no = f'self_check_transfer_{o.id}_{int(timezone.now().timestamp())}'
            t = alipay.transfer_to_account(
                out_biz_no=out_biz_no,
                payee_account=seller_login_id,
                amount=float(seller_amount),
                payee_real_name=(seller_profile.alipay_real_name if seller_profile else None),
                remark='易淘分账-自检转账代结算'
            )
            print('TRANSFER', t)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: settlement_self_check.py <order_id>')
        sys.exit(1)
    check_and_fix(int(sys.argv[1]))

