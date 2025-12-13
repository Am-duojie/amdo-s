import os
import sys
from decimal import Decimal

# 保证可以找到 core.settings
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.utils import timezone
from app.secondhand_app.models import Order
from app.secondhand_app.alipay_client import AlipayClient
from app.admin_api.models import AdminAuditLog

def retry(order_id: int):
    o = Order.objects.select_related('product__seller__profile').get(id=order_id)
    alipay = AlipayClient()
    trade_no = getattr(o, 'alipay_trade_no', '')
    seller_profile = getattr(o.product.seller, 'profile', None)
    seller_login_id = seller_profile.alipay_login_id if seller_profile else ''
    seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
    seller_amount = Decimal(str(o.product.price))
    commission_amount = Decimal(str(o.total_price)) - seller_amount
    if commission_amount < 0:
        commission_amount = Decimal('0.00')
    out_request_no = f'admin_retry_settle_{o.id}_{int(timezone.now().timestamp())}'
    if seller_user_id:
        res = alipay.settle_order(
            trade_no=trade_no,
            out_request_no=out_request_no,
            splits=[{
                'trans_in': seller_user_id,
                'trans_in_type': 'userId',
                'amount': float(seller_amount),
                'desc': '易淘分账-卖家(管理员重试)'
            }]
        )
    else:
        res = alipay.settle_order(
            trade_no=trade_no,
            out_request_no=out_request_no,
            splits=[{
                'trans_in': seller_login_id,
                'trans_in_type': 'loginName',
                'amount': float(seller_amount),
                'desc': '易淘分账-卖家(管理员重试)'
            }]
        )
    if res.get('success'):
        o.settlement_status = 'settled'
        o.settled_at = timezone.now()
        o.settle_request_no = out_request_no
        o.seller_settle_amount = seller_amount
        o.platform_commission_amount = commission_amount
        o.save()
        AdminAuditLog.objects.create(actor=None, target_type='Order', target_id=o.id, action='settlement_retry', snapshot_json={'result': 'success'})
        print('RESULT', 'SUCCESS')
    else:
        o.settlement_status = 'failed'
        o.settle_request_no = out_request_no
        o.save()
        AdminAuditLog.objects.create(actor=None, target_type='Order', target_id=o.id, action='settlement_retry', snapshot_json={'result': 'failed', 'code': res.get('code'), 'msg': res.get('msg'), 'sub_code': res.get('sub_code'), 'sub_msg': res.get('sub_msg')})
        print('RESULT', 'FAIL', res)
        try:
            from django.conf import settings
            if getattr(settings, 'SETTLEMENT_FALLBACK_TO_TRANSFER', False):
                out_biz_no = f'admin_retry_settle_transfer_{o.id}_{int(timezone.now().timestamp())}'
                t = alipay.transfer_to_account(
                    out_biz_no=out_biz_no,
                    payee_account=(seller_login_id or seller_user_id),
                    amount=float(seller_amount),
                    payee_real_name=(seller_profile.alipay_real_name if seller_profile else None),
                    remark='易淘分账-管理员转账代结算'
                )
                if t.get('success'):
                    o.settlement_status = 'settled'
                    o.settled_at = timezone.now()
                    o.seller_settle_amount = seller_amount
                    o.platform_commission_amount = commission_amount
                    o.save()
                    AdminAuditLog.objects.create(actor=None, target_type='Order', target_id=o.id, action='settlement_retry_transfer', snapshot_json={'result': 'success'})
                    print('RESULT', 'SUCCESS', 'TRANSFER')
        print('ORDER', o.id, o.status, o.settlement_status)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: retry_settlement.py <order_id>')
        sys.exit(1)
    retry(int(sys.argv[1]))
