import time
from datetime import datetime, timedelta
import json
from django.utils import timezone
from django.db.models import Count, Q, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
from .models import AdminUser, AdminRole, AdminInspectionReport, AdminAuditQueueItem, AdminAuditLog, AdminRefreshToken, AdminTokenBlacklist
from app.secondhand_app.models import RecycleOrder, VerifiedProduct, VerifiedOrder, Order, Shop, Category, Product, Message, Address
from app.secondhand_app.alipay_client import AlipayClient
from .serializers import AdminUserSerializer, RecycleOrderListSerializer, VerifiedProductListSerializer, AdminAuditQueueItemSerializer, ShopAdminSerializer
from app.secondhand_app.serializers import OrderSerializer, VerifiedProductSerializer
from .jwt import encode as jwt_encode, decode as jwt_decode
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

def get_admin_from_request(request):
    import logging
    logger = logging.getLogger(__name__)
    
    # 记录请求方法、路径和时间
    method = getattr(request, 'method', 'UNKNOWN')
    path = getattr(request, 'path', 'UNKNOWN')
    logger.info(f'[get_admin_from_request] 开始处理请求: {method} {path}')
    
    # 尝试多种方式获取Authorization头
    auth = None
    auth_source = None
    
    # 方式1: 从request.headers获取（Django REST Framework）
    if hasattr(request, 'headers'):
        try:
            # Django REST Framework的headers是大小写不敏感的
            auth = request.headers.get('Authorization', '')
            if auth:
                auth_source = 'request.headers[Authorization]'
            if not auth:
                auth = request.headers.get('AUTHORIZATION', '')
                if auth:
                    auth_source = 'request.headers[AUTHORIZATION]'
        except Exception as e:
            logger.warning(f'[get_admin_from_request] 读取request.headers失败: {e}')
    
    # 方式2: 从META中获取（Django原生方式）
    # Django会将HTTP头转换为大写，并添加HTTP_前缀，连字符变为下划线
    # Authorization -> HTTP_AUTHORIZATION
    if not auth:
        # 尝试多种可能的键名
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if auth:
            auth_source = 'META[HTTP_AUTHORIZATION]'
        if not auth:
            auth = request.META.get('HTTP_AUTH', '')
            if auth:
                auth_source = 'META[HTTP_AUTH]'
        if not auth:
            auth = request.META.get('AUTHORIZATION', '')
            if auth:
                auth_source = 'META[AUTHORIZATION]'
    
    # 详细日志 - 无论是否找到都记录
    if auth:
        logger.info(f'[get_admin_from_request] 找到Authorization头，来源: {auth_source}')
        logger.info(f'[get_admin_from_request] Authorization值: {auth[:20]}...' if len(auth) > 20 else f'[get_admin_from_request] Authorization值: {auth}')
    else:
        logger.warning(f'[get_admin_from_request] 未找到Authorization头')
        # 查找所有包含AUTH的META键
        auth_keys = [k for k in request.META.keys() if 'AUTH' in k.upper()]
        logger.warning(f'[get_admin_from_request] 相关META键: {auth_keys}')
        if hasattr(request, 'headers'):
            try:
                headers_dict = dict(request.headers)
                logger.warning(f'[get_admin_from_request] request.headers内容: {headers_dict}')
            except Exception as e:
                logger.warning(f'[get_admin_from_request] 无法读取request.headers: {e}')
        # 打印所有HTTP_开头的META键
        http_keys = [k for k in request.META.keys() if k.startswith('HTTP_')]
        logger.warning(f'[get_admin_from_request] 所有HTTP_开头的META键: {http_keys}')
    
    if not auth or not auth.startswith('Bearer '):
        if auth:
            logger.warning(f'[get_admin_from_request] Authorization头格式不正确，不是Bearer开头: {auth[:30]}...')
        return None
    
    token = auth[7:]
    try:
        payload = jwt_decode(token, settings.ADMIN_JWT_SECRET)
        uid = payload.get('uid')
        if not uid:
            return None
        admin = AdminUser.objects.get(id=uid)
        # 检查token是否在黑名单中
        jti = payload.get('jti')
        if jti and AdminTokenBlacklist.objects.filter(jti=jti).exists():
            return None
        return admin
    except ValueError as e:
        # JWT验证失败（token过期、签名错误等）
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'JWT验证失败: {str(e)}')
        return None
    except AdminUser.DoesNotExist:
        return None
    except Exception as e:
        # 其他异常
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'获取管理员用户时发生异常: {str(e)}', exc_info=True)
        return None

def has_perms(admin, perms_list):
    if not admin or not admin.role:
        return False
    role_perms = admin.role.permissions or []
    if '*' in role_perms:
        return True
    for p in perms_list:
        if p in role_perms:
            return True
    return False

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        if not username or not password:
            return Response({'detail': '用户名和密码不能为空'}, status=400)
        try:
            admin = AdminUser.objects.get(username=username)
        except AdminUser.DoesNotExist:
            return Response({'detail': '用户名或密码错误'}, status=401)
        if not check_password(password, admin.password_hash):
            return Response({'detail': '用户名或密码错误'}, status=401)
        now = int(time.time())
        expires_in = settings.ADMIN_JWT_EXPIRE_DAYS * 24 * 3600
        exp = now + expires_in
        import secrets
        jti = secrets.token_urlsafe(16)
        payload = {'uid': admin.id, 'username': admin.username, 'exp': exp, 'jti': jti}
        token = jwt_encode(payload, settings.ADMIN_JWT_SECRET)
        refresh_token_obj = AdminRefreshToken.objects.create(
            user=admin,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(days=30)
        )
        user_data = AdminUserSerializer(admin).data
        return Response({
            'token': token,
            'refresh_token': refresh_token_obj.token,
            'user': user_data
        })

@method_decorator(csrf_exempt, name='dispatch')
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """
        刷新访问token
        需要提供有效的refresh_token
        """
        refresh_token = request.data.get('refresh_token', '').strip()
        if not refresh_token:
            return Response({'detail': 'refresh_token required'}, status=400)
        try:
            rt_obj = AdminRefreshToken.objects.get(token=refresh_token, revoked=False)
            # 检查refresh token是否过期
            if rt_obj.expires_at < timezone.now():
                # 标记为已撤销
                rt_obj.revoked = True
                rt_obj.save()
                return Response({'detail': 'refresh_token expired'}, status=401)
            admin = rt_obj.user
            now = int(time.time())
            expires_in = settings.ADMIN_JWT_EXPIRE_DAYS * 24 * 3600
            exp = now + expires_in
            import secrets
            jti = secrets.token_urlsafe(16)
            payload = {'uid': admin.id, 'username': admin.username, 'exp': exp, 'jti': jti}
            token = jwt_encode(payload, settings.ADMIN_JWT_SECRET)
            return Response({'token': token})
        except AdminRefreshToken.DoesNotExist:
            return Response({'detail': 'invalid refresh_token'}, status=401)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'刷新token时发生异常: {str(e)}', exc_info=True)
            return Response({'detail': 'refresh token failed'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        admin = get_admin_from_request(request)
        if admin:
            refresh_token = request.data.get('refresh_token', '').strip()
            if refresh_token:
                AdminRefreshToken.objects.filter(token=refresh_token).update(revoked=True)
            auth = request.headers.get('Authorization','')
            if auth.startswith('Bearer '):
                token = auth[7:]
                try:
                    payload = jwt_decode(token, settings.ADMIN_JWT_SECRET)
                    jti = payload.get('jti')
                    if jti:
                        AdminTokenBlacklist.objects.get_or_create(jti=jti)
                except:
                    pass
        return Response({'success': True})

@method_decorator(csrf_exempt, name='dispatch')
class AuthMeView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        user_data = AdminUserSerializer(admin).data
        return Response({'user': user_data})

@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        old_password = request.data.get('old_password', '').strip()
        new_password = request.data.get('new_password', '').strip()
        if not check_password(old_password, admin.password_hash):
            return Response({'detail': '旧密码错误'}, status=400)
        admin.password_hash = make_password(new_password)
        admin.save()
        return Response({'success': True})

@method_decorator(csrf_exempt, name='dispatch')
class PermissionsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        perms = admin.role.permissions if admin.role else []
        return Response({'permissions': perms})

@method_decorator(csrf_exempt, name='dispatch')
class MenusView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        perms = admin.role.permissions if admin.role else []
        menus = []
        if '*' in perms or any('dashboard:view' in p for p in perms):
            menus.append({'key': 'dashboard', 'title': '总览', 'path': '/admin/dashboard'})
        # 可以根据权限动态生成菜单
        return Response({'menus': menus})

@method_decorator(csrf_exempt, name='dispatch')
class DashboardMetricsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['dashboard:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        today = timezone.now().date()
        gmv_qs = VerifiedOrder.objects.filter(created_at__date=today, status__in=['paid','completed']).values_list('total_price', flat=True)
        gmv_today = sum([float(x) for x in gmv_qs]) if gmv_qs else 0.0
        metrics = {
            'todayInspection': RecycleOrder.objects.filter(created_at__date=today).count(),
            'pendingAudit': AdminAuditQueueItem.objects.filter(status='pending').count(),
            'verifiedPublished': VerifiedProduct.objects.filter(status='active').count(),
            'verifiedOrdersPaidToday': VerifiedOrder.objects.filter(created_at__date=today, status='paid').count(),
            'verifiedOrdersCompletedToday': VerifiedOrder.objects.filter(created_at__date=today, status='completed').count(),
            'gmvToday': gmv_today
        }
        return Response(metrics)

@method_decorator(csrf_exempt, name='dispatch')
class StatisticsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['dashboard:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end = timezone.now().date()
            start = end - timedelta(days=30)
        
        recycle_total = RecycleOrder.objects.filter(created_at__date__gte=start, created_at__date__lte=end).count()
        recycle_completed = RecycleOrder.objects.filter(status='completed', created_at__date__gte=start, created_at__date__lte=end).count()
        verified_total = VerifiedOrder.objects.filter(created_at__date__gte=start, created_at__date__lte=end).count()
        gmv_qs = VerifiedOrder.objects.filter(created_at__date__gte=start, created_at__date__lte=end, status__in=['paid','completed']).values_list('total_price', flat=True)
        total_gmv = sum([float(x) for x in gmv_qs]) if gmv_qs else 0.0
        
        return Response({
            'recycleOrdersTotal': recycle_total,
            'recycleCompleted': recycle_completed,
            'verifiedOrdersTotal': verified_total,
            'totalGMV': total_gmv
        })

# 质检订单相关视图
@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrdersView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        status_filter = request.query_params.get('status', '')
        payment_status_filter = request.query_params.get('payment_status', '')
        search = request.query_params.get('search', '').strip()
        qs = RecycleOrder.objects.select_related('user').all().order_by('-created_at')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if payment_status_filter:
            qs = qs.filter(payment_status=payment_status_filter)
        if search:
            qs = qs.filter(Q(user__username__icontains=search) | Q(brand__icontains=search) | Q(model__icontains=search) | Q(id__icontains=search))
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{
            'id': o.id,
            'user': {'id': o.user.id, 'username': o.user.username},
            'status': o.status,
            'payment_status': o.payment_status,
            'device_type': o.device_type,
            'brand': o.brand,
            'model': o.model,
            'storage': o.storage or '',
            'condition': o.condition,
            'estimated_price': float(o.estimated_price) if o.estimated_price else None,
            'final_price': float(o.final_price) if o.final_price else None,
            'bonus': float(o.bonus) if o.bonus else 0,
            'total_price': float(o.final_price + o.bonus) if o.final_price else None,
            'shipping_carrier': o.shipping_carrier or '',
            'tracking_number': o.tracking_number or '',
            'price_dispute': o.price_dispute,
            'created_at': o.created_at.isoformat(),
            'updated_at': o.updated_at.isoformat()
        } for o in items]
        return Response({'results': data, 'count': total})

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderDetailView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            o = RecycleOrder.objects.get(id=order_id)
        except RecycleOrder.DoesNotExist:
            return Response({'success': False})
        rep = o.admin_reports.order_by('-id').first()
        profile = getattr(o.user, 'profile', None)
        return Response({'success': True, 'item': {
            'id': o.id,
            'user': {
                'id': o.user.id,
                'username': o.user.username,
                'email': getattr(o.user, 'email', ''),
                'alipay_login_id': (getattr(profile, 'alipay_login_id', '') if profile else ''),
                'alipay_real_name': (getattr(profile, 'alipay_real_name', '') if profile else '')
            },
            'status': o.status,
            'device_type': o.device_type,
            'brand': o.brand,
            'model': o.model,
            'storage': o.storage or '',
            'condition': o.condition,
            'estimated_price': float(o.estimated_price) if o.estimated_price else None,
            'final_price': float(o.final_price) if o.final_price else None,
            'bonus': float(o.bonus) if o.bonus else 0,
            'total_price': float(o.final_price + o.bonus) if o.final_price else None,
            'contact_name': o.contact_name,
            'contact_phone': o.contact_phone,
            'address': o.address,
            'note': o.note or '',
            # 物流信息
            'shipping_carrier': o.shipping_carrier or '',
            'tracking_number': o.tracking_number or '',
            'shipped_at': o.shipped_at.isoformat() if o.shipped_at else None,
            'received_at': o.received_at.isoformat() if o.received_at else None,
            # 质检信息
            'inspected_at': o.inspected_at.isoformat() if o.inspected_at else None,
            # 打款信息
            'payment_status': o.payment_status,
            'payment_method': o.payment_method or '',
            'payment_account': o.payment_account or '',
            'paid_at': o.paid_at.isoformat() if o.paid_at else None,
            'payment_note': o.payment_note or '',
            # 价格异议
            'price_dispute': o.price_dispute,
            'price_dispute_reason': o.price_dispute_reason or '',
            'reject_reason': o.reject_reason or '',
            # 时间信息
            'created_at': o.created_at.isoformat(),
            'updated_at': o.updated_at.isoformat(),
            # 质检报告
            'report': {'check_items': (rep.check_items if rep else {}), 'remarks': (rep.remarks if rep else ''), 'created_at': (rep.created_at.isoformat() if rep else None)}
        }})
    def put(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        # 从请求体或查询参数获取状态（优先从body获取）
        status_val = None
        reject_reason = ''
        
        # 尝试从request.data获取（JSON body）
        if hasattr(request, 'data') and request.data:
            status_val = request.data.get('status')
            reject_reason = request.data.get('reject_reason', '').strip()
        
        # 如果body中没有，尝试从query参数获取
        if not status_val:
            status_val = request.query_params.get('status')
        
        if not status_val:
            return Response({'success': False, 'detail': '状态参数不能为空'}, status=400)
        try:
            o = RecycleOrder.objects.get(id=order_id)
            old_status = o.status
            o.status = status_val
            if status_val == 'cancelled' and reject_reason:
                o.reject_reason = reject_reason
            # 状态变更时更新时间戳
            if status_val == 'inspected' and not o.inspected_at:
                o.inspected_at = timezone.now()
                # 如果没有收到时间，自动设置收到时间
                if not o.received_at:
                    o.received_at = timezone.now()
            elif status_val == 'completed':
                # 订单完成时，如果最终价格未设置，使用预估价格
                if not o.final_price and o.estimated_price:
                    o.final_price = o.estimated_price
            o.save()
            AdminAuditLog.objects.create(
                actor=admin, 
                target_type='RecycleOrder', 
                target_id=o.id, 
                action='status_change', 
                snapshot_json={'old_status': old_status, 'new_status': status_val, 'reject_reason': reject_reason}
            )
            return Response({'success': True})
        except RecycleOrder.DoesNotExist:
            return Response({'success': False})
    def post(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        items = request.data.get('check_items', {})
        remarks = request.data.get('remarks', '')
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except Exception:
                return Response({'success': False, 'detail': '检测项目JSON解析失败'}, status=400)
        if not isinstance(items, dict):
            return Response({'success': False, 'detail': '检测项目必须为对象'}, status=400)
        try:
            o = RecycleOrder.objects.get(id=order_id)
        except RecycleOrder.DoesNotExist:
            return Response({'success': False})
        AdminInspectionReport.objects.create(order=o, check_items=items, remarks=remarks)
        # 更新状态和质检时间
        if o.status in ['shipped', 'confirmed']:
            o.status = 'inspected'
            if not o.inspected_at:
                o.inspected_at = timezone.now()
            # 如果没有收到时间，设置收到时间
            if not o.received_at:
                o.received_at = timezone.now()
            o.save()
        AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='inspection_report', snapshot_json={'status': o.status, 'check_items_count': len(items)})
        return Response({'success': True})

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderLogisticsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        
        # 根据URL路径判断操作类型
        # 如果URL包含/received，则默认为receive操作
        path = request.path
        if '/received' in path:
            action = 'receive'
        else:
            action = request.data.get('action', 'ship')  # ship: 用户寄出, receive: 平台收到
        
        carrier = request.data.get('carrier', '').strip()
        tracking_number = request.data.get('tracking_number', '').strip()
        
        try:
            o = RecycleOrder.objects.get(id=order_id)
            if action == 'ship':
                # 用户寄出
                if not carrier or not tracking_number:
                    return Response({'success': False, 'detail': '物流公司和运单号不能为空'}, status=400)
                o.shipping_carrier = carrier
                o.tracking_number = tracking_number
                o.status = 'shipped'
                if not o.shipped_at:
                    o.shipped_at = timezone.now()
                AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='logistics_ship', snapshot_json={'carrier': carrier, 'tracking_number': tracking_number})
            elif action == 'receive':
                # 平台收到
                # 如果订单状态还是confirmed，先更新为shipped
                if o.status == 'confirmed':
                    o.status = 'shipped'
                # 保持shipped状态，但标记为已收到
                if not o.received_at:
                    o.received_at = timezone.now()
                AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='logistics_receive', snapshot_json={'received_at': o.received_at.isoformat()})
            else:
                return Response({'success': False, 'detail': f'不支持的操作类型: {action}'}, status=400)
            
            o.save()
            return Response({'success': True})
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': '订单不存在'}, status=404)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'确认收到设备失败: {str(e)}', exc_info=True)
            return Response({'success': False, 'detail': f'操作失败: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderPriceView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def put(self, request, order_id):
        # 调试：打印请求信息
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'[InspectionOrderPriceView] ========== 收到PUT请求 ==========')
        logger.info(f'[InspectionOrderPriceView] 路径: /inspection-orders/{order_id}/price')
        logger.info(f'[InspectionOrderPriceView] 请求方法: {request.method}')
        logger.info(f'[InspectionOrderPriceView] 完整路径: {request.path}')
        logger.info(f'[InspectionOrderPriceView] 查询参数: {request.GET}')
        
        # 记录所有HTTP_开头的META键
        http_meta_keys = [k for k in request.META.keys() if k.startswith('HTTP_')]
        logger.info(f'[InspectionOrderPriceView] META中的HTTP_*键 ({len(http_meta_keys)}个): {http_meta_keys}')
        
        # 记录所有META键（用于调试）
        all_meta_keys = list(request.META.keys())
        logger.info(f'[InspectionOrderPriceView] 所有META键数量: {len(all_meta_keys)}')
        
        # 记录request.headers
        if hasattr(request, 'headers'):
            try:
                headers_dict = dict(request.headers)
                logger.info(f'[InspectionOrderPriceView] request.headers内容: {headers_dict}')
            except Exception as e:
                logger.warning(f'[InspectionOrderPriceView] 无法读取request.headers: {e}')
        
        # 尝试直接从META读取Authorization
        auth_from_meta = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_from_meta:
            logger.info(f'[InspectionOrderPriceView] 从META[HTTP_AUTHORIZATION]直接读取到: {auth_from_meta[:30]}...')
        else:
            logger.warning(f'[InspectionOrderPriceView] META[HTTP_AUTHORIZATION]为空')
        
        # 尝试从request.headers读取Authorization
        if hasattr(request, 'headers'):
            try:
                auth_from_headers = request.headers.get('Authorization', '') or request.headers.get('AUTHORIZATION', '')
                if auth_from_headers:
                    logger.info(f'[InspectionOrderPriceView] 从request.headers读取到: {auth_from_headers[:30]}...')
                else:
                    logger.warning(f'[InspectionOrderPriceView] request.headers中没有Authorization')
            except Exception as e:
                logger.warning(f'[InspectionOrderPriceView] 读取request.headers失败: {e}')
        
        logger.info(f'[InspectionOrderPriceView] 开始调用get_admin_from_request...')
        admin = get_admin_from_request(request)
        if not admin:
            logger.error(f'[InspectionOrderPriceView] get_admin_from_request返回None，认证失败')
            return Response({'detail': '身份认证信息未提供。'}, status=401)
        logger.info(f'[InspectionOrderPriceView] 认证成功，管理员ID: {admin.id}, 用户名: {admin.username}')
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        
        price_type = request.data.get('price_type', 'final')  # estimated: 预估价格, final: 最终价格
        estimated_price = request.data.get('estimated_price')
        final_price = request.data.get('final_price')
        bonus = request.data.get('bonus', 0)
        
        try:
            o = RecycleOrder.objects.get(id=order_id)
            
            if price_type == 'estimated' and estimated_price is not None:
                # 更新预估价格（估价阶段）
                try:
                    estimated_price = float(estimated_price)
                    if estimated_price <= 0:
                        return Response({'success': False, 'detail': '价格必须大于0'}, status=400)
                    o.estimated_price = estimated_price
                    # 如果订单状态是pending，自动更新为quoted
                    if o.status == 'pending':
                        o.status = 'quoted'
                    # 清除价格异议标记（如果重新估价）
                    if o.price_dispute:
                        o.price_dispute = False
                        o.price_dispute_reason = ''
                    o.save()
                except (ValueError, TypeError):
                    return Response({'success': False, 'detail': '价格格式错误'}, status=400)
            elif price_type == 'final' and final_price is not None:
                # 更新最终价格（质检后）
                try:
                    final_price = float(final_price)
                    bonus = float(bonus) if bonus else 0
                    old_final_price = o.final_price
                    o.final_price = final_price
                    o.bonus = bonus
                    # 如果订单还未完成，且最终价格已设置，可以标记为已完成
                    if o.status == 'inspected' and not o.payment_status == 'paid':
                        o.status = 'completed'
                    # 清除价格异议标记
                    if o.price_dispute:
                        o.price_dispute = False
                        o.price_dispute_reason = ''
                except (ValueError, TypeError):
                    return Response({'success': False, 'detail': '价格格式错误'}, status=400)
            else:
                return Response({'success': False, 'detail': '价格参数错误'}, status=400)
            
            o.save()
            AdminAuditLog.objects.create(
                actor=admin, 
                target_type='RecycleOrder', 
                target_id=o.id, 
                action=f'update_{price_type}_price', 
                snapshot_json={
                    'estimated_price': float(o.estimated_price) if o.estimated_price else None,
                    'final_price': float(o.final_price) if o.final_price else None,
                    'bonus': float(o.bonus)
                }
            )
            return Response({'success': True})
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': '订单不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderPaymentView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        note = request.data.get('note', '').strip()
        payment_method = request.data.get('payment_method', '').strip()
        payment_account = request.data.get('payment_account', '').strip()
        
        try:
            o = RecycleOrder.objects.get(id=order_id)
            if not o.final_price:
                return Response({'success': False, 'detail': '订单尚未确定最终价格'}, status=400)
            # 允许已完成或已检测状态的订单打款（只要有最终价格）
            if o.status not in ['completed', 'inspected']:
                return Response({
                    'success': False, 
                    'detail': f'订单状态必须是已完成或已检测才能打款，当前状态: {o.status}',
                    'current_status': o.status,
                    'required_status': ['completed', 'inspected']
                }, status=400)
            # 如果已经打款成功，不允许重复打款
            if o.payment_status == 'paid':
                return Response({
                    'success': False, 
                    'detail': '订单已打款，无法重复打款',
                    'payment_status': o.payment_status
                }, status=400)
            
            # 计算打款总额（最终价格 + 加价）
            from decimal import Decimal
            final_price_decimal = Decimal(str(o.final_price)) if o.final_price else Decimal('0')
            bonus_decimal = Decimal(str(o.bonus)) if o.bonus else Decimal('0')
            total_amount_decimal = final_price_decimal + bonus_decimal
            total_amount = float(total_amount_decimal)
            AdminAuditLog.objects.create(
                actor=admin, 
                target_type='RecycleOrder', 
                target_id=o.id, 
                action='payment', 
                snapshot_json={
                    'amount': total_amount,
                    'final_price': float(o.final_price),
                    'bonus': float(o.bonus),
                    'note': note,
                    'payment_method': payment_method or None,
                    'payment_account': payment_account or None
                }
            )
            
            if payment_method and payment_method not in ['wallet', 'transfer']:
                return Response({'success': False, 'detail': '打款方式不支持'}, status=400)
            
            if payment_method == 'transfer':
                if not payment_account:
                    profile = getattr(o.user, 'profile', None)
                    payment_account = getattr(profile, 'alipay_login_id', '') if profile else ''
                if not payment_account:
                    return Response({'success': False, 'detail': '收款账户不能为空'}, status=400)
                o.payment_status = 'paid'
                o.paid_at = timezone.now()
                o.payment_method = 'transfer'
                o.payment_account = payment_account or None
                parts = []
                if note:
                    parts.append(note)
                parts.append(f'已直接转账，金额: ¥{total_amount}')
                if payment_account:
                    parts.append(f'收款账户: {payment_account}')
                o.payment_note = '\n'.join(parts)
                o.save()

                # 记录交易（用于前端“钱包-交易记录”展示提示）
                from app.secondhand_app.models import Wallet, WalletTransaction
                wallet, _ = Wallet.objects.get_or_create(user=o.user)
                from decimal import Decimal
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='withdraw',
                    amount=Decimal(str(-total_amount)),
                    balance_after=wallet.balance,
                    related_order=o,
                    withdraw_status='success',
                    alipay_account=payment_account or '',
                    note=f'平台已打款到支付宝（订单#{o.id}），金额：¥{total_amount}'
                )

                return Response({'success': True, 'message': '打款成功，已直接转账', 'amount': total_amount})
            
            # 将钱存入用户钱包
            from app.secondhand_app.models import Wallet, WalletTransaction
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                # 获取或创建用户钱包
                wallet, created = Wallet.objects.get_or_create(user=o.user)
                logger.info(f'[打款] 开始: 订单ID={o.id}, 用户ID={o.user.id}, 用户名={o.user.username}, 金额={total_amount}, 钱包已存在={not created}, 当前余额={wallet.balance}')
                
                # 刷新钱包对象以确保获取最新数据
                wallet.refresh_from_db()
                
                # 将钱存入钱包
                old_balance = wallet.balance
                wallet.add_balance(
                    amount=total_amount,
                    transaction_type='income',
                    related_order=o,
                    note=f'回收订单#{o.id}打款，设备：{o.brand} {o.model}'
                )
                
                # 再次刷新以确保余额已更新
                wallet.refresh_from_db()
                
                logger.info(f'[打款] 成功: 订单ID={o.id}, 用户ID={o.user.id}, 金额={total_amount}, 原余额={old_balance}, 新余额={wallet.balance}')
                
                # 更新打款状态
                o.payment_status = 'paid'
                o.paid_at = timezone.now()
                payment_note_parts = []
                if note:
                    payment_note_parts.append(note)
                payment_note_parts.append(f'已存入钱包，钱包余额: ¥{wallet.balance}')
                o.payment_note = '\n'.join(payment_note_parts)
                o.payment_method = 'wallet'
                o.payment_account = None
                o.save()
                
                logger.info(f'订单状态已更新: 订单ID={o.id}, 打款状态={o.payment_status}, 打款时间={o.paid_at}')
                
                return Response({
                    'success': True, 
                    'message': f'打款成功，已存入用户钱包。钱包余额: ¥{wallet.balance}', 
                    'amount': total_amount,
                    'wallet_balance': float(wallet.balance)
                })
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f'[打款] 异常详情: {str(e)}\n{error_trace}')
                # 打款异常时，更新打款状态为失败
                o.payment_status = 'failed'
                error_info = f'\n打款异常: {str(e)}'
                if o.payment_note:
                    o.payment_note += error_info
                else:
                    o.payment_note = error_info.strip()
                o.save()
                
                return Response({
                    'success': False,
                    'detail': f'打款异常: {str(e)}。请查看服务器日志获取详细信息。'
                }, status=500)
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': '订单不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderPublishVerifiedView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['recycled:write', 'verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            o = RecycleOrder.objects.get(id=order_id)
            if o.status not in ['inspected', 'completed']:
                return Response({'success': False, 'detail': '订单尚未完成质检'}, status=400)
            category = Category.objects.filter(name__icontains='手机').first()
            if not category:
                category = Category.objects.first()
            vp = VerifiedProduct.objects.create(
                seller=o.user,
                category=category,
                title=f"{o.brand} {o.model} {o.storage or ''}".strip(),
                description=f"回收自用户订单，已完成质检。设备类型：{o.device_type}，成色：{o.get_condition_display()}",
                price=o.final_price * 1.3 if o.final_price else 0,
                original_price=None,
                condition='good' if o.condition in ['new', 'like_new'] else 'good',
                status='active',
                location='北京',
                brand=o.brand,
                model=o.model,
                storage=o.storage,
                verified_at=timezone.now(),
                verified_by=None
            )
            AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='publish_verified', snapshot_json={'verified_product_id': vp.id, 'title': vp.title})
            return Response({'success': True, 'verified_product_id': vp.id, 'message': '发布成功'})
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': '订单不存在'}, status=404)
        except Exception as e:
            return Response({'success': False, 'detail': f'发布失败: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrdersBatchUpdateView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        ids = request.data.get('ids', [])
        new_status = request.data.get('status', '')
        if not ids or not new_status:
            return Response({'success': False, 'detail': '参数不完整'}, status=400)
        try:
            count = RecycleOrder.objects.filter(id__in=ids).update(status=new_status)
            AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=0, action='batch_update', snapshot_json={'ids': ids, 'status': new_status, 'count': count})
            return Response({'success': True, 'count': count})
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=500)

# ---------------- 上传接口 ----------------
@method_decorator(csrf_exempt, name='dispatch')
class AdminUploadImageView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        f = request.FILES.get('file')
        if not f:
            return Response({'detail': 'no file'}, status=400)
        filename = default_storage.save(os.path.join('uploads', f.name), ContentFile(f.read()))
        url = request.build_absolute_uri(settings.MEDIA_URL + filename) if not filename.startswith(settings.MEDIA_URL) else request.build_absolute_uri(filename)
        return Response({'url': url})

@method_decorator(csrf_exempt, name='dispatch')
class AdminUploadReportView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        f = request.FILES.get('file')
        if not f:
            return Response({'detail': 'no file'}, status=400)
        filename = default_storage.save(os.path.join('uploads', f.name), ContentFile(f.read()))
        url = request.build_absolute_uri(settings.MEDIA_URL + filename) if not filename.startswith(settings.MEDIA_URL) else request.build_absolute_uri(filename)
        return Response({'url': url})

# ---------------- 新版官方验商品管理（前端调用） ----------------
@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedProductListView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:view', 'verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        status_q = request.query_params.get('status')
        search = request.query_params.get('search')
        qs = VerifiedProduct.objects.all().order_by('-created_at')
        if status_q:
            qs = qs.filter(status=status_q)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(brand__icontains=search) | Q(model__icontains=search))
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        return Response({'results': VerifiedProductListSerializer(items, many=True).data, 'count': total})

    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = VerifiedProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            return Response(VerifiedProductSerializer(obj, context={'request': request}).data)
        return Response(serializer.errors, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedProductDetailView(APIView):
    authentication_classes = []
    permission_classes = []
    def get_object(self, pk):
        return VerifiedProduct.objects.get(id=pk)

    def get(self, request, pk):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:view', 'verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            obj = self.get_object(pk)
            return Response(VerifiedProductSerializer(obj, context={'request': request}).data)
        except VerifiedProduct.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)

    def put(self, request, pk):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            obj = self.get_object(pk)
        except VerifiedProduct.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        serializer = VerifiedProductSerializer(obj, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            return Response(VerifiedProductSerializer(obj, context={'request': request}).data)
        return Response(serializer.errors, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedProductPublishView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, pk):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            obj = VerifiedProduct.objects.get(id=pk)
        except VerifiedProduct.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        obj.status = 'active'
        obj.published_at = timezone.now()
        obj.save()
        return Response(VerifiedProductSerializer(obj, context={'request': request}).data)

@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedProductUnpublishView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, pk):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            obj = VerifiedProduct.objects.get(id=pk)
        except VerifiedProduct.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        obj.status = 'removed'
        obj.removed_reason = request.data.get('reason', '')
        obj.save()
        return Response(VerifiedProductSerializer(obj, context={'request': request}).data)
# 回收商品相关视图
@method_decorator(csrf_exempt, name='dispatch')
class RecycledProductsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['recycled:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = VerifiedProduct.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        return Response({'results': VerifiedProductListSerializer(items, many=True).data, 'count': total})
    def post(self, request, item_id=None):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['recycled:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        if item_id:
            try:
                p = VerifiedProduct.objects.get(id=item_id)
                p.status = 'active'
                p.save()
                return Response({'success': True})
            except VerifiedProduct.DoesNotExist:
                return Response({'success': False})
        return Response({'success': False})
    def put(self, request, item_id=None):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['recycled:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            p = VerifiedProduct.objects.get(id=item_id)
            toggle = request.data.get('toggle', True)
            p.status = 'active' if toggle else 'removed'
            p.save()
            return Response({'success': True})
        except VerifiedProduct.DoesNotExist:
            return Response({'success': False})

# 官方验商品相关视图
@method_decorator(csrf_exempt, name='dispatch')
class VerifiedListingsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, item_id=None):
        if item_id:
            admin = get_admin_from_request(request)
            if not admin:
                return Response({'detail': 'Unauthorized'}, status=401)
            if not has_perms(admin, ['verified:view']):
                return Response({'detail': 'Forbidden'}, status=403)
            try:
                v = VerifiedProduct.objects.get(id=item_id)
                return Response({
                    'id': v.id,
                    'title': v.title,
                    'brand': v.brand,
                    'model': v.model,
                    'storage': v.storage,
                    'condition': v.condition,
                    'price': float(v.price),
                    'original_price': float(v.original_price) if v.original_price else None,
                    'status': v.status,
                    'description': v.description,
                    'sales_count': v.sales_count,
                    'view_count': v.view_count,
                    'created_at': v.created_at.isoformat(),
                    'updated_at': v.updated_at.isoformat()
                })
            except VerifiedProduct.DoesNotExist:
                return Response({'detail': '商品不存在'}, status=404)
        
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        search = request.query_params.get('search', '').strip()
        status_filter = request.query_params.get('status', '').strip()
        qs = VerifiedProduct.objects.all().order_by('-created_at')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(brand__icontains=search) | Q(model__icontains=search))
        if status_filter:
            qs = qs.filter(status=status_filter)
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{
            'id': v.id,
            'title': v.title,
            'brand': v.brand or '',
            'model': v.model or '',
            'storage': v.storage or '',
            'condition': v.condition,
            'price': float(v.price),
            'original_price': float(v.original_price) if v.original_price else None,
            'status': v.status,
            'sales_count': v.sales_count,
            'view_count': v.view_count,
            'created_at': v.created_at.isoformat()
        } for v in items]
        return Response({'results': data, 'count': total})
    def post(self, request, item_id=None, action=None):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            v = VerifiedProduct.objects.get(id=item_id)
            if action == 'publish':
                v.status = 'active'
            elif action == 'unpublish':
                v.status = 'removed'
            elif action == 'audit-approve':
                v.status = 'active'
                AdminAuditLog.objects.create(actor=admin, target_type='VerifiedProduct', target_id=v.id, action='approve', snapshot_json={'title': v.title})
            elif action == 'audit-reject':
                v.status = 'removed'
                AdminAuditLog.objects.create(actor=admin, target_type='VerifiedProduct', target_id=v.id, action='reject', snapshot_json={'title': v.title})
            v.save()
            return Response({'success': True})
        except VerifiedProduct.DoesNotExist:
            return Response({'success': False})

# 审核队列相关视图
@method_decorator(csrf_exempt, name='dispatch')
class AuditQueueView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['audit:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = AdminAuditQueueItem.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        return Response({'results': AdminAuditQueueItemSerializer(items, many=True).data, 'count': total})
    def post(self, request, qid, decision):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['audit:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            item = AdminAuditQueueItem.objects.get(id=qid)
            item.decision = decision
            item.status = 'completed'
            item.assigned_auditor = admin
            item.save()
            if decision == 'approve':
                item.product.status = 'active'
            else:
                item.product.status = 'removed'
            item.product.save()
            AdminAuditLog.objects.create(actor=admin, target_type='AdminAuditQueueItem', target_id=item.id, action=decision, snapshot_json={'product_id': item.product.id})
            return Response({'success': True})
        except AdminAuditQueueItem.DoesNotExist:
            return Response({'success': False})

# 审核日志相关视图
@method_decorator(csrf_exempt, name='dispatch')
class AuditLogsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['audit_log:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = AdminAuditLog.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{
            'id': log.id,
            'actor': log.actor.username if log.actor else None,
            'target_type': log.target_type,
            'target_id': log.target_id,
            'action': log.action,
            'snapshot_json': log.snapshot_json,
            'created_at': log.created_at.isoformat()
        } for log in items]
        return Response({'results': data, 'count': total})

# 管理员用户相关视图
@method_decorator(csrf_exempt, name='dispatch')
class UsersView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, uid=None):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['admin_user:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        if uid:
            try:
                u = AdminUser.objects.get(id=uid)
                return Response(AdminUserSerializer(u).data)
            except AdminUser.DoesNotExist:
                return Response({'detail': '用户不存在'}, status=404)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = AdminUser.objects.all().order_by('-id')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        return Response({'results': AdminUserSerializer(items, many=True).data, 'count': total})
    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['admin_user:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        role_name = request.data.get('role', 'auditor')
        email = request.data.get('email', '').strip()
        try:
            role = AdminRole.objects.get(name=role_name)
        except AdminRole.DoesNotExist:
            role = None
        u = AdminUser.objects.create(
            username=username,
            password_hash=make_password(password),
            role=role,
            email=email
        )
        return Response(AdminUserSerializer(u).data)
    def put(self, request, uid):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['admin_user:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            u = AdminUser.objects.get(id=uid)
            if 'role' in request.data:
                role_name = request.data.get('role')
                try:
                    u.role = AdminRole.objects.get(name=role_name)
                except AdminRole.DoesNotExist:
                    pass
            if 'email' in request.data:
                u.email = request.data.get('email', '').strip()
            if 'password' in request.data and request.data.get('password'):
                u.password_hash = make_password(request.data.get('password'))
            u.save()
            return Response(AdminUserSerializer(u).data)
        except AdminUser.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=404)
    def delete(self, request, uid):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['admin_user:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            u = AdminUser.objects.get(id=uid)
            u.delete()
            return Response({'success': True})
        except AdminUser.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=404)

# 角色相关视图
@method_decorator(csrf_exempt, name='dispatch')
class RolesView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['role:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        roles = AdminRole.objects.all()
        data = [{
            'id': r.id,
            'name': r.name,
            'description': r.description,
            'permissions': r.permissions or []
        } for r in roles]
        return Response({'results': data})
    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['role:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        perms_text = request.data.get('permsText', '').strip()
        perms = [p.strip() for p in perms_text.split(',') if p.strip()] if perms_text else []
        role, created = AdminRole.objects.get_or_create(name=name, defaults={'description': description, 'permissions': perms})
        if not created:
            role.description = description
            role.permissions = perms
            role.save()
        return Response({'success': True, 'id': role.id})

# 支付订单相关视图
@method_decorator(csrf_exempt, name='dispatch')
class PaymentOrdersView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['payment:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        status_filter = request.query_params.get('status', '')
        settlement_filter = request.query_params.get('settlement_status', '').strip()
        qs = Order.objects.select_related('product__seller', 'buyer').all().order_by('-created_at')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if settlement_filter:
            qs = qs.filter(settlement_status=settlement_filter)
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{
            'id': o.id,
            'product': o.product.title if o.product else '',
            'buyer': o.buyer.username if o.buyer else '',
            'seller': o.product.seller.username if getattr(o, 'product', None) and getattr(o.product, 'seller', None) else '',
            'total_price': float(o.total_price),
            'status': o.status,
            'settlement_status': getattr(o, 'settlement_status', 'pending'),
            'alipay_trade_no': getattr(o, 'alipay_trade_no', ''),
            'created_at': o.created_at.isoformat(),
            'seller_bound': (getattr(o.product.seller, 'profile', None) and bool(getattr(o.product.seller.profile, 'alipay_login_id', ''))) or False,
            'can_retry': ((getattr(o.product.seller, 'profile', None) and bool(getattr(o.product.seller.profile, 'alipay_login_id', ''))) and bool(getattr(o, 'alipay_trade_no', '')))
        } for o in items]
        return Response({'results': data, 'count': total})

@method_decorator(csrf_exempt, name='dispatch')
class PaymentOrderDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['payment:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            o = Order.objects.select_related(
                'buyer__profile',
                'product__seller__profile'
            ).prefetch_related('product__images').get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'order not found'}, status=404)

        data = OrderSerializer(o, context={'request': request}).data
        seller_profile = getattr(o.product.seller, 'profile', None)
        data['seller_profile'] = {
            'alipay_login_id': getattr(seller_profile, 'alipay_login_id', '') if seller_profile else '',
            'alipay_real_name': getattr(seller_profile, 'alipay_real_name', '') if seller_profile else ''
        }
        data['buyer_profile'] = {
            'phone': getattr(getattr(o.buyer, 'profile', None), 'phone', '') if hasattr(o.buyer, 'profile') else ''
        }
        return Response({'order': data})

@method_decorator(csrf_exempt, name='dispatch')
class PaymentOrderActionView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, order_id, action):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        try:
            o = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'success': False, 'detail': 'order not found'}, status=404)
        if action == 'query':
            if not has_perms(admin, ['payment:view']):
                return Response({'detail': 'Forbidden'}, status=403)
            # 使用支付宝查询
            alipay = AlipayClient()
            result = alipay.query_trade(f'normal_{order_id}')
            return Response({'success': True, 'result': result})
        elif action == 'refund':
            if not has_perms(admin, ['payment:write']):
                return Response({'detail': 'Forbidden'}, status=403)
            # TODO: 实现支付宝退款接口
            return Response({'success': False, 'detail': '退款功能暂未实现'}, status=501)
        elif action == 'ship':
            if not has_perms(admin, ['order:ship']):
                return Response({'detail': 'Forbidden'}, status=403)
            carrier = request.data.get('carrier', '').strip()
            tracking_number = request.data.get('tracking_number', '').strip()
            o.carrier = carrier
            o.tracking_number = tracking_number
            o.shipped_at = timezone.now()
            o.status = 'shipped'
            o.save()
            AdminAuditLog.objects.create(actor=admin, target_type='Order', target_id=o.id, action='ship', snapshot_json={'carrier': carrier, 'tracking_number': tracking_number})
            return Response({'success': True})
        return Response({'success': False}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentOrderSettlementView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, order_id, action=None):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['payment:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            o = Order.objects.select_related('product__seller__profile', 'buyer').get(id=order_id)
            seller_profile = getattr(o.product.seller, 'profile', None)
            seller_login_id = seller_profile.alipay_login_id if seller_profile else ''
            seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
            seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
            seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
            seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
            seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
            seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
            if action == 'history':
                logs = AdminAuditLog.objects.filter(target_type__in=['Order','VerifiedOrder'], target_id=o.id, action__in=['settlement_auto','settlement_retry','settlement_retry_transfer']).order_by('created_at')
                history = [{
                    'id': lg.id,
                    'action': lg.action,
                    'created_at': lg.created_at.isoformat(),
                    'snapshot': lg.snapshot_json or {}
                } for lg in logs]
                return Response({'id': o.id, 'history': history})
            # 最近一次分账重试审计日志
            last_log = AdminAuditLog.objects.filter(target_type='Order', target_id=o.id, action='settlement_retry').order_by('-id').first()
            last_log_info = None
            if last_log:
                last_log_info = {
                    'id': last_log.id,
                    'created_at': last_log.created_at.isoformat(),
                    'snapshot': last_log.snapshot_json or {}
                }
            can_retry = bool(seller_login_id) and bool(getattr(o, 'alipay_trade_no', ''))
            return Response({
                'id': o.id,
                'status': o.status,
                'alipay_trade_no': getattr(o, 'alipay_trade_no', ''),
                'settlement_status': getattr(o, 'settlement_status', 'pending'),
                'settled_at': o.settled_at.isoformat() if getattr(o, 'settled_at', None) else None,
                'seller_settle_amount': float(o.seller_settle_amount) if o.seller_settle_amount else None,
                'platform_commission_amount': float(o.platform_commission_amount) if o.platform_commission_amount else None,
                'settlement_method': getattr(o, 'settlement_method', ''),
                'settlement_account': (seller_user_id or seller_login_id),
                'transfer_order_id': getattr(o, 'transfer_order_id', ''),
                'seller': {
                    'id': o.product.seller.id,
                    'username': o.product.seller.username,
                    'alipay_login_id': seller_login_id,
                    'alipay_real_name': seller_profile.alipay_real_name if seller_profile else '',
                },
                'can_retry': can_retry,
                'last_settlement_log': last_log_info
            })
        except Order.DoesNotExist:
            return Response({'detail': 'order not found'}, status=404)
    
    def post(self, request, order_id, action):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['payment:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        if action != 'retry':
            return Response({'success': False, 'detail': 'unknown action'}, status=400)
        try:
            o = Order.objects.select_related('product__seller__profile').get(id=order_id)
            seller_profile = getattr(o.product.seller, 'profile', None)
            seller_login_id = seller_profile.alipay_login_id if seller_profile else ''
            seller_user_id = seller_profile.alipay_user_id if seller_profile else ''
            if not seller_login_id:
                return Response({'success': False, 'detail': '卖家未绑定支付宝登录账号'}, status=400)
            from app.secondhand_app.alipay_client import AlipayClient
            alipay = AlipayClient()
            trade_no = getattr(o, 'alipay_trade_no', '')
            if not trade_no:
                q = alipay.query_trade(f'normal_{o.id}')
                if q.get('success'):
                    trade_no = q.get('trade_no', '')
            if not trade_no:
                return Response({'success': False, 'detail': '无法获取支付宝交易号'}, status=400)
            from decimal import Decimal
            seller_amount = Decimal(str(o.product.price))
            commission_amount = Decimal(str(o.total_price)) - seller_amount
            if commission_amount < 0:
                commission_amount = Decimal('0.00')
            out_request_no = f'admin_retry_settle_{o.id}_{int(time.time())}'
            if seller_user_id:
                result = alipay.settle_order(
                    trade_no=trade_no,
                    out_request_no=out_request_no,
                    splits=[{
                        'trans_in': seller_user_id,
                        'trans_in_type': 'userId',
                        'amount': float(seller_amount),
                        'desc': '易淘分账-卖家(管理员重试)',
                        'royalty_scene': '平台服务费'
                    }]
                )
            else:
                result = alipay.settle_order(
                    trade_no=trade_no,
                    out_request_no=out_request_no,
                    splits=[{
                        'trans_in': seller_login_id,
                        'trans_in_type': 'loginName',
                        'amount': float(seller_amount),
                        'desc': '易淘分账-卖家(管理员重试)',
                        'royalty_scene': '平台服务费'
                    }]
                )
            if result.get('success'):
                o.settlement_status = 'settled'
                o.settled_at = timezone.now()
                o.settle_request_no = out_request_no
                o.seller_settle_amount = seller_amount
                o.platform_commission_amount = commission_amount
                o.settlement_method = 'ROYALTY'
                o.save()
                try:
                    from app.secondhand_app.models import Wallet, WalletTransaction
                    wallet, _ = Wallet.objects.get_or_create(user=o.product.seller)
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type='income',
                        amount=seller_amount,
                        balance_after=wallet.balance,
                        related_market_order=o,
                        alipay_account=(seller_user_id or seller_login_id),
                        alipay_name=(seller_profile.alipay_real_name if seller_profile else ''),
                        note=f'订单#{o.id} 分账完成，资金已存入支付宝: {(seller_user_id or seller_login_id)}'
                    )
                except Exception:
                    pass
                AdminAuditLog.objects.create(actor=admin, target_type='Order', target_id=o.id, action='settlement_retry', snapshot_json={'result': 'success'})
                return Response({'success': True})
            else:
                o.settlement_status = 'failed'
                o.settle_request_no = out_request_no
                o.save()
                AdminAuditLog.objects.create(actor=admin, target_type='Order', target_id=o.id, action='settlement_retry', snapshot_json={'result': 'failed', 'code': result.get('code'), 'msg': result.get('msg')})
                try:
                    from django.conf import settings
                    from django.utils import timezone
                    if getattr(settings, 'SETTLEMENT_FALLBACK_TO_TRANSFER', False):
                        out_biz_no = f'admin_settle_transfer_{o.id}_{int(time.time())}'
                        transfer_res = alipay.transfer_to_account(
                            out_biz_no=out_biz_no,
                            payee_account=(seller_login_id or seller_user_id),
                            amount=float(seller_amount),
                            payee_real_name=(seller_profile.alipay_real_name if seller_profile else None),
                            remark='易淘分账-管理员转账代结算'
                        )
                        if transfer_res.get('success'):
                            o.settlement_status = 'settled'
                            o.settled_at = timezone.now()
                            o.seller_settle_amount = seller_amount
                            o.platform_commission_amount = commission_amount
                            o.settlement_method = 'TRANSFER'
                            o.transfer_order_id = transfer_res.get('order_id','')
                            o.save()
                            try:
                                from app.secondhand_app.models import Wallet, WalletTransaction
                                wallet, _ = Wallet.objects.get_or_create(user=o.product.seller)
                                WalletTransaction.objects.create(
                                    wallet=wallet,
                                    transaction_type='income',
                                    amount=seller_amount,
                                    balance_after=wallet.balance,
                                    related_market_order=o,
                                    alipay_account=(seller_user_id or seller_login_id),
                                    alipay_name=(seller_profile.alipay_real_name if seller_profile else ''),
                                    alipay_order_id=transfer_res.get('order_id',''),
                                    note=f'订单#{o.id} 转账代结算成功，资金已存入支付宝: {(seller_user_id or seller_login_id)}'
                                )
                            except Exception:
                                pass
                            AdminAuditLog.objects.create(actor=admin, target_type='Order', target_id=o.id, action='settlement_retry_transfer', snapshot_json={'result': 'success'})
                            return Response({'success': True})
                except Exception:
                    pass
                return Response({'success': False, 'detail': result.get('msg', '分账失败')}, status=500)
        except Order.DoesNotExist:
            return Response({'detail': 'order not found'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class SettlementSummaryView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['payment:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        qs = Order.objects.all()
        counts = qs.values('settlement_status').annotate(cnt=Count('id'))
        totals = qs.aggregate(
            total_commission=Sum('platform_commission_amount'),
            total_seller_amount=Sum('seller_settle_amount')
        )
        return Response({
            'status_counts': {c['settlement_status'] or 'pending': c['cnt'] for c in counts},
            'total_commission': float(totals['total_commission'] or 0),
            'total_seller_amount': float(totals['total_seller_amount'] or 0)
        })

# 官方验订单相关视图
@method_decorator(csrf_exempt, name='dispatch')
class VerifiedOrdersAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, oid=None):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        
        if oid:
            try:
                vo = VerifiedOrder.objects.select_related('buyer', 'product').get(id=oid)
                return Response({
                    'id': vo.id,
                    'product': {
                        'id': vo.product.id,
                        'title': vo.product.title,
                        'brand': vo.product.brand,
                        'model': vo.product.model
                    },
                    'buyer': {
                        'id': vo.buyer.id,
                        'username': vo.buyer.username,
                        'email': vo.buyer.email
                    },
                    'total_price': float(vo.total_price),
                    'status': vo.status,
                    'carrier': vo.carrier,
                    'tracking_number': vo.tracking_number,
                    'shipped_at': vo.shipped_at.isoformat() if vo.shipped_at else None,
                    'delivered_at': vo.delivered_at.isoformat() if vo.delivered_at else None,
                    'shipping_address': vo.shipping_address,
                    'shipping_name': vo.shipping_name,
                    'shipping_phone': vo.shipping_phone,
                    'note': vo.note,
                    'created_at': vo.created_at.isoformat(),
                    'updated_at': vo.updated_at.isoformat()
                })
            except VerifiedOrder.DoesNotExist:
                return Response({'detail': '订单不存在'}, status=404)
        
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        status_filter = request.query_params.get('status', '')
        search = request.query_params.get('search', '').strip()
        qs = VerifiedOrder.objects.select_related('buyer', 'product').all().order_by('-created_at')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if search:
            qs = qs.filter(Q(product__title__icontains=search) | Q(buyer__username__icontains=search) | Q(id__icontains=search))
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{
            'id': vo.id,
            'product': {'id': vo.product.id, 'title': vo.product.title, 'brand': vo.product.brand, 'model': vo.product.model},
            'buyer': {'id': vo.buyer.id, 'username': vo.buyer.username},
            'total_price': float(vo.total_price),
            'status': vo.status,
            'carrier': vo.carrier,
            'tracking_number': vo.tracking_number,
            'created_at': vo.created_at.isoformat(),
        } for vo in items]
        return Response({'results': data, 'count': total})
    def post(self, request, oid, action):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['verified:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            vo = VerifiedOrder.objects.get(id=oid)
        except VerifiedOrder.DoesNotExist:
            return Response({'success': False, 'detail': 'order not found'}, status=404)
        if action == 'mark-paid':
            vo.status = 'paid'
        elif action == 'ship':
            carrier = request.data.get('carrier', '').strip()
            tracking_number = request.data.get('tracking_number', '').strip()
            note = request.data.get('note', '').strip()
            if not carrier or not tracking_number:
                return Response({'success': False, 'detail': '物流公司和运单号不能为空'}, status=400)
            vo.carrier = carrier
            vo.tracking_number = tracking_number
            vo.shipped_at = timezone.now()
            vo.status = 'shipped'
            if note:
                vo.note = (vo.note + '\n' + note).strip() if vo.note else note
        elif action == 'complete':
            vo.delivered_at = timezone.now()
            vo.status = 'completed'
        elif action == 'cancel':
            vo.status = 'cancelled'
        else:
            return Response({'success': False, 'detail': 'unknown action'}, status=400)
        vo.save()
        AdminAuditLog.objects.create(actor=admin, target_type='VerifiedOrder', target_id=vo.id, action=action, snapshot_json={'status': vo.status})
        return Response({'success': True})

# 店铺管理相关视图（简化版）
@method_decorator(csrf_exempt, name='dispatch')
class ShopsAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, sid=None):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['shop:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        if sid:
            try:
                s = Shop.objects.get(id=sid)
                return Response(ShopAdminSerializer(s).data)
            except Shop.DoesNotExist:
                return Response({'detail': '店铺不存在'}, status=404)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        search = request.query_params.get('search', '').strip()
        qs = Shop.objects.all().order_by('-created_at')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(owner__username__icontains=search))
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        return Response({'results': ShopAdminSerializer(items, many=True).data, 'count': total})
    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['shop:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        # 创建店铺逻辑
        return Response({'success': False, 'detail': 'Not implemented'})
    def put(self, request, sid):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['shop:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        # 更新店铺逻辑
        return Response({'success': False, 'detail': 'Not implemented'})
    def delete(self, request, sid):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['shop:delete']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            s = Shop.objects.get(id=sid)
            s.delete()
            return Response({'success': True})
        except Shop.DoesNotExist:
            return Response({'detail': '店铺不存在'}, status=404)

# 分类管理、商品管理、前端用户管理、消息管理、地址管理等视图（简化实现）
@method_decorator(csrf_exempt, name='dispatch')
class CategoriesAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, cid=None):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['category:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        if cid:
            try:
                c = Category.objects.get(id=cid)
                return Response({'id': c.id, 'name': c.name, 'description': c.description})
            except Category.DoesNotExist:
                return Response({'detail': '分类不存在'}, status=404)
        qs = Category.objects.all()
        data = [{'id': c.id, 'name': c.name, 'description': c.description} for c in qs]
        return Response({'results': data})
    def post(self, request):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['category:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        c = Category.objects.create(name=name, description=description)
        return Response({'id': c.id, 'name': c.name})
    def put(self, request, cid):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['category:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            c = Category.objects.get(id=cid)
            c.name = request.data.get('name', c.name)
            c.description = request.data.get('description', c.description)
            c.save()
            return Response({'id': c.id, 'name': c.name})
        except Category.DoesNotExist:
            return Response({'detail': '分类不存在'}, status=404)
    def delete(self, request, cid):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['category:delete']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            c = Category.objects.get(id=cid)
            c.delete()
            return Response({'success': True})
        except Category.DoesNotExist:
            return Response({'detail': '分类不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class ProductsAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, pid=None):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['product:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        if pid:
            try:
                p = Product.objects.get(id=pid)
                return Response({'id': p.id, 'title': p.title, 'status': p.status})
            except Product.DoesNotExist:
                return Response({'detail': '商品不存在'}, status=404)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = Product.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{'id': p.id, 'title': p.title, 'status': p.status} for p in items]
        return Response({'results': data, 'count': total})
    def post(self, request, pid, action):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['product:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            p = Product.objects.get(id=pid)
            if action == 'publish':
                p.status = 'active'
            elif action == 'unpublish':
                p.status = 'removed'
            elif action == 'mark-sold':
                p.status = 'sold'
            p.save()
            return Response({'success': True})
        except Product.DoesNotExist:
            return Response({'success': False})
    def delete(self, request, pid):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['product:delete']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            p = Product.objects.get(id=pid)
            p.delete()
            return Response({'success': True})
        except Product.DoesNotExist:
            return Response({'detail': '商品不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class UsersFrontendAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, uid=None):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['user:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        if uid:
            try:
                from django.contrib.auth.models import User
                u = User.objects.get(id=uid)
                return Response({'id': u.id, 'username': u.username, 'email': u.email, 'is_active': u.is_active, 'is_staff': u.is_staff})
            except User.DoesNotExist:
                return Response({'detail': '用户不存在'}, status=404)
        from django.contrib.auth.models import User
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = User.objects.all().order_by('-date_joined')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{'id': u.id, 'username': u.username, 'email': u.email, 'is_active': u.is_active, 'is_staff': u.is_staff, 'date_joined': u.date_joined.isoformat()} for u in items]
        return Response({'results': data, 'count': total})
    def post(self, request, uid):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['user:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        from django.contrib.auth.models import User
        try:
            u = User.objects.get(id=uid)
            action = request.data.get('action')
            if action == 'toggle_active':
                u.is_active = not u.is_active
            elif action == 'toggle_staff':
                u.is_staff = not u.is_staff
            u.save()
            return Response({'success': True})
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=404)
    def delete(self, request, uid):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['user:delete']):
            return Response({'detail': 'Forbidden'}, status=403)
        from django.contrib.auth.models import User
        try:
            u = User.objects.get(id=uid)
            u.delete()
            return Response({'success': True})
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class MessagesAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, mid=None):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['message:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = Message.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{'id': m.id, 'sender': m.sender.username if m.sender else '', 'receiver': m.receiver.username if m.receiver else '', 'content': m.content, 'is_read': m.is_read, 'created_at': m.created_at.isoformat()} for m in items]
        return Response({'results': data, 'count': total})
    def delete(self, request, mid):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['message:delete']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            m = Message.objects.get(id=mid)
            m.delete()
            return Response({'success': True})
        except Message.DoesNotExist:
            return Response({'detail': '消息不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class AddressesAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, aid=None):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['address:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = Address.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{'id': a.id, 'user': a.user.username if a.user else '', 'name': a.name, 'phone': a.phone, 'address': a.address, 'is_default': a.is_default, 'created_at': a.created_at.isoformat()} for a in items]
        return Response({'results': data, 'count': total})
    def delete(self, request, aid):
        admin = get_admin_from_request(request)
        if not admin or not has_perms(admin, ['address:delete']):
            return Response({'detail': 'Forbidden'}, status=403)
        try:
            a = Address.objects.get(id=aid)
            a.delete()
            return Response({'success': True})
        except Address.DoesNotExist:
            return Response({'detail': '地址不存在'}, status=404)
