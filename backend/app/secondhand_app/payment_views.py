"""
易支付相关视图
支付平台：https://pay.myzfw.com/
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import Order
from .easypay import EasyPayClient
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    创建支付订单（API接口）
    返回支付二维码
    """
    order_id = request.data.get('order_id')
    pay_type = request.data.get('pay_type', 'alipay')  # alipay 或 wxpay
    
    if not order_id:
        return Response({'error': '订单ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 检查订单权限
    if order.buyer != request.user:
        return Response({'error': '无权限操作此订单'}, status=status.HTTP_403_FORBIDDEN)
    
    # 检查订单状态
    if order.status != 'pending':
        return Response({'error': f'订单状态不正确，当前状态：{order.get_status_display()}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 创建支付客户端
    easypay = EasyPayClient()
    
    # 验证配置
    is_valid, error_msg = easypay.validate_config()
    if not is_valid:
        logger.error(f'支付配置错误: {error_msg}')
        return Response({
            'success': False,
            'error': error_msg
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # 获取客户端IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    # 调用易支付API
    result = easypay.create_payment_api(
        order_id=order.id,
        order_name=order.product.title[:50],  # 商品名称限制50字符
        amount=order.total_price,
        client_ip=client_ip,
        pay_type=pay_type,
        return_url=f'http://localhost:5173/order/{order.id}',
        param=f'order_{order.id}'
    )
    
    # 处理响应
    if result.get('code') == 1:
        logger.info(f'支付订单创建成功: order_id={order.id}, trade_no={result.get("trade_no")}')
        return Response({
            'success': True,
            'payment_url': result.get('payurl'),
            'qrcode': result.get('qrcode'),
            'urlscheme': result.get('urlscheme'),
            'trade_no': result.get('trade_no'),
        })
    else:
        error_msg = result.get('msg', '创建支付失败')
        logger.error(f'支付订单创建失败: {error_msg}')
        return Response({
            'success': False,
            'error': error_msg
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_url(request):
    """
    创建支付URL（页面跳转支付）
    """
    order_id = request.data.get('order_id')
    pay_type = request.data.get('pay_type', 'alipay')
    
    if not order_id:
        return Response({'error': '订单ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 检查权限
    if order.buyer != request.user:
        return Response({'error': '无权限操作此订单'}, status=status.HTTP_403_FORBIDDEN)
    
    if order.status != 'pending':
        return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 创建支付
    easypay = EasyPayClient()
    
    is_valid, error_msg = easypay.validate_config()
    if not is_valid:
        return Response({
            'success': False,
            'error': error_msg
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    payment_url = easypay.create_payment(
        order_id=order.id,
        order_name=order.product.title[:50],
        amount=order.total_price,
        pay_type=pay_type,
        return_url=f'http://localhost:5173/order/{order.id}',
        param=f'order_{order.id}'
    )
    
    logger.info(f'生成支付URL: {payment_url}')
    
    return Response({
        'success': True,
        'payment_url': payment_url
    })


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def payment_notify(request):
    """
    支付异步通知回调
    易支付会在支付成功后调用此接口
    """
    # 获取通知参数
    params = request.GET.dict() if request.method == 'GET' else request.POST.dict()
    
    logger.info(f'收到支付通知: method={request.method}, params={params}')
    
    # 验证签名
    easypay = EasyPayClient()
    if not easypay.verify_sign(params):
        logger.error('签名验证失败')
        return HttpResponse('fail')
    
    # 获取订单信息
    out_trade_no = params.get('out_trade_no')  # 商户订单号
    trade_status = params.get('trade_status')  # 支付状态
    trade_no = params.get('trade_no')  # 易支付订单号
    
    logger.info(f'订单号: {out_trade_no}, 状态: {trade_status}, 易支付订单号: {trade_no}')
    
    if trade_status == 'TRADE_SUCCESS':
        try:
            order = Order.objects.get(id=out_trade_no)
            
            # 防止重复处理
            if order.status == 'pending':
                # 更新订单状态
                order.status = 'paid'
                order.save()
                
                logger.info(f'订单 {out_trade_no} 支付成功，状态已更新')
            else:
                logger.info(f'订单 {out_trade_no} 已处理过，当前状态：{order.status}')
        except Order.DoesNotExist:
            logger.error(f'订单 {out_trade_no} 不存在')
            return HttpResponse('fail')
        except Exception as e:
            logger.error(f'处理订单异常: {str(e)}')
            return HttpResponse('fail')
    
    # 必须返回 success
    return HttpResponse('success')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_payment(request, order_id):
    """
    查询支付状态
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 检查权限
    if order.buyer != request.user and order.product.seller != request.user:
        return Response({'error': '无权限查看此订单'}, status=status.HTTP_403_FORBIDDEN)
    
    # 查询支付状态
    easypay = EasyPayClient()
    result = easypay.query_order(order_id)
    
    if result.get('code') == 1:
        payment_status = result.get('status')  # 1=已支付，0=未支付
        
        # 如果支付成功但订单状态未更新，同步更新
        if payment_status == 1 and order.status == 'pending':
            order.status = 'paid'
            order.save()
            logger.info(f'订单 {order_id} 状态同步更新为已支付')
        
        return Response({
            'success': True,
            'status': payment_status,
            'paid': payment_status == 1,
            'order_status': order.status
        })
    else:
        return Response({
            'success': False,
            'error': result.get('msg', '查询失败')
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refund_payment(request, order_id):
    """
    申请退款
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 只有买家可以申请退款
    if order.buyer != request.user:
        return Response({'error': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
    
    # 只有已支付的订单可以退款
    if order.status != 'paid':
        return Response({'error': '订单状态不允许退款'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 调用退款接口
    easypay = EasyPayClient()
    result = easypay.refund_order(
        out_trade_no=order_id,
        money=order.total_price
    )
    
    if result.get('code') == 1:
        logger.info(f'订单 {order_id} 退款成功')
        return Response({
            'success': True,
            'message': '退款成功'
        })
    else:
        logger.error(f'订单 {order_id} 退款失败: {result.get("msg")}')
        return Response({
            'success': False,
            'error': result.get('msg', '退款失败')
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_complete_payment(request, order_id):
    """
    演示模式：手动完成支付
    仅在 EASYPAY_DEMO_MODE = True 时可用
    """
    from django.conf import settings
    
    # 检查是否启用演示模式
    if not getattr(settings, 'EASYPAY_DEMO_MODE', False):
        return Response({
            'success': False,
            'error': '此接口仅在演示模式下可用'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 检查权限
    if order.buyer != request.user:
        return Response({'error': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
    
    # 检查订单状态
    if order.status != 'pending':
        return Response({
            'success': False,
            'error': f'订单状态不正确，当前状态：{order.get_status_display()}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 更新订单状态为已支付
    order.status = 'paid'
    order.save()
    
    logger.info(f'演示模式：订单 {order_id} 手动标记为已支付')
    
    return Response({
        'success': True,
        'message': '演示支付完成',
        'order_status': 'paid'
    })

