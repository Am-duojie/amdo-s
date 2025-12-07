"""
支付相关视图
使用支付宝支付
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import Order, VerifiedOrder
from .alipay_client import AlipayClient
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    创建支付订单（支付宝支付）
    返回支付URL，前端直接跳转
    
    参数:
        order_id: 订单ID
        order_type: 订单类型，'normal' 为易淘订单，'verified' 为官方验订单
    """
    order_id = request.data.get('order_id')
    order_type = request.data.get('order_type', 'normal')  # normal: 易淘订单, verified: 官方验订单
    
    if not order_id:
        return Response({'error': '订单ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 根据订单类型获取订单
    try:
        if order_type == 'verified':
            order = VerifiedOrder.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id)
    except (Order.DoesNotExist, VerifiedOrder.DoesNotExist):
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 检查订单权限
    if order.buyer != request.user:
        return Response({'error': '无权限操作此订单'}, status=status.HTTP_403_FORBIDDEN)
    
    # 检查订单状态
    if order.status != 'pending':
        return Response({'error': f'订单状态不正确，当前状态：{order.get_status_display()}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 使用支付宝支付
    alipay = AlipayClient()
    
    # 验证配置
    is_valid, error_msg = alipay.validate_config()
    if not is_valid:
        logger.error(f'支付宝配置错误: {error_msg}')
        return Response({
            'success': False,
            'error': error_msg
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # 获取商品标题
    product_title = order.product.title[:256]
    
    # 构建回调URL
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    # 注意：notify_url 不建议包含查询参数，可能导致签名验证问题
    # 我们通过 out_trade_no 来区分订单类型，格式为: {order_type}_{order_id}
    notify_url = f'{getattr(settings, "BACKEND_URL", "http://127.0.0.1:8000")}/api/payment/alipay/notify/'
    
    if order_type == 'verified':
        return_url = f'{base_url}/verified-order/{order.id}'
    else:
        return_url = f'{base_url}/order/{order.id}'
    
    # 创建支付订单
    result = alipay.create_trade(
        out_trade_no=f'{order_type}_{order.id}',
        subject=product_title,
        total_amount=order.total_price,
        return_url=return_url,
        notify_url=notify_url
    )
    
    if result.get('success'):
        logger.info(f'支付宝支付订单创建成功: order_id={order.id}, order_type={order_type}')
        return Response({
            'success': True,
            'payment_url': result.get('payment_url'),
            'payment_provider': 'alipay',
        })
    else:
        error_msg = result.get('msg', '创建支付失败')
        logger.error(f'支付宝支付订单创建失败: {error_msg}')
        return Response({
            'success': False,
            'error': error_msg
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_url(request):
    """
    创建支付URL（页面跳转支付）
    兼容旧接口，内部调用 create_payment
    """
    return create_payment(request)


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def alipay_payment_notify(request):
    """
    支付宝支付异步通知回调
    支付宝会在支付成功后调用此接口
    """
    # 获取通知参数
    params = request.GET.dict() if request.method == 'GET' else request.POST.dict()
    
    logger.info(f'收到支付宝支付通知: method={request.method}, params={params}')
    
    # 验证签名
    alipay = AlipayClient()
    if not alipay.verify_notify(params):
        logger.error('支付宝签名验证失败')
        return HttpResponse('fail')
    
    # 解析订单号（格式：order_type_order_id）
    out_trade_no = params.get('out_trade_no', '')
    trade_status = params.get('trade_status', '')
    trade_no = params.get('trade_no', '')
    
    logger.info(f'支付宝订单号: {out_trade_no}, 状态: {trade_status}, 支付宝交易号: {trade_no}')
    
    # 解析订单类型和ID
    if '_' in out_trade_no:
        parts = out_trade_no.split('_', 1)
        order_type = parts[0]
        order_id = parts[1]
    else:
        # 兼容旧格式
        order_type = 'normal'
        order_id = out_trade_no
    
    # 处理支付成功
    if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
        try:
            if order_type == 'verified':
                order = VerifiedOrder.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id)
            
            # 防止重复处理
            if order.status == 'pending':
                # 更新订单状态
                order.status = 'paid'
                # 记录支付宝交易号
                if hasattr(order, 'alipay_trade_no'):
                    order.alipay_trade_no = trade_no
                # 支付完成后分账仍待触发
                if hasattr(order, 'settlement_status') and order.settlement_status != 'settled':
                    order.settlement_status = 'pending'
                order.save()
                
                logger.info(f'订单 {out_trade_no} 支付成功，状态已更新')
            else:
                logger.info(f'订单 {out_trade_no} 已处理过，当前状态：{order.status}')
        except (Order.DoesNotExist, VerifiedOrder.DoesNotExist):
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
    查询支付状态（支付宝支付）
    """
    order_type = request.query_params.get('order_type', 'normal')  # normal 或 verified
    
    # 根据订单类型获取订单
    try:
        if order_type == 'verified':
            order = VerifiedOrder.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id)
    except (Order.DoesNotExist, VerifiedOrder.DoesNotExist):
        return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 检查权限
    if order.buyer != request.user:
        if order_type == 'verified':
            return Response({'error': '无权限查看此订单'}, status=status.HTTP_403_FORBIDDEN)
        elif order.product.seller != request.user:
            return Response({'error': '无权限查看此订单'}, status=status.HTTP_403_FORBIDDEN)
    
    # 查询支付状态
    alipay = AlipayClient()
    result = alipay.query_trade(f'{order_type}_{order.id}')
    
    if result.get('success'):
        trade_status = result.get('trade_status', '')
        
        # 如果支付成功但订单状态未更新，同步更新
        if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED'] and order.status == 'pending':
            order.status = 'paid'
            order.save()
            logger.info(f'订单 {order_id} 状态同步更新为已支付')
        
        return Response({
            'success': True,
            'trade_status': trade_status,
            'paid': trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED'],
            'order_status': order.status
        })
    else:
        return Response({
            'success': False,
            'error': result.get('msg', '查询失败')
        }, status=status.HTTP_400_BAD_REQUEST)
