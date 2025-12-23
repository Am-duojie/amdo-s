"""
支付相关视图
使用支付宝支付
"""
import re
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from .models import Order, VerifiedOrder
from .alipay_client import AlipayClient
import logging

logger = logging.getLogger(__name__)


def _sanitize_subject(title: str, order_id: int) -> str:
    """
    清洗订单标题，避免支付宝因非法字符/格式报 INVALID_PARAMETER。
    - 去除换行、制表符，压缩多余空格
    - 移除非常用符号和表情等可能导致校验失败的字符
    - 兜底使用订单号，确保非空
    """
    raw = str(title or '').strip()
    if not raw:
        return f"订单{order_id}"

    # 去除控制字符并压缩空白
    cleaned = re.sub(r'[\r\n\t]+', ' ', raw)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # 移除非常用特殊字符与表情，保留常见中英文、数字及常用标点
    cleaned = re.sub(r'[^\w\s\-\u4e00-\u9fff.,，。！？!?:：;；（）()【】《》<>———+*#/&%￥@·]', '', cleaned)

    if not cleaned:
        cleaned = f"订单{order_id}"

    return cleaned[:120]  # 控制长度，远低于支付宝256限制


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
    
    # 获取并清洗商品标题，避免非法字符导致 INVALID_PARAMETER
    product_title = _sanitize_subject(getattr(order.product, 'title', ''), order.id)
    
    # 构建回调URL
    # 注意：支付宝沙箱环境可能不支持 localhost，需要使用公网地址
    # 如果使用 ngrok，前端地址也应该使用 ngrok 地址
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    backend_url = getattr(settings, 'BACKEND_URL', 'http://127.0.0.1:8000')
    
    # 构建 return_url
    # 策略（改进版，优先使用后端重定向，更稳定）：
    # 1. 如果后端是 ngrok，优先使用后端重定向页面（更稳定，即使前端 ngrok 离线也能工作）
    # 2. 如果前端是 ngrok 且后端不是 ngrok，使用前端地址
    # 3. 如果前后端都不是 ngrok，使用前端地址
    
    # 检查前端和后端是否是 ngrok 地址
    frontend_is_ngrok = 'ngrok' in frontend_url or 'ngrok-free.dev' in frontend_url
    backend_is_ngrok = 'ngrok' in backend_url or 'ngrok-free.dev' in backend_url
    frontend_is_localhost = 'localhost' in frontend_url or '127.0.0.1' in frontend_url
    
    # 优先使用后端重定向页面（更稳定）
    # 后端重定向页面可以处理前端 ngrok 离线的情况
    if backend_is_ngrok:
        # 后端是 ngrok，使用后端重定向页面（推荐方案，更稳定）
        if order_type == 'verified':
            return_url = f'{backend_url}/api/payment/redirect?order_id={order.id}&order_type=verified'
        else:
            return_url = f'{backend_url}/api/payment/redirect?order_id={order.id}&order_type=normal'
        logger.info(f'使用后端重定向页面（推荐，更稳定）: {return_url}')
    elif frontend_is_ngrok:
        # 前端是 ngrok 地址，直接跳转到前端
        if order_type == 'verified':
            return_url = f'{frontend_url}/payment/return?order_id={order.id}&order_type=verified'
        else:
            return_url = f'{frontend_url}/payment/return?order_id={order.id}&order_type=normal'
        logger.info(f'使用前端 ngrok 地址作为 return_url: {return_url}')
    else:
        # 其他情况，直接跳转到前端
        if order_type == 'verified':
            return_url = f'{frontend_url}/payment/return?order_id={order.id}&order_type=verified'
        else:
            return_url = f'{frontend_url}/payment/return?order_id={order.id}&order_type=normal'
        logger.info(f'直接跳转到前端: {return_url}')
    
    # 注意：notify_url 不建议包含查询参数，可能导致签名验证问题
    # 我们通过 out_trade_no 来区分订单类型，格式为: {order_type}_{order_id}
    notify_url = f'{backend_url}/api/payment/alipay/notify/'
    
    # 检查是否启用分账功能
    enable_royalty = getattr(settings, 'ENABLE_ALIPAY_ROYALTY', False)
    
    # 创建支付订单
    result = alipay.create_trade(
        out_trade_no=f'{order_type}_{order.id}',
        subject=product_title,
        total_amount=order.total_price,
        return_url=return_url,
        notify_url=notify_url,
        enable_royalty=enable_royalty  # 如果启用分账，设置分账冻结参数
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
def payment_redirect(request):
    '''Redirects Alipay callbacks straight to the frontend payment return page.'''
    all_params = dict(request.GET)
    logger.info('========== ????????? ==========')
    logger.info(f'????: {request.method}')
    logger.info(f'???? {all_params}')
    logger.info(f'??URL: {request.build_absolute_uri()}')

    order_id = request.GET.get('order_id')
    order_type = request.GET.get('order_type', 'normal')

    if not order_id:
        out_trade_no = request.GET.get('out_trade_no', '')
        if out_trade_no and '_' in out_trade_no:
            parts = out_trade_no.split('_', 1)
            order_type = parts[0]
            order_id = parts[1]
            logger.info(f'?? out_trade_no ??: order_type={order_type}, order_id={order_id}')
        else:
            logger.error('?? ID ??????? out_trade_no ??')
            return HttpResponse('?? ID ??', status=400)

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    query_params = request.GET.copy()
    query_params.pop('order_id', None)
    query_params.pop('order_type', None)

    query_string = '&'.join([f'{k}={v}' for k, v in query_params.items()])
    redirect_url = f'{frontend_url}/payment/return?order_id={order_id}&order_type={order_type}'
    if query_string:
        redirect_url = f'{redirect_url}&{query_string}'

    logger.info(f'??????? URL: {redirect_url}')

    response = HttpResponseRedirect(redirect_url)
    if 'localhost' in frontend_url or '127.0.0.1' in frontend_url:
        response['Refresh'] = f'3; url={redirect_url}'
    return response
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
