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
    """
    支付回调重定向页面
    用于跳过 ngrok 警告页面，重定向到前端支付回调页面
    
    改进：
    1. 如果前端 ngrok 离线，提供备用方案（直接显示支付结果）
    2. 使用 HTTP 302 重定向 + HTML meta refresh 双重保障
    3. 如果前端是 localhost 或离线，提供手动跳转链接和说明
    """
    # 记录所有接收到的参数（用于调试）
    all_params = dict(request.GET)
    logger.info(f'========== 支付回调重定向页面 ==========')
    logger.info(f'请求方法: {request.method}')
    logger.info(f'所有参数: {all_params}')
    logger.info(f'请求路径: {request.path}')
    logger.info(f'完整URL: {request.build_absolute_uri()}')
    
    order_id = request.GET.get('order_id')
    order_type = request.GET.get('order_type', 'normal')
    
    # 检查是否有支付宝返回的参数
    alipay_params = {
        'out_trade_no': request.GET.get('out_trade_no'),
        'trade_status': request.GET.get('trade_status'),
        'trade_no': request.GET.get('trade_no'),
        'total_amount': request.GET.get('total_amount'),
    }
    logger.info(f'支付宝返回参数: {alipay_params}')
    
    if not order_id:
        # 如果没有 order_id，尝试从 out_trade_no 解析
        out_trade_no = request.GET.get('out_trade_no', '')
        if out_trade_no and '_' in out_trade_no:
            parts = out_trade_no.split('_', 1)
            order_type = parts[0]
            order_id = parts[1]
            logger.info(f'从 out_trade_no 解析: order_type={order_type}, order_id={order_id}')
        else:
            logger.error('订单ID缺失，且无法从 out_trade_no 解析')
            return HttpResponse('订单ID缺失', status=400)
    
    # 获取前端地址
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    backend_url = getattr(settings, 'BACKEND_URL', 'http://127.0.0.1:8000')
    
    # 检查前端是否是 localhost（可能无法从外部访问）
    is_localhost = 'localhost' in frontend_url or '127.0.0.1' in frontend_url
    frontend_is_ngrok = 'ngrok' in frontend_url or 'ngrok-free.dev' in frontend_url
    
    # 构建前端回调URL，保留所有支付宝返回的参数
    query_params = request.GET.copy()
    # 移除我们自己的参数
    query_params.pop('order_id', None)
    query_params.pop('order_type', None)
    
    # 构建查询字符串
    query_string = '&'.join([f'{k}={v}' for k, v in query_params.items()])
    if query_string:
        redirect_url = f'{frontend_url}/payment/return?order_id={order_id}&order_type={order_type}&{query_string}'
    else:
        redirect_url = f'{frontend_url}/payment/return?order_id={order_id}&order_type={order_type}'
    
    logger.info(f'支付回调重定向: order_id={order_id}, order_type={order_type}')
    logger.info(f'重定向URL: {redirect_url}')
    
    # 尝试查询支付状态（用于显示在页面上）
    # 优先查询支付宝接口，确保获取最新状态
    payment_status = None
    payment_message = '正在查询支付状态...'
    try:
        from .models import Order, VerifiedOrder
        from .alipay_client import AlipayClient
        
        # 先查询支付宝接口获取最新支付状态
        alipay = AlipayClient()
        out_trade_no = f'{order_type}_{order_id}'
        alipay_result = alipay.query_trade(out_trade_no)
        
        if alipay_result.get('success'):
            trade_status = alipay_result.get('trade_status', '')
            # 如果支付宝显示支付成功，但订单状态未更新，立即更新
            if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
                try:
                    if order_type == 'verified':
                        order = VerifiedOrder.objects.get(id=order_id)
                    else:
                        order = Order.objects.get(id=order_id)
                    
                    if order.status == 'pending':
                        order.status = 'paid'
                        if hasattr(order, 'alipay_trade_no') and alipay_result.get('trade_no'):
                            order.alipay_trade_no = alipay_result.get('trade_no')
                        order.save()
                        logger.info(f'支付回调：订单 {order_id} 状态已更新为已支付')
                    
                    payment_status = 'success'
                    payment_message = '支付成功！'
                except Exception as e:
                    logger.error(f'更新订单状态失败: {str(e)}')
                    payment_status = 'success'  # 支付宝已确认支付成功
                    payment_message = '支付成功！'
            else:
                payment_status = 'processing'
                payment_message = '支付处理中，请稍候...'
        else:
            # 支付宝查询失败，检查订单状态
            if order_type == 'verified':
                order = VerifiedOrder.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id)
            
            if order.status == 'paid':
                payment_status = 'success'
                payment_message = '支付成功！'
            elif order.status == 'pending':
                payment_status = 'processing'
                payment_message = '支付处理中，请稍候...'
            else:
                payment_status = 'unknown'
                payment_message = f'订单状态：{order.get_status_display()}'
    except Exception as e:
        logger.error(f'查询支付状态异常: {str(e)}', exc_info=True)
        payment_status = 'processing'
        payment_message = '正在查询支付状态，请稍候...'
    
    logger.info(f'支付状态查询结果: status={payment_status}, message={payment_message}')
    
    # 根据支付状态显示不同的图标和颜色
    status_icon = '✓' if payment_status == 'success' else '⏳' if payment_status == 'processing' else '❓'
    status_color = '#10b981' if payment_status == 'success' else '#f59e0b' if payment_status == 'processing' else '#6b7280'
    status_title = '支付成功' if payment_status == 'success' else '支付处理中' if payment_status == 'processing' else '支付状态未知'
    
    # 如果前端是 localhost，需要特殊处理
    # 因为支付宝从外部跳转回来，无法直接访问 localhost
    # 但用户在本地浏览器中打开后端页面时，可以跳转到 localhost
    if is_localhost:
        # 前端是 localhost，提供跳转方案
        # 用户在本地浏览器中打开此页面时，可以跳转到 localhost
        
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="3;url={redirect_url}">
            <title>{status_title} - 易淘</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    max-width: 500px;
                    text-align: center;
                }}
                .status-icon {{
                    font-size: 64px;
                    color: {status_color};
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: {status_color};
                    margin-bottom: 10px;
                }}
                .status-message {{
                    font-size: 18px;
                    color: #6b7280;
                    margin-bottom: 20px;
                }}
                .info {{
                    background: #f0f9ff;
                    border-left: 4px solid #3b82f6;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: left;
                    border-radius: 4px;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    margin: 10px;
                    padding: 12px 24px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                    transition: background 0.3s;
                }}
                .button:hover {{
                    background: #5568d3;
                }}
                .button-secondary {{
                    background: #6b7280;
                }}
                .button-secondary:hover {{
                    background: #4b5563;
                }}
                .button-success {{
                    background: #10b981;
                }}
                .button-success:hover {{
                    background: #059669;
                }}
            </style>
            <script>
                // 尝试跳转到前端（如果前端可用）
                let redirectAttempted = false;
                const redirectUrl = '{redirect_url}';
                
                function tryRedirect() {{
                    if (!redirectAttempted) {{
                        redirectAttempted = true;
                        console.log('准备跳转到:', redirectUrl);
                        setTimeout(function() {{
                            try {{
                                console.log('正在跳转...');
                                window.location.href = redirectUrl;
                            }} catch(e) {{
                                console.error('跳转失败:', e);
                                alert('自动跳转失败，请点击下方按钮手动跳转');
                            }}
                        }}, 2000);
                    }}
                }}
                
                // 页面加载后立即尝试跳转
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', tryRedirect);
                }} else {{
                    tryRedirect();
                }}
                // 备用：页面加载完成后也尝试跳转
                window.onload = tryRedirect;
            </script>
        </head>
        <body>
            <div class="container">
                <div class="status-icon">{status_icon}</div>
                <h1>{status_title}</h1>
                <p class="status-message">{payment_message}</p>
                <p style="font-size: 16px; margin-bottom: 20px;">订单号: <strong>#{order_id}</strong></p>
                
                <div class="info">
                    <strong>提示：</strong><br>
                    支付已完成！系统正在尝试跳转到本地前端页面（3秒后自动跳转）。<br>
                    如果页面没有自动跳转，请点击下方按钮手动跳转：
                </div>
                
                <div style="margin-top: 30px;">
                    <a href="{redirect_url}" class="button button-success">跳转到本地前端页面</a><br>
                    <a href="javascript:location.reload()" class="button button-secondary" style="margin-top: 10px;">刷新页面查看最新状态</a><br>
                    <p style="margin-top: 20px; color: #6b7280; font-size: 12px;">
                        如果无法跳转，请确保本地前端服务正在运行（http://localhost:5173），<br>
                        或稍后在"我的订单"中查看订单状态
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''
    else:
        # 前端是公网地址，可以直接跳转
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="0;url={redirect_url}">
            <title>正在跳转...</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                }}
            </style>
            <script>
                // 立即跳转
                window.location.href = '{redirect_url}';
            </script>
        </head>
        <body>
            <div class="container">
                <h2>支付完成</h2>
                <p>正在跳转到支付结果页面...</p>
                <p>如果页面没有自动跳转，请<a href="{redirect_url}" style="color: #667eea;">点击这里</a></p>
            </div>
        </body>
        </html>
        '''
    
    response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
    # 尝试使用 HTTP 302 重定向（但保留 HTML 作为备用）
    # 注意：由于 ngrok 警告页面，302 重定向可能不会立即生效
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
