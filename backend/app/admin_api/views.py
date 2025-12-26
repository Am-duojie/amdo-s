import time
import math
from functools import wraps
from datetime import datetime, timedelta
import json
from django.utils import timezone
from django.db.models import Count, Q, Sum, F, Value, FloatField, ExpressionWrapper
from django.db.models.functions import TruncDate, Coalesce
from django.db import IntegrityError
from django.db.utils import DatabaseError, OperationalError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from .models import (
    AdminUser, AdminRole, AdminInspectionReport, AdminAuditLog, AdminRefreshToken, AdminTokenBlacklist,
    RecycleDeviceTemplate, RecycleQuestionTemplate, RecycleQuestionOption
)
from .permissions import PERMISSIONS, validate_permissions
from app.secondhand_app.models import (
    RecycleOrder, VerifiedProduct, VerifiedOrder, Order, Category, Product, Message, Address,
    PlatformRecipient, VerifiedDevice, create_verified_product_from_device
)
from app.secondhand_app.alipay_client import AlipayClient
from .serializers import (
    AdminUserSerializer, RecycleOrderListSerializer, VerifiedProductListSerializer,
    VerifiedDeviceListSerializer, OfficialInventorySerializer,
    RecycleDeviceTemplateSerializer, RecycleDeviceTemplateListSerializer, RecycleQuestionTemplateSerializer, RecycleQuestionOptionSerializer
)
from app.secondhand_app.serializers import (
    OrderSerializer, VerifiedProductSerializer, VerifiedDeviceSerializer, MessageSerializer, UserSerializer,
    PlatformRecipientSerializer
)
from .jwt import encode as jwt_encode, decode as jwt_decode
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

def _get_official_verified_seller():
    """
    管理端创建“官方验库存/商品”时使用的默认卖家账号。
    - 避免 VerifiedDevice.seller 为空导致创建失败
    - 统一官方验的商品/库存归属
    """
    username = getattr(settings, 'OFFICIAL_VERIFIED_SELLER_USERNAME', 'verified_seller')
    email = getattr(settings, 'OFFICIAL_VERIFIED_SELLER_EMAIL', 'verified@example.com')
    User = get_user_model()
    seller, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_active': True}
    )
    if created:
        try:
            seller.set_unusable_password()
        except Exception:
            pass
        seller.save()
    return seller

def _get_service_user():
    """
    管理端客服对话使用的默认前台客服账号。
    - 便于统一客服身份
    - 支持通过 settings 覆盖账号
    """
    username = getattr(settings, 'SUPPORT_SERVICE_USERNAME', 'support_service')
    email = getattr(settings, 'SUPPORT_SERVICE_EMAIL', 'support@example.com')
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_active': True}
    )
    if created:
        try:
            user.set_unusable_password()
        except Exception:
            pass
        user.save()
    return user


def _get_platform_recipient():
    defaults = getattr(settings, 'PLATFORM_RECIPIENT_DEFAULT', {}) or {}
    try:
        obj = PlatformRecipient.objects.first()
        if obj:
            return obj
        return PlatformRecipient.objects.create(
            name=defaults.get('name', ''),
            phone=defaults.get('phone', ''),
            address=defaults.get('address', '')
        )
    except (OperationalError, DatabaseError):
        return None

def _get_product_cover(product):
    if not product:
        return ''
    try:
        primary = product.images.filter(is_primary=True).first()
        if primary and primary.image:
            return primary.image.url
    except Exception:
        pass
    try:
        first_img = product.images.first()
        if first_img and first_img.image:
            return first_img.image.url
    except Exception:
        pass
    return ''

def _get_verified_product_cover(product):
    if not product:
        return ''
    cover = getattr(product, 'cover_image', '') or ''
    if cover:
        return cover
    try:
        if product.detail_images:
            first = product.detail_images[0]
            if isinstance(first, dict):
                return first.get('image') or first.get('url') or ''
            if isinstance(first, str):
                return first
    except Exception:
        pass
    try:
        img = product.images.first()
        if img and img.image:
            return img.image.url
    except Exception:
        pass
    return ''

def _build_order_item_payload(item_type, order_obj):
    if item_type == 'secondhand':
        product = getattr(order_obj, 'product', None)
        return {
            'type': 'secondhand',
            'order_id': order_obj.id,
            'product_id': product.id if product else None,
            'title': product.title if product else f'订单#{order_obj.id}',
            'price': str(product.price) if product else str(order_obj.total_price),
            'cover': _get_product_cover(product)
        }
    if item_type == 'verified':
        product = getattr(order_obj, 'product', None)
        return {
            'type': 'verified',
            'order_id': order_obj.id,
            'verified_product_id': product.id if product else None,
            'title': product.title if product else f'官方验订单#{order_obj.id}',
            'price': str(product.price) if product else str(order_obj.total_price),
            'cover': _get_verified_product_cover(product)
        }
    if item_type == 'recycle':
        title = f"回收订单#{order_obj.id} {order_obj.brand} {order_obj.model}"
        price = order_obj.final_price or order_obj.estimated_price or ''
        return {
            'type': 'recycle',
            'recycle_order_id': order_obj.id,
            'title': title.strip(),
            'price': str(price) if price else '',
            'cover': ''
        }
    return {}

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
        logger.warning('[get_admin_from_request] Authorization header missing')
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


def require_admin(request, perms=None):
    admin = get_admin_from_request(request)
    if not admin:
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    if perms and not has_perms(admin, perms):
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    request.admin = admin
    return admin


def admin_required(perms=None, resolve_perms=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            perms_to_check = perms
            if resolve_perms:
                perms_to_check = resolve_perms(request, *args, **kwargs)
            admin = require_admin(request, perms_to_check)
            if isinstance(admin, Response):
                return admin
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def _audit(admin, action, target_type, target_id, snapshot=None):
    if not admin:
        return
    AdminAuditLog.objects.create(
        actor=admin,
        target_type=target_type,
        target_id=target_id,
        action=action,
        snapshot_json=snapshot or {}
    )

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
    
    @admin_required()
    def get(self, request):
        admin = request.admin
        user_data = AdminUserSerializer(admin).data
        return Response({'user': user_data})

@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required()
    def post(self, request):
        admin = request.admin
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
    
    @admin_required()
    def get(self, request):
        admin = request.admin
        perms = admin.role.permissions if admin.role else []
        return Response({'permissions': perms, 'all_permissions': PERMISSIONS})

@method_decorator(csrf_exempt, name='dispatch')
class MenusView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required()
    def get(self, request):
        admin = request.admin
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
    
    @admin_required(['dashboard:view'])
    def get(self, request):
        admin = request.admin
        today = timezone.now().date()
        gmv_qs = VerifiedOrder.objects.filter(created_at__date=today, status__in=['paid','completed']).values_list('total_price', flat=True)
        gmv_today = sum([float(x) for x in gmv_qs]) if gmv_qs else 0.0
        metrics = {
            'todayInspection': RecycleOrder.objects.filter(created_at__date=today).count(),
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
    
    @admin_required(['dashboard:view'])
    def get(self, request):
        admin = request.admin
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        include = (request.query_params.get('include') or 'trend,funnel,breakdown').strip()
        include_parts = {p.strip().lower() for p in include.split(',') if p.strip()}
        breakdown_type = (request.query_params.get('breakdown') or '').strip().lower()
        breakdown_gmv_scope = (request.query_params.get('breakdown_gmv_scope') or request.query_params.get('gmv_scope') or 'paid').strip().lower()
        exclude_cancelled_orders = (request.query_params.get('exclude_cancelled_orders') or request.query_params.get('exclude_cancelled') or 'true').strip().lower() in ['1', 'true', 'yes', 'y', 'on']
        include_cancelled_in_order_gmv = (request.query_params.get('include_cancelled_in_order_gmv') or 'false').strip().lower() in ['1', 'true', 'yes', 'y', 'on']

        recycle_statuses_raw = (request.query_params.get('recycle_statuses') or '').strip()
        verified_statuses_raw = (request.query_params.get('verified_statuses') or '').strip()
        secondhand_statuses_raw = (request.query_params.get('secondhand_statuses') or '').strip()

        def parse_csv(raw):
            if not raw:
                return []
            return [p.strip() for p in raw.split(',') if p.strip()]

        recycle_statuses = parse_csv(recycle_statuses_raw)
        verified_statuses = parse_csv(verified_statuses_raw)
        secondhand_statuses = parse_csv(secondhand_statuses_raw)
        try:
            top_n = int(request.query_params.get('top_n') or 10)
        except Exception:
            top_n = 10
        top_n = max(1, min(50, top_n))
        
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end = timezone.now().date()
            start = end - timedelta(days=30)

        # 保护：避免 end < start
        if end < start:
            start, end = end, start

        def date_iter(start_d, end_d):
            cur = start_d
            while cur <= end_d:
                yield cur
                cur = cur + timedelta(days=1)

        # ==================== Summary（保持向后兼容的 key） ====================
        paid_status = ['paid', 'completed']

        recycle_qs_base = RecycleOrder.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
        verified_qs_base = VerifiedOrder.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
        secondhand_qs_base = Order.objects.filter(created_at__date__gte=start, created_at__date__lte=end)

        # 状态过滤：影响趋势/汇总/维度拆分；漏斗始终展示全量状态分布
        recycle_qs_filtered = recycle_qs_base.filter(status__in=recycle_statuses) if recycle_statuses else recycle_qs_base
        verified_qs_filtered = verified_qs_base.filter(status__in=verified_statuses) if verified_statuses else verified_qs_base
        secondhand_qs_filtered = secondhand_qs_base.filter(status__in=secondhand_statuses) if secondhand_statuses else secondhand_qs_base

        # 订单数口径：默认排除取消（可通过 exclude_cancelled_orders=false 开启包含取消）
        recycle_qs = recycle_qs_filtered.exclude(status='cancelled') if exclude_cancelled_orders else recycle_qs_filtered
        verified_qs = verified_qs_filtered.exclude(status='cancelled') if exclude_cancelled_orders else verified_qs_filtered
        secondhand_qs = secondhand_qs_filtered.exclude(status='cancelled') if exclude_cancelled_orders else secondhand_qs_filtered

        # 下单GMV口径：默认不含取消；勾选 include_cancelled_in_order_gmv=true 时纳入取消单金额
        verified_qs_gmv_all = verified_qs_filtered if include_cancelled_in_order_gmv else verified_qs_filtered.exclude(status='cancelled')
        secondhand_qs_gmv_all = secondhand_qs_filtered if include_cancelled_in_order_gmv else secondhand_qs_filtered.exclude(status='cancelled')

        recycle_total = recycle_qs.count()
        recycle_total_all = recycle_qs_filtered.count()
        recycle_cancelled = recycle_qs_filtered.filter(status='cancelled').count()
        recycle_completed = recycle_qs.filter(status='completed').count()
        recycle_gmv_completed = recycle_qs_filtered.filter(status='completed').aggregate(
            gmv=Sum(
                ExpressionWrapper(
                    Coalesce(F('final_price'), Value(0)) + Coalesce(F('bonus'), Value(0)),
                    output_field=FloatField(),
                )
            )
        ).get('gmv') or 0
        verified_total = verified_qs.count()
        verified_gmv_paid = verified_qs.aggregate(
            gmv=Sum('total_price', filter=Q(status__in=paid_status))
        ).get('gmv') or 0
        verified_gmv_all = verified_qs_gmv_all.aggregate(gmv=Sum('total_price')).get('gmv') or 0
        secondhand_total = secondhand_qs.count()
        secondhand_total_all = secondhand_qs_filtered.count()
        secondhand_cancelled = secondhand_qs_filtered.filter(status='cancelled').count()
        secondhand_completed = secondhand_qs_filtered.filter(status='completed').count()
        secondhand_paid_total = secondhand_qs_filtered.filter(status__in=paid_status).count()
        secondhand_gmv_paid = secondhand_qs.aggregate(
            gmv=Sum('total_price', filter=Q(status__in=paid_status))
        ).get('gmv') or 0
        secondhand_gmv_all = secondhand_qs_gmv_all.aggregate(gmv=Sum('total_price')).get('gmv') or 0
        secondhand_settlement_failed = secondhand_qs.filter(settlement_status='failed').count()

        # ==================== Trend（按天聚合，给 BI 图表用） ====================
        trend = []
        if 'trend' in include_parts:
            trend_map = {
                d: {
                    'date': d.isoformat(),
                    'recycleOrders': 0,
                    'recycleCompleted': 0,
                    'recycleDisputes': 0,
                    'recycleGMVCompleted': 0.0,
                    'verifiedOrders': 0,
                    'verifiedGMVPaid': 0.0,
                    'verifiedGMVAll': 0.0,
                    'secondhandOrders': 0,
                    'secondhandGMVPaid': 0.0,
                    'secondhandGMVAll': 0.0,
                    'secondhandSettlementFailed': 0,
                }
                for d in date_iter(start, end)
            }

            for row in (
                recycle_qs.annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(
                    orders=Count('id'),
                    completed=Count('id', filter=Q(status='completed')),
                    disputes=Count('id', filter=Q(price_dispute=True)),
                    gmv_completed=Sum(
                        ExpressionWrapper(
                            Coalesce(F('final_price'), Value(0)) + Coalesce(F('bonus'), Value(0)),
                            output_field=FloatField(),
                        ),
                        filter=Q(status='completed'),
                    ),
                )
            ):
                day = row['day']
                if day in trend_map:
                    trend_map[day]['recycleOrders'] = int(row['orders'] or 0)
                    trend_map[day]['recycleCompleted'] = int(row['completed'] or 0)
                    trend_map[day]['recycleDisputes'] = int(row['disputes'] or 0)
                    trend_map[day]['recycleGMVCompleted'] = float(row['gmv_completed'] or 0)

            for row in (
                verified_qs.annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(
                    orders=Count('id'),
                    gmv_paid=Sum('total_price', filter=Q(status__in=paid_status)),
                )
            ):
                day = row['day']
                if day in trend_map:
                    trend_map[day]['verifiedOrders'] = int(row['orders'] or 0)
                    trend_map[day]['verifiedGMVPaid'] = float(row['gmv_paid'] or 0)

            for row in (
                verified_qs_gmv_all.annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(gmv_all=Sum('total_price'))
            ):
                day = row['day']
                if day in trend_map:
                    trend_map[day]['verifiedGMVAll'] = float(row['gmv_all'] or 0)

            for row in (
                secondhand_qs.annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(
                    orders=Count('id'),
                    gmv_paid=Sum('total_price', filter=Q(status__in=paid_status)),
                    settlement_failed=Count('id', filter=Q(settlement_status='failed')),
                )
            ):
                day = row['day']
                if day in trend_map:
                    trend_map[day]['secondhandOrders'] = int(row['orders'] or 0)
                    trend_map[day]['secondhandGMVPaid'] = float(row['gmv_paid'] or 0)
                    trend_map[day]['secondhandSettlementFailed'] = int(row['settlement_failed'] or 0)

            for row in (
                secondhand_qs_gmv_all.annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(gmv_all=Sum('total_price'))
            ):
                day = row['day']
                if day in trend_map:
                    trend_map[day]['secondhandGMVAll'] = float(row['gmv_all'] or 0)

            trend = [trend_map[d] for d in sorted(trend_map.keys())]

        # ==================== Funnel（订单状态漏斗） ====================
        funnels = None
        if 'funnel' in include_parts:
            def build_funnel(qs, choices):
                data = []
                for key, label in choices:
                    c = qs.filter(status=key).count()
                    data.append({'key': key, 'label': label, 'count': c})
                return data

            recycle_status_choices = list(getattr(RecycleOrder._meta.get_field('status'), 'choices', []))
            verified_status_choices = list(getattr(VerifiedOrder._meta.get_field('status'), 'choices', []))
            secondhand_status_choices = list(getattr(Order._meta.get_field('status'), 'choices', []))

            funnels = {
                'recycle': build_funnel(recycle_qs_base, recycle_status_choices),
                'verified': build_funnel(verified_qs_base, verified_status_choices),
                'secondhand': build_funnel(secondhand_qs_base, secondhand_status_choices),
            }

        # ==================== Recycle Flow（履约效率/异常） ====================
        recycle_flow = None
        if 'flow' in include_parts or 'efficiency' in include_parts:
            def percentile(sorted_vals, p):
                if not sorted_vals:
                    return None
                k = (len(sorted_vals) - 1) * p
                f = math.floor(k)
                c = math.ceil(k)
                if f == c:
                    return sorted_vals[int(k)]
                return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)

            def summarize_durations(values):
                if not values:
                    return None
                values_sorted = sorted(values)
                n = len(values_sorted)
                avg = sum(values_sorted) / n
                return {
                    'sample': n,
                    'avg_hours': round(avg, 2),
                    'median_hours': round(percentile(values_sorted, 0.5), 2),
                    'p90_hours': round(percentile(values_sorted, 0.9), 2),
                    'p95_hours': round(percentile(values_sorted, 0.95), 2),
                }

            created_to_shipped = []
            shipped_to_received = []
            received_to_inspected = []
            inspected_to_paid = []
            created_to_paid = []
            sla_rules = [
                {'key': 'created_to_shipped', 'label': '创建 → 寄出', 'threshold_hours': 72, 'owner': '用户寄出'},
                {'key': 'shipped_to_received', 'label': '寄出 → 收货', 'threshold_hours': 48, 'owner': '物流'},
                {'key': 'received_to_inspected', 'label': '收货 → 质检', 'threshold_hours': 24, 'owner': '质检'},
            ]
            sla_stats = {r['key']: {'label': r['label'], 'threshold_hours': r['threshold_hours'], 'overtime': 0, 'total': 0} for r in sla_rules}

            for o in recycle_qs_filtered.iterator():
                if o.shipped_at:
                    delta = o.shipped_at - o.created_at
                    if delta.total_seconds() >= 0:
                        hours = delta.total_seconds() / 3600.0
                        created_to_shipped.append(hours)
                        sla_stats['created_to_shipped']['total'] += 1
                        if hours > sla_stats['created_to_shipped']['threshold_hours']:
                            sla_stats['created_to_shipped']['overtime'] += 1
                if o.shipped_at and o.received_at:
                    delta = o.received_at - o.shipped_at
                    if delta.total_seconds() >= 0:
                        hours = delta.total_seconds() / 3600.0
                        shipped_to_received.append(hours)
                        sla_stats['shipped_to_received']['total'] += 1
                        if hours > sla_stats['shipped_to_received']['threshold_hours']:
                            sla_stats['shipped_to_received']['overtime'] += 1
                if o.received_at and o.inspected_at:
                    delta = o.inspected_at - o.received_at
                    if delta.total_seconds() >= 0:
                        hours = delta.total_seconds() / 3600.0
                        received_to_inspected.append(hours)
                        sla_stats['received_to_inspected']['total'] += 1
                        if hours > sla_stats['received_to_inspected']['threshold_hours']:
                            sla_stats['received_to_inspected']['overtime'] += 1
                if o.inspected_at and o.paid_at:
                    delta = o.paid_at - o.inspected_at
                    if delta.total_seconds() >= 0:
                        inspected_to_paid.append(delta.total_seconds() / 3600.0)
                if o.paid_at:
                    delta = o.paid_at - o.created_at
                    if delta.total_seconds() >= 0:
                        created_to_paid.append(delta.total_seconds() / 3600.0)

            recycle_total_all = recycle_qs_filtered.count()
            cancelled_count = recycle_qs_filtered.filter(status='cancelled').count()
            dispute_count = recycle_qs_filtered.filter(price_dispute=True).count()
            payment_failed_count = recycle_qs_filtered.filter(payment_status='failed').count()
            unconfirmed_count = recycle_qs_filtered.filter(status='inspected', final_price_confirmed=False).count()

            def safe_rate(num, denom):
                return (float(num) / float(denom)) if denom else 0.0

            recycle_flow = {
                'timings': {
                    'created_to_shipped': summarize_durations(created_to_shipped),
                    'shipped_to_received': summarize_durations(shipped_to_received),
                    'received_to_inspected': summarize_durations(received_to_inspected),
                    'inspected_to_paid': summarize_durations(inspected_to_paid),
                    'created_to_paid': summarize_durations(created_to_paid),
                },
                'sla': [
                    {
                        'key': key,
                        'label': stat['label'],
                        'threshold_hours': stat['threshold_hours'],
                        'overtime_count': stat['overtime'],
                        'total': stat['total'],
                        'overtime_rate': safe_rate(stat['overtime'], stat['total']),
                    }
                    for key, stat in sla_stats.items()
                ],
                'sla_attribution': [
                    {
                        'key': rule['key'],
                        'owner': rule['owner'],
                        'label': rule['label'],
                        'overtime_rate': safe_rate(sla_stats[rule['key']]['overtime'], sla_stats[rule['key']]['total']),
                        'overtime_count': sla_stats[rule['key']]['overtime'],
                        'total': sla_stats[rule['key']]['total'],
                    }
                    for rule in sla_rules
                ],
                'exceptions': {
                    'cancelled_rate': safe_rate(cancelled_count, recycle_total_all),
                    'dispute_rate': safe_rate(dispute_count, recycle_total_all),
                    'payment_failed_rate': safe_rate(payment_failed_count, recycle_total_all),
                    'unconfirmed_rate': safe_rate(unconfirmed_count, recycle_total_all),
                    'counts': {
                        'total': recycle_total_all,
                        'cancelled': cancelled_count,
                        'dispute': dispute_count,
                        'payment_failed': payment_failed_count,
                        'unconfirmed': unconfirmed_count,
                    },
                },
            }

        # ==================== Price Gap Distribution（估价偏差） ====================
        price_gap_distribution = None
        if 'gap' in include_parts or 'price_gap' in include_parts:
            bins = [
                {'label': '0-5%', 'min': 0.0, 'max': 0.05, 'mid': 0.025},
                {'label': '5-10%', 'min': 0.05, 'max': 0.10, 'mid': 0.075},
                {'label': '10-20%', 'min': 0.10, 'max': 0.20, 'mid': 0.15},
                {'label': '20-30%', 'min': 0.20, 'max': 0.30, 'mid': 0.25},
                {'label': '30%+', 'min': 0.30, 'max': None, 'mid': 0.40},
            ]
            counts = [0 for _ in bins]
            total = 0
            for o in recycle_qs_filtered.iterator():
                if o.estimated_price is None or o.final_price is None:
                    continue
                try:
                    estimated = float(o.estimated_price)
                    final = float(o.final_price)
                except Exception:
                    continue
                if estimated <= 0:
                    continue
                gap = abs(final - estimated) / estimated
                total += 1
                placed = False
                for idx, b in enumerate(bins):
                    lo = float(b['min'])
                    hi = b['max']
                    if hi is None:
                        if gap >= lo:
                            counts[idx] += 1
                            placed = True
                            break
                    else:
                        if gap >= lo and gap < float(hi):
                            counts[idx] += 1
                            placed = True
                            break
                if not placed:
                    counts[-1] += 1

            price_gap_distribution = {
                'total': total,
                'bins': [
                    {
                        'label': b['label'],
                        'count': counts[i],
                        'mid': b['mid'],
                    }
                    for i, b in enumerate(bins)
                ],
            }

        # ==================== Secondhand Price Distribution（易淘价格区间） ====================
        secondhand_price_distribution = None
        if 'secondhand' in include_parts or 'secondhand_price' in include_parts:
            price_bins = [
                {'label': '0-500', 'min': 0, 'max': 500},
                {'label': '500-1000', 'min': 500, 'max': 1000},
                {'label': '1000-2000', 'min': 1000, 'max': 2000},
                {'label': '2000-4000', 'min': 2000, 'max': 4000},
                {'label': '4000+', 'min': 4000, 'max': None},
            ]
            counts = [0 for _ in price_bins]
            total = 0
            qs = secondhand_qs_filtered.filter(status__in=paid_status)
            for o in qs.iterator():
                try:
                    price = float(o.total_price or 0)
                except Exception:
                    continue
                if price <= 0:
                    continue
                total += 1
                placed = False
                for idx, b in enumerate(price_bins):
                    lo = float(b['min'])
                    hi = b['max']
                    if hi is None:
                        if price >= lo:
                            counts[idx] += 1
                            placed = True
                            break
                    else:
                        if price >= lo and price < float(hi):
                            counts[idx] += 1
                            placed = True
                            break
                if not placed:
                    counts[-1] += 1

            secondhand_price_distribution = {
                'total': total,
                'scope': 'paid',
                'bins': [
                    {
                        'label': b['label'],
                        'count': counts[i],
                    }
                    for i, b in enumerate(price_bins)
                ],
            }

        # ==================== Breakdown（维度拆分 TopN） ====================
        breakdown = None
        if 'breakdown' in include_parts and breakdown_type:
            def norm_dim(v):
                s = (v or '').strip()
                return s if s else '未知'

            if breakdown_type == 'recycle_brand':
                rows = list(
                    recycle_qs.values('brand')
                    .annotate(
                        count=Count('id'),
                        completed=Count('id', filter=Q(status='completed')),
                        disputes=Count('id', filter=Q(price_dispute=True)),
                    )
                    .order_by('-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '回收 - 品牌 Top',
                    'defaultMetric': 'count',
                    'rows': [
                        {
                            'dim': norm_dim(r.get('brand')),
                            'count': int(r.get('count') or 0),
                            'completed': int(r.get('completed') or 0),
                            'disputes': int(r.get('disputes') or 0),
                        }
                        for r in rows
                    ],
                }
            elif breakdown_type == 'recycle_model':
                rows = list(
                    recycle_qs.values('brand', 'model')
                    .annotate(
                        count=Count('id'),
                        completed=Count('id', filter=Q(status='completed')),
                        disputes=Count('id', filter=Q(price_dispute=True)),
                    )
                    .order_by('-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '回收 - 机型 Top',
                    'defaultMetric': 'count',
                    'rows': [
                        {
                            'dim': f"{norm_dim(r.get('brand'))} {norm_dim(r.get('model'))}".strip(),
                            'count': int(r.get('count') or 0),
                            'completed': int(r.get('completed') or 0),
                            'disputes': int(r.get('disputes') or 0),
                        }
                        for r in rows
                    ],
                }
            elif breakdown_type == 'verified_brand':
                base = verified_qs_filtered
                count_agg = Count('id', filter=~Q(status='cancelled')) if exclude_cancelled_orders else Count('id')
                gmv_agg = (
                    Sum('total_price', filter=Q(status__in=paid_status))
                    if breakdown_gmv_scope == 'paid'
                    else (Sum('total_price') if include_cancelled_in_order_gmv else Sum('total_price', filter=~Q(status='cancelled')))
                )
                rows = list(
                    base.values('product__brand')
                    .annotate(count=count_agg, gmv=gmv_agg)
                    .order_by('-gmv', '-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '官方验订单 - 品牌 Top（按 GMV）',
                    'defaultMetric': 'gmv',
                    'rows': [
                        {
                            'dim': norm_dim(r.get('product__brand')),
                            'count': int(r.get('count') or 0),
                            'gmv': float(r.get('gmv') or 0),
                        }
                        for r in rows
                    ],
                }
            elif breakdown_type == 'verified_model':
                base = verified_qs_filtered
                count_agg = Count('id', filter=~Q(status='cancelled')) if exclude_cancelled_orders else Count('id')
                gmv_agg = (
                    Sum('total_price', filter=Q(status__in=paid_status))
                    if breakdown_gmv_scope == 'paid'
                    else (Sum('total_price') if include_cancelled_in_order_gmv else Sum('total_price', filter=~Q(status='cancelled')))
                )
                rows = list(
                    base.values('product__brand', 'product__model')
                    .annotate(count=count_agg, gmv=gmv_agg)
                    .order_by('-gmv', '-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '官方验订单 - 机型 Top（按 GMV）',
                    'defaultMetric': 'gmv',
                    'rows': [
                        {
                            'dim': f"{norm_dim(r.get('product__brand'))} {norm_dim(r.get('product__model'))}".strip(),
                            'count': int(r.get('count') or 0),
                            'gmv': float(r.get('gmv') or 0),
                        }
                        for r in rows
                    ],
                }
            elif breakdown_type == 'secondhand_category':
                base = secondhand_qs_filtered
                count_agg = Count('id', filter=~Q(status='cancelled')) if exclude_cancelled_orders else Count('id')
                gmv_agg = (
                    Sum('total_price', filter=Q(status__in=paid_status))
                    if breakdown_gmv_scope == 'paid'
                    else (Sum('total_price') if include_cancelled_in_order_gmv else Sum('total_price', filter=~Q(status='cancelled')))
                )
                rows = list(
                    base.values('product__category__name')
                    .annotate(count=count_agg, gmv=gmv_agg)
                    .order_by('-gmv', '-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '易淘订单 - 分类 Top（按 GMV）',
                    'defaultMetric': 'gmv',
                    'rows': [
                        {
                            'dim': norm_dim(r.get('product__category__name')),
                            'count': int(r.get('count') or 0),
                            'gmv': float(r.get('gmv') or 0),
                        }
                        for r in rows
                    ],
                }
            elif breakdown_type == 'secondhand_shop':
                base = secondhand_qs_filtered
                count_agg = Count('id', filter=~Q(status='cancelled')) if exclude_cancelled_orders else Count('id')
                gmv_agg = (
                    Sum('total_price', filter=Q(status__in=paid_status))
                    if breakdown_gmv_scope == 'paid'
                    else (Sum('total_price') if include_cancelled_in_order_gmv else Sum('total_price', filter=~Q(status='cancelled')))
                )
                rows = list(
                    base.values('product__seller__username')
                    .annotate(count=count_agg, gmv=gmv_agg)
                    .order_by('-gmv', '-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '易淘订单 - 卖家 Top（按 GMV）',
                    'defaultMetric': 'gmv',
                    'rows': [
                        {
                            'dim': norm_dim(r.get('product__seller__username')),
                            'count': int(r.get('count') or 0),
                            'gmv': float(r.get('gmv') or 0),
                        }
                        for r in rows
                    ],
                }
            elif breakdown_type == 'secondhand_product':
                base = secondhand_qs_filtered
                count_agg = Count('id', filter=~Q(status='cancelled')) if exclude_cancelled_orders else Count('id')
                gmv_agg = (
                    Sum('total_price', filter=Q(status__in=paid_status))
                    if breakdown_gmv_scope == 'paid'
                    else (Sum('total_price') if include_cancelled_in_order_gmv else Sum('total_price', filter=~Q(status='cancelled')))
                )
                rows = list(
                    base.values('product__title')
                    .annotate(count=count_agg, gmv=gmv_agg)
                    .order_by('-gmv', '-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '易淘订单 - 商品 Top（按 GMV）',
                    'defaultMetric': 'gmv',
                    'rows': [
                        {
                            'dim': norm_dim(r.get('product__title')),
                            'count': int(r.get('count') or 0),
                            'gmv': float(r.get('gmv') or 0),
                        }
                        for r in rows
                    ],
                }
            elif breakdown_type == 'inventory_brand':
                inv_qs = VerifiedDevice.objects.all()
                rows = list(
                    inv_qs.values('brand')
                    .annotate(
                        count=Count('id'),
                        ready=Count('id', filter=Q(status='ready')),
                        listed=Count('id', filter=Q(status='listed')),
                        locked=Count('id', filter=Q(status='locked')),
                        sold=Count('id', filter=Q(status='sold')),
                    )
                    .order_by('-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '库存 - 品牌 Top',
                    'defaultMetric': 'count',
                    'rows': [
                        {
                            'dim': norm_dim(r.get('brand')),
                            'count': int(r.get('count') or 0),
                            'ready': int(r.get('ready') or 0),
                            'listed': int(r.get('listed') or 0),
                            'locked': int(r.get('locked') or 0),
                            'sold': int(r.get('sold') or 0),
                        }
                        for r in rows
                    ],
                }
            elif breakdown_type == 'inventory_model':
                inv_qs = VerifiedDevice.objects.all()
                rows = list(
                    inv_qs.values('brand', 'model')
                    .annotate(
                        count=Count('id'),
                        ready=Count('id', filter=Q(status='ready')),
                        listed=Count('id', filter=Q(status='listed')),
                        locked=Count('id', filter=Q(status='locked')),
                        sold=Count('id', filter=Q(status='sold')),
                    )
                    .order_by('-count')[:top_n]
                )
                breakdown = {
                    'type': breakdown_type,
                    'label': '库存 - 机型 Top',
                    'defaultMetric': 'count',
                    'rows': [
                        {
                            'dim': f"{norm_dim(r.get('brand'))} {norm_dim(r.get('model'))}".strip(),
                            'count': int(r.get('count') or 0),
                            'ready': int(r.get('ready') or 0),
                            'listed': int(r.get('listed') or 0),
                            'locked': int(r.get('locked') or 0),
                            'sold': int(r.get('sold') or 0),
                        }
                        for r in rows
                    ],
                }

        return Response({
            # 口径/范围
            'startDate': start.isoformat(),
            'endDate': end.isoformat(),
            'days': len(trend),
            'methodology': {
                'timeField': 'created_at',
                'excludeCancelledOrders': exclude_cancelled_orders,
                'includeCancelledInOrderGMV': include_cancelled_in_order_gmv,
                'gmvPaidStatuses': paid_status,
            'note': '趋势/汇总/维度拆分支持状态过滤；漏斗始终展示全量状态分布（便于解释转化与取消）。',
            'filters': {
                'recycle_statuses': recycle_statuses,
                'verified_statuses': verified_statuses,
                'secondhand_statuses': secondhand_statuses,
            },
            'breakdownGMVScope': breakdown_gmv_scope,
            'flowScope': '回收履约效率/异常基于回收订单筛选结果（recycle_statuses）统计，时间字段为 created_at/shipped_at/received_at/inspected_at/paid_at。',
        },

            # 旧字段（Statistics.vue 已在使用）
            'recycleOrdersTotal': recycle_total,
            'recycleOrdersTotalAll': recycle_total_all,
            'recycleCancelledTotal': recycle_cancelled,
            'recycleCompleted': recycle_completed,
            'recycleGMVCompleted': float(recycle_gmv_completed),
            'verifiedOrdersTotal': verified_total,
            'totalGMV': float(verified_gmv_paid),

            # 新增字段（BI）
            'verifiedGMV': float(verified_gmv_paid),
            'verifiedGMVPaid': float(verified_gmv_paid),
            'verifiedGMVAll': float(verified_gmv_all),
            'secondhandOrdersTotal': secondhand_total,
            'secondhandOrdersTotalAll': secondhand_total_all,
            'secondhandCancelledTotal': secondhand_cancelled,
            'secondhandCompleted': secondhand_completed,
            'secondhandPaidTotal': secondhand_paid_total,
            'secondhandGMV': float(secondhand_gmv_paid),
            'secondhandGMVPaid': float(secondhand_gmv_paid),
            'secondhandGMVAll': float(secondhand_gmv_all),
            'secondhandSettlementFailed': secondhand_settlement_failed,
            'totalGMVAll': float(verified_gmv_paid) + float(secondhand_gmv_paid),
            'totalGMVAllPaid': float(verified_gmv_paid) + float(secondhand_gmv_paid),
            'totalGMVAllAll': float(verified_gmv_all) + float(secondhand_gmv_all),

            'trend': trend,
            'funnels': funnels,
            'recycle_flow': recycle_flow,
            'price_gap_distribution': price_gap_distribution,
            'secondhand_price_distribution': secondhand_price_distribution,
            'breakdown': breakdown,
        })

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrdersView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['inspection:view'])
    def get(self, request):
        admin = request.admin
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
            'paid_at': o.paid_at.isoformat() if o.paid_at else None,
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
            'price_dispute_reason': o.price_dispute_reason or '',
            'final_price_confirmed': bool(getattr(o, 'final_price_confirmed', False)),
            'created_at': o.created_at.isoformat(),
            'updated_at': o.updated_at.isoformat()
        } for o in items]
        return Response({'results': data, 'count': total})

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderDetailView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['inspection:view'])
    def get(self, request, order_id):
        admin = request.admin
        try:
            o = RecycleOrder.objects.select_related('template').get(id=order_id)
        except RecycleOrder.DoesNotExist:
            return Response({'success': False})
        rep = o.admin_reports.order_by('-id').first()
        profile = getattr(o.user, 'profile', None)
        if rep:
            report_data = {
                'check_items': rep.check_items if rep.check_items is not None else {},
                'remarks': rep.remarks or '',
                'evidence': rep.evidence or [],
                'overall_result': rep.overall_result or '',
                'recommend_price': float(rep.recommend_price) if rep.recommend_price is not None else None,
                'score': float(rep.score) if rep.score is not None else None,
                'template_name': rep.template_name or '',
                'template_version': rep.template_version or '',
                'created_at': rep.created_at.isoformat() if rep.created_at else None
            }
        else:
            report_data = {
                'check_items': {},
                'remarks': '',
                'evidence': [],
                'overall_result': '',
                'recommend_price': None,
                'score': None,
                'template_name': '',
                'template_version': '',
                'created_at': None
            }
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
            'selected_storage': getattr(o, 'selected_storage', '') or '',
            'selected_color': getattr(o, 'selected_color', '') or '',
            'selected_ram': getattr(o, 'selected_ram', '') or '',
            'selected_version': getattr(o, 'selected_version', '') or '',
            'template_info': {
                'id': o.template.id,
                'device_type': o.template.device_type,
                'brand': o.template.brand,
                'model': o.template.model,
                'series': o.template.series or '',
            } if getattr(o, 'template', None) else None,
            'questionnaire_answers': o.questionnaire_answers or {},
            'condition': o.condition,
            'estimated_price': float(o.estimated_price) if o.estimated_price else None,
            'final_price': float(o.final_price) if o.final_price else None,
            'bonus': float(o.bonus) if o.bonus else 0,
            'total_price': float(o.final_price + o.bonus) if o.final_price else None,
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
            # 价格确认
            'final_price_confirmed': o.final_price_confirmed,
            # 时间信息
            'created_at': o.created_at.isoformat(),
            'updated_at': o.updated_at.isoformat(),
            # 质检报告
            'report': report_data,
        }})
    @admin_required(['inspection:write'])
    def put(self, request, order_id):
        admin = request.admin
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
            if status_val == 'received' and not o.received_at:
                o.received_at = timezone.now()
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
    @admin_required(['inspection:write'])
    def post(self, request, order_id):
        admin = request.admin
        items = request.data.get('check_items', {})
        remarks = request.data.get('remarks', '')
        evidence = request.data.get('evidence', [])
        overall_result = (request.data.get('overall_result') or 'passed').strip() or 'passed'
        template_name = (request.data.get('template_name') or 'default').strip() or 'default'
        template_version = (request.data.get('template_version') or 'v1').strip() or 'v1'
        recommend_price = request.data.get('recommend_price')
        score = request.data.get('score')
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except Exception:
                return Response({'success': False, 'detail': '检测项目JSON解析失败'}, status=400)
        # 支持对象格式（旧格式）和数组格式（新格式：66项检测）
        if not isinstance(items, (dict, list)):
            return Response({'success': False, 'detail': '检测项目必须为对象或数组'}, status=400)
        if isinstance(evidence, str):
            try:
                evidence = json.loads(evidence)
            except Exception:
                return Response({'success': False, 'detail': '佐证JSON解析失败'}, status=400)
        if evidence is None:
            evidence = []
        if not isinstance(evidence, (list, tuple)):
            return Response({'success': False, 'detail': '佐证必须为数组/列表'}, status=400)
        try:
            recommend_price = float(recommend_price) if recommend_price not in [None, ''] else None
        except (TypeError, ValueError):
            return Response({'success': False, 'detail': '推荐价格格式错误'}, status=400)
        try:
            score = float(score) if score not in [None, ''] else None
        except (TypeError, ValueError):
            return Response({'success': False, 'detail': '评分格式错误'}, status=400)
        try:
            o = RecycleOrder.objects.get(id=order_id)
        except RecycleOrder.DoesNotExist:
            return Response({'success': False})
        if o.status in ['cancelled']:
            return Response({'success': False, 'detail': '订单已取消，无法提交质检报告'}, status=400)
        if isinstance(items, dict) and not items:
            return Response({'success': False, 'detail': '质检报告不能为空'}, status=400)
        if isinstance(items, list) and len(items) == 0:
            return Response({'success': False, 'detail': '质检报告不能为空'}, status=400)
        AdminInspectionReport.objects.create(
            order=o,
            check_items=items,
            remarks=remarks,
            evidence=evidence,
            overall_result=overall_result,
            recommend_price=recommend_price,
            score=score,
            template_name=template_name,
            template_version=template_version
        )
        # 更新状态和质检时间
        if o.status in ['shipped', 'received']:
            o.status = 'inspected'
            if not o.inspected_at:
                o.inspected_at = timezone.now()
            # 如果没有收到时间，设置收到时间
            if not o.received_at:
                o.received_at = timezone.now()
            o.save()
        AdminAuditLog.objects.create(
            actor=admin,
            target_type='RecycleOrder',
            target_id=o.id,
            action='inspection_report',
            snapshot_json={
                'status': o.status,
                'check_items_count': len(items),
                'overall_result': overall_result,
                'recommend_price': recommend_price,
                'score': score,
                'template_name': template_name,
                'template_version': template_version,
                'evidence_count': len(evidence)
            }
        )
        return Response({'success': True})

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderLogisticsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['inspection:write'])
    def post(self, request, order_id):
        admin = request.admin
        
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
                if o.status not in ['pending', 'shipped']:
                    return Response({'success': False, 'detail': '当前状态不允许填写物流信息'}, status=400)
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
                # 平台确认收货
                if o.status != 'shipped':
                    return Response({'success': False, 'detail': f'订单状态为 {o.get_status_display()}，只有"已寄出"状态的订单才能确认收货'}, status=400)
                o.received_at = timezone.now()
                o.status = 'received'  # 更新为已收货状态
                AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='logistics_receive', snapshot_json={'received_at': o.received_at.isoformat(), 'new_status': 'received'})
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
    # Disable default auth; handled manually
    authentication_classes = []
    permission_classes = []

    @admin_required(['inspection:write'])
    def put(self, request, order_id):
        import logging
        logger = logging.getLogger(__name__)
        logger.info('[InspectionOrderPriceView] received PUT request')
        admin = request.admin

        price_type = request.data.get('price_type', 'final')
        estimated_price = request.data.get('estimated_price')
        final_price = request.data.get('final_price')
        bonus = request.data.get('bonus', 0)

        try:
            o = RecycleOrder.objects.get(id=order_id)
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': 'Order not found'}, status=404)

        if price_type == 'estimated' and estimated_price is not None:
            try:
                estimated_price = float(estimated_price)
                if estimated_price <= 0:
                    return Response({'success': False, 'detail': 'Price must be greater than 0'}, status=400)
                o.estimated_price = estimated_price
                if o.status == 'pending':
                    o.status = 'shipped'
                if o.price_dispute:
                    o.price_dispute = False
                    o.price_dispute_reason = ''
            except (ValueError, TypeError):
                return Response({'success': False, 'detail': 'Invalid price format'}, status=400)
        elif price_type == 'final' and final_price is not None:
            try:
                if o.payment_status == 'paid':
                    return Response({'success': False, 'detail': 'Order already paid'}, status=400)
                if o.status not in ['inspected', 'completed']:
                    return Response(
                        {'success': False, 'detail': f'Invalid status for final price: {o.status}'},
                        status=400
                    )
                final_price = float(final_price)
                if final_price <= 0:
                    return Response({'success': False, 'detail': 'Price must be greater than 0'}, status=400)
                bonus = float(bonus) if bonus else 0
                o.final_price = final_price
                o.bonus = bonus
                o.final_price_confirmed = False
                o.status = 'inspected'
                if o.price_dispute:
                    o.price_dispute = False
                    o.price_dispute_reason = ''
            except (ValueError, TypeError):
                return Response({'success': False, 'detail': 'Invalid price format'}, status=400)
        else:
            return Response({'success': False, 'detail': 'Invalid price parameters'}, status=400)

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

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderPaymentView(APIView):
    # Disable default auth; handled manually
    authentication_classes = []
    permission_classes = []

    @admin_required(['inspection:write'])
    def post(self, request, order_id):
        admin = request.admin
        note = (request.data.get('note') or '').strip()
        payment_method = (request.data.get('payment_method') or '').strip()
        if not payment_method:
            payment_method = 'transfer'
        payment_account = (request.data.get('payment_account') or '').strip()

        try:
            o = RecycleOrder.objects.get(id=order_id)
            if not o.final_price:
                return Response({'success': False, 'detail': 'Final price not set'}, status=400)
            if getattr(o, 'price_dispute', False):
                return Response({'success': False, 'detail': 'Price dispute pending'}, status=400)
            if not getattr(o, 'final_price_confirmed', False):
                return Response({'success': False, 'detail': 'Final price not confirmed'}, status=400)

            if o.status != 'completed':
                return Response({
                    'success': False,
                    'detail': f'Order must be completed before payment. Current: {o.status}',
                    'current_status': o.status,
                    'required_status': ['completed']
                }, status=400)

            if o.payment_status == 'paid':
                return Response({
                    'success': False,
                    'detail': 'Order already paid',
                    'payment_status': o.payment_status
                }, status=400)

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
                    'payment_account': payment_account or None,
                }
            )

            if payment_method and payment_method != 'transfer':
                return Response({'success': False, 'detail': 'Unsupported payment method'}, status=400)

            if payment_method == 'transfer':
                if not payment_account:
                    profile = getattr(o.user, 'profile', None)
                    payment_account = getattr(profile, 'alipay_login_id', '') if profile else ''
                if not payment_account:
                    return Response({'success': False, 'detail': 'Payee account required'}, status=400)
                o.payment_status = 'paid'
                o.paid_at = timezone.now()
                o.payment_method = 'transfer'
                o.payment_account = payment_account or None
                parts = []
                if note:
                    parts.append(note)
                parts.append(f'Transfer amount: ?{total_amount}')
                if payment_account:
                    parts.append(f'Payee: {payment_account}')
                o.payment_note = '\n'.join(parts)
                o.save()
                return Response({'success': True, 'message': 'Transfer completed', 'amount': total_amount})

            return Response({'success': False, 'detail': 'Unsupported payment method'}, status=400)
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': 'Order not found'}, status=404)

# 已移除“从回收订单侧直接发布官方验商品/入库”的接口：
# 官方验库存改为在“官方验库存管理”中手动选择来源回收单入库，再从库存设备上架生成商品。
@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrdersBatchUpdateView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['inspection:write'])
    def post(self, request):
        admin = request.admin
        ids = request.data.get('ids', [])
        new_status = request.data.get('status', '')
        if not ids or not new_status:
            return Response({'success': False, 'detail': '参数不完整'}, status=400)
        try:
            qs = RecycleOrder.objects.filter(id__in=ids)
            if new_status == 'received':
                count = qs.update(status=new_status, received_at=timezone.now())
            else:
                count = qs.update(status=new_status)
            AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=0, action='batch_update', snapshot_json={'ids': ids, 'status': new_status, 'count': count})
            return Response({'success': True, 'count': count})
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=500)

# ---------------- 上传接口 ----------------
@method_decorator(csrf_exempt, name='dispatch')
class AdminUploadImageView(APIView):
    authentication_classes = []
    permission_classes = []
    @admin_required()
    def post(self, request):
        admin = request.admin
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
    @admin_required()
    def post(self, request):
        admin = request.admin
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
    @admin_required(['verified:view', 'verified:write'])
    def get(self, request):
        admin = request.admin
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        status_q = request.query_params.get('status')
        search = request.query_params.get('search')
        qs = VerifiedProduct.objects.all().prefetch_related('devices').order_by('-created_at')
        if status_q:
            qs = qs.filter(status=status_q)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(brand__icontains=search) | Q(model__icontains=search))
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        return Response({'results': VerifiedProductListSerializer(items, many=True).data, 'count': total})

    @admin_required(['verified:write'])
    def post(self, request):
        return Response({'detail': '官方验商品仅允许由库存设备上架生成'}, status=403)

@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedProductDetailView(APIView):
    authentication_classes = []
    permission_classes = []
    def get_object(self, pk):
        return VerifiedProduct.objects.get(id=pk)

    @admin_required(['verified:view', 'verified:write'])
    def get(self, request, pk):
        admin = request.admin
        try:
            obj = self.get_object(pk)
            data = VerifiedProductSerializer(obj, context={'request': request}).data
            device = VerifiedDevice.objects.filter(linked_product=obj).first()
            data['linked_device'] = None
            if device:
                data['linked_device'] = {
                    'id': device.id,
                    'sn': device.sn,
                    'brand': device.brand,
                    'model': device.model,
                    'storage': device.storage,
                    'status': device.status,
                }
            return Response(data)
        except VerifiedProduct.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)

    @admin_required(['verified:write'])
    def put(self, request, pk):
        admin = request.admin
        try:
            obj = self.get_object(pk)
        except VerifiedProduct.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)

        # 官方验商品的“展示字段”以库存设备为准：此处若关联了库存设备，则把编辑内容回写到库存，再由库存同步回商品。
        device = VerifiedDevice.objects.filter(linked_product=obj).first()
        if device:
            data = request.data or {}
            device_patch = {}
            # 规格/展示字段
            for k in [
                'brand', 'model', 'storage', 'ram', 'version', 'color', 'condition',
                'cover_image', 'detail_images', 'inspection_reports',
                'inspection_result', 'inspection_date', 'inspection_staff', 'inspection_note',
                'battery_health', 'screen_condition', 'repair_history',
                'location', 'category_id', 'template_id'
            ]:
                if k in data:
                    device_patch[k] = data.get(k)
            # 商品描述 -> 库存上架描述
            if 'description' in data:
                device_patch['listing_description'] = data.get('description') or ''

            if device_patch:
                dev_ser = VerifiedDeviceSerializer(device, data=device_patch, partial=True, context={'request': request})
                if not dev_ser.is_valid():
                    return Response(dev_ser.errors, status=400)
                device = dev_ser.save()

            desired_status = data.get('status', getattr(obj, 'status', 'draft'))
            price_override = data.get('price', getattr(obj, 'price', None))
            original_price_override = data.get('original_price', getattr(obj, 'original_price', None))

            try:
                product = create_verified_product_from_device(
                    device,
                    status=desired_status,
                    price_override=price_override,
                    original_price_override=original_price_override,
                    enforce_publish_requirements=False,
                )
            except ValueError as e:
                return Response({'detail': str(e)}, status=400)

            # 仅保留“非库存来源”的字段由本接口直接更新
            meta_patch = {}
            for k in ['stock', 'tags', 'removed_reason']:
                if k in data:
                    meta_patch[k] = data.get(k)
            if meta_patch:
                meta_ser = VerifiedProductSerializer(product, data=meta_patch, partial=True, context={'request': request})
                if meta_ser.is_valid():
                    product = meta_ser.save()
                else:
                    return Response(meta_ser.errors, status=400)

            return Response(VerifiedProductSerializer(product, context={'request': request}).data)

        serializer = VerifiedProductSerializer(obj, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            obj = serializer.save()
            return Response(VerifiedProductSerializer(obj, context={'request': request}).data)
        return Response(serializer.errors, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedProductPublishView(APIView):
    authentication_classes = []
    permission_classes = []
    @admin_required(['verified:write'])
    def post(self, request, pk):
        admin = request.admin
        try:
            obj = VerifiedProduct.objects.get(id=pk)
        except VerifiedProduct.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        if obj.stock <= 0:
            return Response({'detail': '库存为0，无法上架'}, status=400)
        device = VerifiedDevice.objects.filter(linked_product=obj).first()
        if not device:
            return Response({'detail': '官方验商品仅允许由库存设备上架生成'}, status=400)
        try:
            product = create_verified_product_from_device(
                device,
                status='active',
                price_override=obj.price,
                original_price_override=obj.original_price,
            )
            return Response(VerifiedProductSerializer(product, context={'request': request}).data)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedProductUnpublishView(APIView):
    authentication_classes = []
    permission_classes = []
    @admin_required(['verified:write'])
    def post(self, request, pk):
        admin = request.admin
        try:
            obj = VerifiedProduct.objects.get(id=pk)
        except VerifiedProduct.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        obj.status = 'removed'
        obj.removed_reason = request.data.get('reason', '')
        obj.save()
        return Response(VerifiedProductSerializer(obj, context={'request': request}).data)


@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedDeviceView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:read', 'verified:write'])
    def get(self, request):
        admin = request.admin
        qs = VerifiedDevice.objects.select_related('template').all().order_by('-created_at')
        search = request.GET.get('search') or request.GET.get('sn')
        status_filter = request.GET.get('status')
        if search:
            qs = qs.filter(
                Q(sn__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search)
            )
        if status_filter:
            qs = qs.filter(status=status_filter)
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        total = qs.count()
        serializer = VerifiedDeviceListSerializer(qs[start:end], many=True)
        return Response({'count': total, 'results': serializer.data})

    @admin_required(['verified:write'])
    def post(self, request):
        return Response({'detail': '官方验库存设备已禁止手动新增，请从回收订单入库。'}, status=403)

@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedDeviceAvailableRecycleOrdersView(APIView):
    """
    提供“已完成回收单”列表，用于在官方验库存新增时选择来源订单。
    仅返回尚未被导入为 VerifiedDevice 的订单。
    """
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:write', 'inspection:view'])
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        search = (request.query_params.get('search') or '').strip()

        qs = (
            RecycleOrder.objects
            .select_related('user')
            .filter(status='completed')
            .filter(final_price_confirmed=True)
            .filter(verified_devices__isnull=True)
            .order_by('-created_at')
        )
        if search:
            qs = qs.filter(
                Q(id__icontains=search) |
                Q(user__username__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search)
            )

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        results = []
        for o in items:
            results.append({
                'id': o.id,
                'user': {'id': o.user.id, 'username': o.user.username},
                'brand': o.brand,
                'model': o.model,
                'storage': o.storage or '',
                'condition': o.condition,
                'final_price': float(o.final_price) if o.final_price else None,
                'bonus': float(o.bonus) if o.bonus else 0,
                'total_price': float(o.final_price + o.bonus) if o.final_price else None,
                'created_at': o.created_at.isoformat(),
            })

        return Response({'count': total, 'results': results})


@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedDeviceCreateFromRecycleOrderView(APIView):
    """
    从回收订单创建官方验库存设备（手动触发，避免回收侧自动生成）。
    """
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:write', 'inspection:view'])
    def post(self, request):
        recycle_order_id = request.data.get('recycle_order_id')
        sn = (request.data.get('sn') or '').strip()
        imei = (request.data.get('imei') or '').strip()
        location = (request.data.get('location') or '').strip()
        inspection_note = (request.data.get('inspection_note') or '').strip()
        suggested_price = request.data.get('suggested_price')

        if not recycle_order_id:
            return Response({'detail': 'recycle_order_id required'}, status=400)
        if not sn:
            return Response({'detail': 'SN required'}, status=400)

        try:
            o = RecycleOrder.objects.select_related('template', 'user').get(id=recycle_order_id)
        except RecycleOrder.DoesNotExist:
            return Response({'detail': '订单不存在'}, status=404)

        if o.status != 'completed':
            return Response({'detail': '仅支持从“已完成”的回收订单入库'}, status=400)
        if not getattr(o, 'final_price_confirmed', False):
            return Response({'detail': '订单未确认最终价格，无法入库'}, status=400)
        if VerifiedDevice.objects.filter(recycle_order=o).exists():
            return Response({'detail': '该订单已入库，不能重复导入'}, status=400)
        if not getattr(o, 'template', None):
            return Response({'detail': '该订单未关联机型模板，无法入库'}, status=400)

        template = o.template
        def _norm_token(s):
            return ''.join(ch for ch in str(s or '').strip().lower() if ch.isalnum())

        def _clean_options(raw_options):
            cleaned = []
            seen = set()
            for x in list(raw_options or []):
                s = str(x or "").strip()
                if not s:
                    continue
                key = _norm_token(s)
                if key in seen:
                    continue
                cleaned.append(s)
                seen.add(key)
            return cleaned

        raw_storage = (getattr(o, 'selected_storage', '') or o.storage or '')
        raw_ram = (getattr(o, 'selected_ram', '') or '')
        raw_version = (getattr(o, 'selected_version', '') or '')
        raw_color = (getattr(o, 'selected_color', '') or '')

        # 入库阶段不强制做模板选项校验：允许先入库，再在库存编辑/上架前补齐并纠正选项
        normalized_storage = str(raw_storage or '').strip()
        normalized_ram = str(raw_ram or '').strip()
        normalized_version = str(raw_version or '').strip()
        normalized_color = str(raw_color or '').strip()

        def normalize_check_items_to_categories(check_items):
            if not check_items:
                return []
            if isinstance(check_items, list):
                if len(check_items) and isinstance(check_items[0], dict) and ('title' in check_items[0] or 'groups' in check_items[0]):
                    return check_items
                items = []
                for item in check_items:
                    if not isinstance(item, dict):
                        continue
                    value = item.get('value', '')
                    pass_value = item.get('pass')
                    items.append({
                        'label': item.get('label') or item.get('key') or '',
                        'value': value,
                        'pass': pass_value if isinstance(pass_value, bool) else (value in ['pass', True]),
                        **({'image': item.get('image')} if item.get('image') else {})
                    })
                return [{
                    'title': '检测结果',
                    'groups': [{'name': '', 'items': items}]
                }] if items else []
            if isinstance(check_items, dict):
                items = [{
                    'label': str(k),
                    'value': v,
                    'pass': (v == 'pass' or v is True)
                } for k, v in check_items.items()]
                return [{
                    'title': '检测结果',
                    'groups': [{'name': '', 'items': items}]
                }] if items else []
            return []

        # 质检报告：沿用回收单完成后的质检结果（AdminInspectionReport）
        inspection_reports = []
        try:
            from app.admin_api.models import AdminInspectionReport
            rep = AdminInspectionReport.objects.filter(order=o).order_by('-created_at').first()
            inspection_reports = normalize_check_items_to_categories(getattr(rep, 'check_items', None))
            evidence = getattr(rep, 'evidence', None) or []
            if evidence:
                photo_items = [{'label': f'照片{i + 1}', 'value': '', 'pass': True, 'image': url} for i, url in enumerate(evidence) if url]
                if photo_items:
                    inspection_reports = list(inspection_reports or [])
                    inspection_reports.append({'title': '质检照片', 'groups': [{'name': '', 'items': photo_items}]})
            if not inspection_note:
                inspection_note = (getattr(rep, 'remarks', '') or '').strip()
        except Exception:
            inspection_reports = []

        try:
            suggested_price_val = float(suggested_price) if suggested_price not in [None, ''] else None
        except (TypeError, ValueError):
            return Response({'detail': 'suggested_price invalid'}, status=400)

        seller = _get_official_verified_seller()
        cost_price = None
        try:
            if o.final_price is not None:
                cost_price = o.final_price + (o.bonus or 0)
        except Exception:
            cost_price = None

        try:
            device = VerifiedDevice.objects.create(
                recycle_order=o,
                template=template,
                seller=seller,
                category=getattr(template, 'category', None),
                sn=sn,
                imei=imei,
                brand=o.brand,
                model=o.model,
                storage=normalized_storage,
                ram=normalized_ram,
                version=normalized_version,
                color=normalized_color,
                condition=o.condition,
                status='pending',
                location=location,
                cost_price=cost_price,
                suggested_price=suggested_price_val,
                inspection_reports=inspection_reports or [],
                inspection_note=inspection_note or '',
            )
        except IntegrityError:
            return Response({'detail': 'SN 已存在'}, status=400)

        _audit(request.admin, 'create_verified_device_from_recycle_order', 'VerifiedDevice', device.id, snapshot={
            'recycle_order_id': o.id,
            'template_id': getattr(o.template, 'id', None),
        })
        return Response(VerifiedDeviceSerializer(device).data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedDeviceDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get_object(self, pk):
        return VerifiedDevice.objects.get(pk=pk)

    @admin_required(['verified:read', 'verified:write'])
    def get(self, request, pk):
        admin = request.admin
        try:
            obj = self.get_object(pk)
        except VerifiedDevice.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        return Response(VerifiedDeviceSerializer(obj).data)

    @admin_required(['verified:write'])
    def patch(self, request, pk):
        admin = request.admin
        try:
            obj = self.get_object(pk)
        except VerifiedDevice.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        serializer = VerifiedDeviceSerializer(obj, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            device = serializer.save()
            # 若已关联官方验商品：库存修改后自动同步到商品（以库存为准）
            if getattr(device, 'linked_product', None):
                try:
                    create_verified_product_from_device(
                        device,
                        status=getattr(device.linked_product, 'status', 'draft'),
                        price_override=getattr(device.linked_product, 'price', None),
                        original_price_override=getattr(device.linked_product, 'original_price', None),
                        enforce_publish_requirements=False,
                    )
                except ValueError as e:
                    return Response({'detail': str(e)}, status=400)
            return Response(VerifiedDeviceSerializer(device).data)
        return Response(serializer.errors, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedDeviceSyncInspectionReportView(APIView):
    """
    从回收订单同步最新质检报告到库存设备（沿用回收质检数据，不在库存阶段重复录入）。
    """
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:write', 'inspection:view'])
    def post(self, request, pk):
        try:
            device = VerifiedDevice.objects.select_related('recycle_order').get(pk=pk)
        except VerifiedDevice.DoesNotExist:
            return Response({'detail': '设备不存在'}, status=404)

        order = getattr(device, 'recycle_order', None)
        if not order:
            return Response({'detail': '该库存设备没有关联回收订单，无法同步质检报告'}, status=400)

        def normalize_check_items_to_categories(check_items):
            if not check_items:
                return []
            if isinstance(check_items, list):
                if len(check_items) and isinstance(check_items[0], dict) and ('title' in check_items[0] or 'groups' in check_items[0]):
                    return check_items
                items = []
                for item in check_items:
                    if not isinstance(item, dict):
                        continue
                    value = item.get('value', '')
                    pass_value = item.get('pass')
                    items.append({
                        'label': item.get('label') or item.get('key') or '',
                        'value': value,
                        'pass': pass_value if isinstance(pass_value, bool) else (value in ['pass', True]),
                        **({'image': item.get('image')} if item.get('image') else {})
                    })
                return [{
                    'title': '检测结果',
                    'groups': [{'name': '', 'items': items}]
                }] if items else []
            if isinstance(check_items, dict):
                items = [{
                    'label': str(k),
                    'value': v,
                    'pass': (v == 'pass' or v is True)
                } for k, v in check_items.items()]
                return [{
                    'title': '检测结果',
                    'groups': [{'name': '', 'items': items}]
                }] if items else []
            return []

        inspection_reports = []
        remarks = ''
        try:
            from app.admin_api.models import AdminInspectionReport
            rep = AdminInspectionReport.objects.filter(order=order).order_by('-created_at').first()
            if rep:
                inspection_reports = normalize_check_items_to_categories(getattr(rep, 'check_items', None))
                evidence = getattr(rep, 'evidence', None) or []
                if evidence:
                    photo_items = [{'label': f'照片{i + 1}', 'value': '', 'pass': True, 'image': url} for i, url in enumerate(evidence) if url]
                    if photo_items:
                        inspection_reports = list(inspection_reports or [])
                        inspection_reports.append({'title': '质检照片', 'groups': [{'name': '', 'items': photo_items}]})
                remarks = (getattr(rep, 'remarks', '') or '').strip()
        except Exception:
            inspection_reports = []
            remarks = ''

        device.inspection_reports = inspection_reports or []
        if remarks and not (device.inspection_note or '').strip():
            device.inspection_note = remarks
        device.save(update_fields=['inspection_reports', 'inspection_note', 'updated_at'])
        return Response(VerifiedDeviceSerializer(device).data)


@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedDeviceListProductView(APIView):
    """
    一键上架：从设备生成官方验商品
    """
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:write'])
    def post(self, request, pk):
        admin = request.admin
        try:
            device = VerifiedDevice.objects.get(pk=pk)
        except VerifiedDevice.DoesNotExist:
            return Response({'detail': '设备不存在'}, status=404)

        # 允许前端覆盖售价/原价/状态，否则用设备建议价，默认上架
        price_override = request.data.get('price')
        original_price_override = request.data.get('original_price')
        status_override = request.data.get('status', 'active')

        try:
            product = create_verified_product_from_device(
                device,
                status=status_override,
                price_override=price_override,
                original_price_override=original_price_override,
            )
            device.refresh_from_db()
            return Response({
                'detail': '生成官方验商品成功',
                'product': VerifiedProductSerializer(product, context={'request': request}).data
            }, status=201)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
        except Exception as e:
            return Response({'detail': f'生成失败: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifiedDeviceActionView(APIView):
    """
    设备状态快捷操作：lock / unlock / sold / remove / ready / repair
    """
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:write'])
    def post(self, request, pk, action):
        admin = request.admin
        try:
            device = VerifiedDevice.objects.get(pk=pk)
        except VerifiedDevice.DoesNotExist:
            return Response({'detail': '设备不存在'}, status=404)

        target_status = None
        if action == 'lock':
            target_status = 'locked'
        elif action == 'unlock':
            target_status = 'ready'
        elif action == 'sold':
            target_status = 'sold'
        elif action == 'remove':
            target_status = 'removed'
        elif action == 'ready':
            target_status = 'ready'
        elif action == 'repair':
            target_status = 'repairing'
        else:
            return Response({'detail': '不支持的操作'}, status=400)

        device.status = target_status
        device.save(update_fields=['status', 'updated_at'])
        return Response({'detail': '操作成功', 'status': target_status})


@method_decorator(csrf_exempt, name='dispatch')
class RecycleDeviceTemplateResolveView(APIView):
    """
    根据品牌+型号解析到机型模板（用于官方验库存录入时强约束选项来源）。
    """
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:write', 'recycle_template:view'])
    def get(self, request):
        brand = (request.query_params.get('brand') or '').strip()
        model = (request.query_params.get('model') or '').strip()
        if not brand or not model:
            return Response({'detail': 'brand/model required'}, status=400)

        tpl = RecycleDeviceTemplate.objects.filter(
            is_active=True,
            brand__iexact=brand,
            model__iexact=model,
        ).first()
        if not tpl:
            return Response({'detail': '未找到机型模板（请先在回收机型模板管理创建并启用）'}, status=404)

        return Response({
            'id': tpl.id,
            'brand': tpl.brand,
            'model': tpl.model,
            'category_id': getattr(tpl, 'category_id', None),
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdminOfficialInventoryView(APIView):
    """
    官方验库存管理：筛选/列表/简单统计
    """
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:view', 'verified:write'])
    def get(self, request):
        admin = request.admin

        qs = VerifiedDevice.objects.select_related('template', 'category').all().order_by('-created_at')

        status_q = request.GET.get('status')
        template_id = request.GET.get('template_id')
        brand = request.GET.get('brand')
        model = request.GET.get('model')
        has_product = request.GET.get('has_product')
        created_from = request.GET.get('created_from')
        created_to = request.GET.get('created_to')

        if status_q:
            qs = qs.filter(status=status_q)
        if template_id:
            qs = qs.filter(template_id=template_id)
        if brand:
            qs = qs.filter(brand__icontains=brand)
        if model:
            qs = qs.filter(model__icontains=model)
        if has_product == 'true':
            qs = qs.filter(linked_product__isnull=False)
        if has_product == 'false':
            qs = qs.filter(linked_product__isnull=True)
        if created_from:
            try:
                qs = qs.filter(created_at__gte=datetime.fromisoformat(created_from))
            except Exception:
                pass
        if created_to:
            try:
                qs = qs.filter(created_at__lte=datetime.fromisoformat(created_to))
            except Exception:
                pass

        # 排序
        ordering = request.GET.get('ordering', '-created_at')
        qs = qs.order_by(ordering)

        # 分页
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        total = qs.count()

        serializer = OfficialInventorySerializer(qs[start:end], many=True)

        status_counts = {item['status']: item['c'] for item in qs.values('status').annotate(c=Count('id'))} if total else {}

        return Response({
            'count': total,
            'results': serializer.data,
            'status_counts': status_counts
        })
# 回收商品相关视图
@method_decorator(csrf_exempt, name='dispatch')
class RecycledProductsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['recycled:view'])
    def get(self, request):
        admin = request.admin
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = VerifiedProduct.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        return Response({'results': VerifiedProductListSerializer(items, many=True).data, 'count': total})
    @admin_required(['recycled:write'])
    def post(self, request, item_id=None):
        admin = request.admin
        if item_id:
            try:
                p = VerifiedProduct.objects.get(id=item_id)
                p.status = 'active'
                p.save()
                return Response({'success': True})
            except VerifiedProduct.DoesNotExist:
                return Response({'success': False})
        return Response({'success': False})
    @admin_required(['recycled:write'])
    def put(self, request, item_id=None):
        admin = request.admin
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
    # Disable default auth; handled manually
    authentication_classes = []
    permission_classes = []

    @admin_required(['verified:view'])
    def get(self, request, item_id=None):
        if item_id:
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
                return Response({'detail': 'product not found'}, status=404)

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
        admin = request.admin
        try:
            v = VerifiedProduct.objects.get(id=item_id)
            if action == 'publish':
                if v.stock <= 0:
                    return Response({'success': False, 'detail': '库存为0，无法上架'}, status=400)
                device = VerifiedDevice.objects.filter(linked_product=v).first()
                if not device:
                    return Response({'success': False, 'detail': '官方验商品仅允许由库存设备上架生成'}, status=400)
                try:
                    create_verified_product_from_device(
                        device,
                        status='active',
                        price_override=v.price,
                        original_price_override=v.original_price,
                    )
                    v.refresh_from_db()
                except ValueError as e:
                    return Response({'success': False, 'detail': str(e)}, status=400)
            elif action == 'unpublish':
                v.status = 'removed'
            elif action == 'audit-approve':
                device = VerifiedDevice.objects.filter(linked_product=v).first()
                if not device:
                    return Response({'success': False, 'detail': '官方验商品仅允许由库存设备上架生成'}, status=400)
                try:
                    create_verified_product_from_device(
                        device,
                        status='active',
                        price_override=v.price,
                        original_price_override=v.original_price,
                    )
                    v.refresh_from_db()
                except ValueError as e:
                    return Response({'success': False, 'detail': str(e)}, status=400)
                AdminAuditLog.objects.create(actor=admin, target_type='VerifiedProduct', target_id=v.id, action='approve', snapshot_json={'title': v.title})
            elif action == 'audit-reject':
                v.status = 'removed'
                AdminAuditLog.objects.create(actor=admin, target_type='VerifiedProduct', target_id=v.id, action='reject', snapshot_json={'title': v.title})
            v.save()
            return Response({'success': True})
        except VerifiedProduct.DoesNotExist:
            return Response({'success': False})

# 审核日志相关视图
@method_decorator(csrf_exempt, name='dispatch')
class AuditLogsView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['audit_log:view'])
    def get(self, request):
        admin = request.admin
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
    # ??REST Framework???????????????????
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['admin_user:view'])
    def get(self, request, uid=None):
        admin = request.admin
        if uid:
            try:
                u = AdminUser.objects.get(id=uid)
                return Response(AdminUserSerializer(u).data)
            except AdminUser.DoesNotExist:
                return Response({'detail': '?????'}, status=404)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = AdminUser.objects.all().order_by('-id')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        return Response({'results': AdminUserSerializer(items, many=True).data, 'count': total})

    @admin_required(['admin_user:write'])
    def post(self, request):
        admin = request.admin
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        role_name = request.data.get('role', 'auditor')
        email = request.data.get('email', '').strip()
        if not username or not password:
            return Response({'detail': 'username and password required'}, status=400)
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
        _audit(admin, 'admin_user:create', 'AdminUser', u.id, {'username': u.username, 'role': role_name})
        return Response(AdminUserSerializer(u).data)

    @admin_required(['admin_user:write'])
    def put(self, request, uid):
        admin = request.admin
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
            _audit(admin, 'admin_user:update', 'AdminUser', u.id, {'username': u.username, 'role': u.role.name if u.role else None})
            return Response(AdminUserSerializer(u).data)
        except AdminUser.DoesNotExist:
            return Response({'detail': '?????'}, status=404)

    @admin_required(['admin_user:write'])
    def delete(self, request, uid):
        admin = request.admin
        try:
            u = AdminUser.objects.get(id=uid)
            _audit(admin, 'admin_user:delete', 'AdminUser', u.id, {'username': u.username})
            u.delete()
            return Response({'success': True})
        except AdminUser.DoesNotExist:
            return Response({'detail': '?????'}, status=404)

class RolesView(APIView):
    # ??REST Framework???????????????????
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['role:view'])
    def get(self, request):
        admin = request.admin
        roles = AdminRole.objects.all()
        data = [{
            'id': r.id,
            'name': r.name,
            'description': r.description,
            'permissions': r.permissions or []
        } for r in roles]
        return Response({'results': data, 'all_permissions': PERMISSIONS})

    @admin_required(['role:write'])
    def post(self, request):
        admin = request.admin
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        perms = request.data.get('permissions')
        if perms is None:
            perms_text = request.data.get('permsText', '').strip()
            perms = [p.strip() for p in perms_text.split(',') if p.strip()] if perms_text else []
        if not isinstance(perms, list):
            return Response({'detail': 'permissions must be a list'}, status=400)
        if not name:
            return Response({'detail': 'role name required'}, status=400)
        valid, invalid = validate_permissions(perms)
        if invalid:
            return Response({'detail': 'invalid permissions', 'invalid': invalid}, status=400)
        perms = sorted(set(valid))
        role, created = AdminRole.objects.get_or_create(
            name=name,
            defaults={'description': description, 'permissions': perms}
        )
        if not created:
            role.description = description
            role.permissions = perms
            role.save()
        _audit(admin, 'role:upsert', 'AdminRole', role.id, {'name': role.name, 'permissions': perms})
        return Response({'success': True, 'id': role.id})

class PaymentOrdersView(APIView):

    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['payment:view'])
    def get(self, request):
        admin = request.admin
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

    @admin_required(['payment:view'])
    def get(self, request, order_id):
        admin = request.admin
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

def _payment_action_perms(request, order_id, action):
    if action == 'query':
        return ['payment:view']
    if action == 'refund':
        return ['payment:write']
    if action == 'ship':
        return ['order:ship']
    return None

@method_decorator(csrf_exempt, name='dispatch')
class PaymentOrderActionView(APIView):
    # Disable default auth; handled manually
    authentication_classes = []
    permission_classes = []

    @admin_required(resolve_perms=_payment_action_perms)
    def post(self, request, order_id, action):
        admin = request.admin
        try:
            o = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'success': False, 'detail': 'order not found'}, status=404)
        if action == 'query':
            alipay = AlipayClient()
            result = alipay.query_trade(f'normal_{order_id}')
            return Response({'success': True, 'result': result})
        if action == 'refund':
            return Response({'success': False, 'detail': 'refund not implemented'}, status=501)
        if action == 'ship':
            carrier = request.data.get('carrier', '').strip()
            tracking_number = request.data.get('tracking_number', '').strip()
            o.carrier = carrier
            o.tracking_number = tracking_number
            o.shipped_at = timezone.now()
            o.status = 'shipped'
            o.save()
            AdminAuditLog.objects.create(
                actor=admin,
                target_type='Order',
                target_id=o.id,
                action='ship',
                snapshot_json={'carrier': carrier, 'tracking_number': tracking_number}
            )
            return Response({'success': True})
        return Response({'success': False}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentOrderSettlementView(APIView):
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['payment:view'])
    def get(self, request, order_id, action=None):
        admin = request.admin
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
    
    @admin_required(['payment:write'])
    def post(self, request, order_id, action):
        admin = request.admin
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
                AdminAuditLog.objects.create(actor=admin, target_type='Order', target_id=o.id, action='settlement_retry', snapshot_json={'result': 'success'})
                return Response({'success': True})
            else:
                o.settlement_status = 'failed'
                o.settle_request_no = out_request_no
                o.save()
                AdminAuditLog.objects.create(actor=admin, target_type='Order', target_id=o.id, action='settlement_retry', snapshot_json={'result': 'failed', 'code': result.get('code'), 'msg': result.get('msg')})
                return Response({'success': False, 'detail': result.get('msg', '分账失败')}, status=500)
        except Order.DoesNotExist:
            return Response({'detail': 'order not found'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class SettlementSummaryView(APIView):
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['payment:view'])
    def get(self, request):
        admin = request.admin
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
    
    @admin_required(['verified:view'])
    def get(self, request, oid=None):
        admin = request.admin
        
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
    @admin_required(['verified:write'])
    def post(self, request, oid, action):
        admin = request.admin
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
            if vo.status not in ['pending', 'paid']:
                return Response({'success': False, 'detail': '当前状态不允许取消'}, status=400)
            if vo.status == 'paid':
                from app.secondhand_app.alipay_client import AlipayClient
                alipay = AlipayClient()
                out_request_no = f'refund_verified_{vo.id}_{int(timezone.now().timestamp())}'
                query_result = alipay.query_trade(f'verified_{vo.id}')
                if query_result.get('success'):
                    trade_status = query_result.get('trade_status')
                    trade_no = query_result.get('trade_no', '') or ''
                    if trade_status not in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
                        vo.status = 'cancelled'
                        product = getattr(vo, 'product', None)
                        if product:
                            if product.status != 'active':
                                product.status = 'active'
                            if product.stock <= 0:
                                product.stock = 1
                            if product.sales_count and product.sales_count > 0:
                                product.sales_count = product.sales_count - 1
                            if product.removed_reason:
                                product.removed_reason = ''
                            product.save(update_fields=['status', 'stock', 'sales_count', 'removed_reason', 'updated_at'])
                        vo.save()
                        AdminAuditLog.objects.create(actor=admin, target_type='VerifiedOrder', target_id=vo.id, action=action, snapshot_json={'status': vo.status})
                        return Response({'success': True})
                    refund_result = alipay.refund_trade(
                        out_trade_no=f'verified_{vo.id}',
                        refund_amount=vo.total_price,
                        refund_reason='订单取消自动退款',
                        trade_no=trade_no or None,
                        out_request_no=out_request_no
                    )
                else:
                    refund_result = alipay.refund_trade(
                        out_trade_no=f'verified_{vo.id}',
                        refund_amount=vo.total_price,
                        refund_reason='订单取消自动退款',
                        out_request_no=out_request_no
                    )
                if not refund_result.get('success'):
                    detail = refund_result.get('msg', '退款失败')
                    sub_code = refund_result.get('sub_code')
                    sub_msg = refund_result.get('sub_msg')
                    if sub_code or sub_msg:
                        detail = f'{detail} ({sub_code or "-"} {sub_msg or "-"})'
                    return Response({'success': False, 'detail': detail}, status=400)
            vo.status = 'cancelled'
            product = getattr(vo, 'product', None)
            if product:
                if product.status != 'active':
                    product.status = 'active'
                if product.stock <= 0:
                    product.stock = 1
                if product.sales_count and product.sales_count > 0:
                    product.sales_count = product.sales_count - 1
                if product.removed_reason:
                    product.removed_reason = ''
                product.save(update_fields=['status', 'stock', 'sales_count', 'removed_reason', 'updated_at'])
        else:
            return Response({'success': False, 'detail': 'unknown action'}, status=400)
        vo.save()
        AdminAuditLog.objects.create(actor=admin, target_type='VerifiedOrder', target_id=vo.id, action=action, snapshot_json={'status': vo.status})
        return Response({'success': True})

@method_decorator(csrf_exempt, name='dispatch')
class CategoriesAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['category:view'])
    def get(self, request, cid=None):
        admin = request.admin
        if cid:
            try:
                c = Category.objects.get(id=cid)
                return Response({'id': c.id, 'name': c.name, 'description': c.description})
            except Category.DoesNotExist:
                return Response({'detail': '分类不存在'}, status=404)
        qs = Category.objects.all()
        data = [{'id': c.id, 'name': c.name, 'description': c.description} for c in qs]
        return Response({'results': data})
    @admin_required(['category:write'])
    def post(self, request):
        admin = request.admin
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        c = Category.objects.create(name=name, description=description)
        return Response({'id': c.id, 'name': c.name})
    @admin_required(['category:write'])
    def put(self, request, cid):
        admin = request.admin
        try:
            c = Category.objects.get(id=cid)
            c.name = request.data.get('name', c.name)
            c.description = request.data.get('description', c.description)
            c.save()
            return Response({'id': c.id, 'name': c.name})
        except Category.DoesNotExist:
            return Response({'detail': '分类不存在'}, status=404)
    @admin_required(['category:delete'])
    def delete(self, request, cid):
        admin = request.admin
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
    
    @admin_required(['product:view'])
    def get(self, request, pid=None):
        admin = request.admin

        def serialize_product(p: Product):
            images = []
            try:
                for img in p.images.all().order_by('-is_primary', 'id'):
                    url = img.image.url if getattr(img, 'image', None) else ''
                    if url:
                        url = request.build_absolute_uri(url)
                    images.append({'id': img.id, 'image': url, 'is_primary': bool(getattr(img, 'is_primary', False))})
            except Exception:
                pass
            return {
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'price': float(p.price) if p.price is not None else 0,
                'original_price': float(p.original_price) if p.original_price else None,
                'condition': p.condition,
                'status': p.status,
                'removed_reason': getattr(p, 'removed_reason', '') or '',
                'removed_at': p.removed_at.isoformat() if getattr(p, 'removed_at', None) else None,
                'removed_by': getattr(p, 'removed_by', '') or '',
                'location': p.location,
                'seller': getattr(p.seller, 'username', '') if getattr(p, 'seller', None) else '',
                'category': getattr(p.category, 'name', '') if getattr(p, 'category', None) else '',
                'images': images,
                'created_at': p.created_at.isoformat() if getattr(p, 'created_at', None) else None,
                'updated_at': p.updated_at.isoformat() if getattr(p, 'updated_at', None) else None,
            }

        if pid:
            try:
                p = Product.objects.select_related('seller', 'category').prefetch_related('images').get(id=pid)
                return Response(serialize_product(p))
            except Product.DoesNotExist:
                return Response({'detail': '商品不存在'}, status=404)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        search = (request.query_params.get('search') or '').strip()
        status_filter = (request.query_params.get('status') or '').strip()

        qs = Product.objects.select_related('seller', 'category').prefetch_related('images').all().order_by('-created_at')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(seller__username__icontains=search))
        if status_filter:
            qs = qs.filter(status=status_filter)
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [serialize_product(p) for p in items]
        return Response({'results': data, 'count': total})

    @admin_required(['product:write'])
    def put(self, request, pid):
        admin = request.admin
        try:
            p = Product.objects.select_related('seller', 'category').get(id=pid)
        except Product.DoesNotExist:
            return Response({'detail': '商品不存在'}, status=404)

        old_status = p.status
        if old_status == 'sold':
            return Response({'detail': '已售商品不允许修改'}, status=400)

        new_status = request.data.get('status', old_status)
        # 状态流转限制：不允许从 sold 回流；不允许 removed/pending 直接标记 sold；不允许 active->pending
        if old_status in ['pending', 'removed'] and new_status == 'sold':
            return Response({'detail': '非在售商品不能标记已售'}, status=400)
        if old_status == 'active' and new_status == 'pending':
            return Response({'detail': '在售商品不能改回待审核'}, status=400)

        allowed_fields = ['title', 'description', 'price', 'original_price', 'condition', 'location', 'status']
        for field in allowed_fields:
            if field not in request.data:
                continue
            value = request.data.get(field)
            if field == 'original_price' and value in ['', None]:
                value = None
            setattr(p, field, value)

        # 下架原因/时间：当状态变为 removed 时写入；改回 active/pending 时清空
        try:
            from django.utils import timezone
            if p.status == 'removed' and old_status != 'removed':
                reason = (request.data.get('reason') or request.data.get('removed_reason') or '').strip()
                p.removed_reason = reason
                p.removed_at = timezone.now()
                p.removed_by = getattr(admin, 'username', '') or getattr(admin, 'name', '') or 'admin'
            elif old_status == 'removed' and p.status in ('active', 'pending'):
                p.removed_reason = ''
                p.removed_at = None
                p.removed_by = ''
        except Exception:
            pass

        p.save()
        return Response({'success': True})

    @admin_required(['product:write'])
    def post(self, request, pid, action):
        admin = request.admin
        try:
            p = Product.objects.get(id=pid)
            if action == 'publish':
                if p.status == 'sold':
                    return Response({'success': False, 'detail': '已售商品不能重新发布'}, status=400)
                p.status = 'active'
                if getattr(p, 'removed_reason', ''):
                    p.removed_reason = ''
                if getattr(p, 'removed_at', None):
                    p.removed_at = None
                if getattr(p, 'removed_by', ''):
                    p.removed_by = ''
            elif action == 'unpublish':
                if p.status == 'sold':
                    return Response({'success': False, 'detail': '已售商品不能下架/更改状态'}, status=400)
                p.status = 'removed'
                try:
                    from django.utils import timezone
                    reason = (request.data.get('reason') or '').strip()
                    p.removed_reason = reason
                    p.removed_at = timezone.now()
                    p.removed_by = getattr(admin, 'username', '') or getattr(admin, 'name', '') or 'admin'
                except Exception:
                    pass
            elif action == 'mark-sold':
                if p.status != 'active':
                    return Response({'success': False, 'detail': '只有在售商品才能标记已售'}, status=400)
                p.status = 'sold'
            else:
                return Response({'success': False, 'detail': '未知操作'}, status=400)
            p.save()
            return Response({'success': True})
        except Product.DoesNotExist:
            return Response({'success': False})
    @admin_required(['product:delete'])
    def delete(self, request, pid):
        admin = request.admin
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
    
    @admin_required(['user:view'])
    def get(self, request, uid=None):
        admin = request.admin
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
    @admin_required(['user:write'])
    def post(self, request, uid):
        admin = request.admin
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
    @admin_required(['user:delete'])
    def delete(self, request, uid):
        admin = request.admin
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
    
    @admin_required(['message:view'])
    def get(self, request, mid=None):
        admin = request.admin
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = Message.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{'id': m.id, 'sender': m.sender.username if m.sender else '', 'receiver': m.receiver.username if m.receiver else '', 'content': m.content, 'is_read': m.is_read, 'created_at': m.created_at.isoformat()} for m in items]
        return Response({'results': data, 'count': total})
    @admin_required(['message:delete'])
    def delete(self, request, mid):
        admin = request.admin
        try:
            m = Message.objects.get(id=mid)
            m.delete()
            return Response({'success': True})
        except Message.DoesNotExist:
            return Response({'detail': '消息不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class AdminServiceConversationsView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['message:service'])
    def get(self, request):
        service_user = _get_service_user()
        related_messages = Message.objects.filter(
            Q(sender=service_user) | Q(receiver=service_user)
        ).select_related('sender', 'receiver', 'product').order_by('-created_at')

        conversations = {}
        for msg in related_messages:
            peer = msg.receiver if msg.sender == service_user else msg.sender
            if not peer:
                continue
            peer_id = peer.id
            if peer_id not in conversations:
                if msg.recalled:
                    display_content = '已撤回'
                elif msg.message_type == 'product':
                    display_content = f"[商品]{(msg.payload or {}).get('title','')}"
                elif msg.message_type == 'image':
                    display_content = '[图片]'
                else:
                    display_content = msg.content

                conversations[peer_id] = {
                    'user': UserSerializer(peer, context={'request': request}).data,
                    'last_message': {
                        'id': msg.id,
                        'content': display_content,
                        'message_type': msg.message_type,
                        'payload': msg.payload,
                        'recalled': msg.recalled,
                        'created_at': msg.created_at.isoformat(),
                    },
                    'unread_count': 0
                }

        unread_qs = Message.objects.filter(
            receiver=service_user, is_read=False
        ).values('sender').annotate(total=Count('id'))
        unread_map = {item['sender']: item['total'] for item in unread_qs}

        for peer_id, count in unread_map.items():
            if peer_id in conversations:
                conversations[peer_id]['unread_count'] = count

        result = sorted(
            conversations.values(),
            key=lambda x: x['last_message']['created_at'] if x['last_message'] else '',
            reverse=True
        )

        return Response({'service_user_id': service_user.id, 'results': result})

@method_decorator(csrf_exempt, name='dispatch')
class AdminServiceMessagesView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['message:service'])
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': '缺少用户ID参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User = get_user_model()
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        service_user = _get_service_user()
        messages = Message.objects.filter(
            (Q(sender=service_user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=service_user))
        ).order_by('created_at')

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response({'service_user_id': service_user.id, 'results': serializer.data})

    @admin_required(['message:service'])
    def post(self, request):
        user_id = request.data.get('user_id')
        content = (request.data.get('content') or '').strip()
        if not user_id:
            return Response({'detail': '缺少用户ID参数'}, status=status.HTTP_400_BAD_REQUEST)
        if not content:
            return Response({'detail': '消息内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User = get_user_model()
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        service_user = _get_service_user()
        message = Message.objects.create(
            sender=service_user,
            receiver=other_user,
            content=content,
            message_type='text',
            recallable_until=timezone.now() + timedelta(minutes=2)
        )

        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            event_payload = {
                'type': 'new_message',
                'id': message.id,
                'sender_id': message.sender_id,
                'sender_username': message.sender.username,
                'receiver_id': message.receiver_id,
                'receiver_username': message.receiver.username,
                'content': message.content,
                'message_type': message.message_type,
                'image': None,
                'payload': message.payload,
                'created_at': message.created_at.isoformat(),
                'recalled': message.recalled
            }
            async_to_sync(channel_layer.group_send)(f'user_{other_user.id}', {'type': 'chat_message', 'message': event_payload})
            async_to_sync(channel_layer.group_send)(f'user_{service_user.id}', {'type': 'chat_message', 'message': event_payload})
        except Exception:
            pass

        serializer = MessageSerializer(message, context={'request': request})
        return Response({'service_user_id': service_user.id, 'message': serializer.data}, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class AdminServiceReadView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['message:service'])
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': '缺少用户ID参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User = get_user_model()
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        service_user = _get_service_user()
        Message.objects.filter(
            sender=other_user,
            receiver=service_user,
            is_read=False
        ).update(is_read=True)

        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{other_user.id}',
                {
                    'type': 'chat_message',
                    'message': {
                        'type': 'read_ack',
                        'peer_id': service_user.id
                    }
                }
            )
        except Exception:
            pass

        return Response({'detail': '已标记为已读'})

@method_decorator(csrf_exempt, name='dispatch')
class AdminServiceTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['message:service'])
    def get(self, request):
        service_user = _get_service_user()
        token = AccessToken.for_user(service_user)
        token.set_exp(lifetime=timedelta(hours=2))
        return Response({
            'token': str(token),
            'service_user_id': service_user.id,
            'username': service_user.username,
        })

@method_decorator(csrf_exempt, name='dispatch')
class AdminServiceOrderItemsView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['message:service'])
    def get(self, request):
        item_type = (request.query_params.get('type') or 'secondhand').strip()
        keyword = (request.query_params.get('keyword') or '').strip()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        if item_type == 'verified':
            qs = VerifiedOrder.objects.select_related('product', 'buyer').order_by('-created_at')
            if keyword:
                qs = qs.filter(
                    Q(product__title__icontains=keyword) |
                    Q(buyer__username__icontains=keyword)
                )
        elif item_type == 'recycle':
            qs = RecycleOrder.objects.select_related('user').order_by('-created_at')
            if keyword:
                qs = qs.filter(
                    Q(brand__icontains=keyword) |
                    Q(model__icontains=keyword) |
                    Q(user__username__icontains=keyword)
                )
        else:
            item_type = 'secondhand'
            qs = Order.objects.select_related('product', 'buyer').order_by('-created_at')
            if keyword:
                qs = qs.filter(
                    Q(product__title__icontains=keyword) |
                    Q(buyer__username__icontains=keyword)
                )

        total = qs.count()
        items = qs[(page - 1) * page_size: page * page_size]

        results = []
        for order in items:
            payload = _build_order_item_payload(item_type, order)
            results.append({
                'id': order.id,
                'type': item_type,
                'title': payload.get('title', ''),
                'price': payload.get('price', ''),
                'cover': payload.get('cover', ''),
                'created_at': order.created_at.isoformat() if getattr(order, 'created_at', None) else None,
                'payload': payload,
            })

        return Response({'results': results, 'count': total})

@method_decorator(csrf_exempt, name='dispatch')
class AdminServiceProductMessageView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['message:service'])
    def post(self, request):
        user_id = request.data.get('user_id')
        item_type = (request.data.get('item_type') or '').strip()
        item_id = request.data.get('item_id')
        if not user_id or not item_type or not item_id:
            return Response({'detail': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User = get_user_model()
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        try:
            if item_type == 'verified':
                order_obj = VerifiedOrder.objects.select_related('product').get(id=item_id)
            elif item_type == 'recycle':
                order_obj = RecycleOrder.objects.get(id=item_id)
            else:
                item_type = 'secondhand'
                order_obj = Order.objects.select_related('product').get(id=item_id)
        except (VerifiedOrder.DoesNotExist, RecycleOrder.DoesNotExist, Order.DoesNotExist):
            return Response({'detail': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        payload = _build_order_item_payload(item_type, order_obj)
        service_user = _get_service_user()
        product = order_obj.product if item_type == 'secondhand' else None
        message = Message.objects.create(
            sender=service_user,
            receiver=other_user,
            content='',
            product=product,
            message_type='product',
            payload=payload,
            recallable_until=timezone.now() + timedelta(minutes=2)
        )

        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            event_payload = {
                'type': 'new_message',
                'id': message.id,
                'sender_id': message.sender_id,
                'sender_username': message.sender.username,
                'receiver_id': message.receiver_id,
                'receiver_username': message.receiver.username,
                'content': '',
                'message_type': message.message_type,
                'payload': message.payload,
                'created_at': message.created_at.isoformat(),
                'recalled': message.recalled
            }
            async_to_sync(channel_layer.group_send)(f'user_{other_user.id}', {'type': 'chat_message', 'message': event_payload})
            async_to_sync(channel_layer.group_send)(f'user_{service_user.id}', {'type': 'chat_message', 'message': event_payload})
        except Exception:
            pass

        serializer = MessageSerializer(message, context={'request': request})
        return Response({'message': serializer.data}, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class AdminServiceImageMessageView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['message:service'])
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': '缺少用户ID参数'}, status=status.HTTP_400_BAD_REQUEST)
        if 'image' not in request.FILES:
            return Response({'detail': '未提供图片文件'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User = get_user_model()
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        service_user = _get_service_user()
        message = Message.objects.create(
            sender=service_user,
            receiver=other_user,
            content='',
            message_type='image',
            image=request.FILES['image'],
            recallable_until=timezone.now() + timedelta(minutes=2)
        )

        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            event_payload = {
                'type': 'new_message',
                'id': message.id,
                'sender_id': message.sender_id,
                'sender_username': message.sender.username,
                'receiver_id': message.receiver_id,
                'receiver_username': message.receiver.username,
                'content': message.content,
                'message_type': message.message_type,
                'image': request.build_absolute_uri(message.image.url) if message.image else None,
                'payload': message.payload,
                'created_at': message.created_at.isoformat(),
                'recalled': message.recalled
            }
            async_to_sync(channel_layer.group_send)(f'user_{other_user.id}', {'type': 'chat_message', 'message': event_payload})
            async_to_sync(channel_layer.group_send)(f'user_{service_user.id}', {'type': 'chat_message', 'message': event_payload})
        except Exception:
            pass

        serializer = MessageSerializer(message, context={'request': request})
        return Response({'message': serializer.data}, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class AddressesAdminView(APIView):
    # 禁用REST Framework的默认认证和权限检查，因为我们手动处理
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['address:view'])
    def get(self, request, aid=None):
        admin = request.admin
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        qs = Address.objects.all().order_by('-created_at')
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{'id': a.id, 'user': a.user.username if a.user else '', 'name': a.name, 'phone': a.phone, 'address': a.address, 'is_default': a.is_default, 'created_at': a.created_at.isoformat()} for a in items]
        return Response({'results': data, 'count': total})
    @admin_required(['address:delete'])
    def delete(self, request, aid):
        admin = request.admin
        try:
            a = Address.objects.get(id=aid)
            a.delete()
            return Response({'success': True})
        except Address.DoesNotExist:
            return Response({'detail': '地址不存在'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class PlatformRecipientSettingView(APIView):
    authentication_classes = []
    permission_classes = []

    @admin_required(['address:view'])
    def get(self, request):
        obj = _get_platform_recipient()
        if not obj:
            defaults = getattr(settings, 'PLATFORM_RECIPIENT_DEFAULT', {}) or {}
            return Response({
                'name': defaults.get('name', ''),
                'phone': defaults.get('phone', ''),
                'address': defaults.get('address', '')
            })
        serializer = PlatformRecipientSerializer(obj)
        return Response(serializer.data)

    @admin_required(['address:write'])
    def put(self, request):
        obj = _get_platform_recipient()
        if not obj:
            return Response({'detail': '请先执行数据库迁移以启用平台设置'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = PlatformRecipientSerializer(obj, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


# ==================== 回收机型模板管理 ====================

@method_decorator(csrf_exempt, name='dispatch')
class RecycleDeviceTemplateView(APIView):
    """回收机型模板管理"""
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['recycle_template:view'])
    def get(self, request, template_id=None):
        admin = request.admin
        
        if template_id:
            # 获取单个模板详情
            try:
                template = RecycleDeviceTemplate.objects.get(id=template_id)
                serializer = RecycleDeviceTemplateSerializer(template)
                return Response(serializer.data)
            except RecycleDeviceTemplate.DoesNotExist:
                return Response({'detail': '模板不存在'}, status=404)
        else:
            # 获取模板列表
            device_type = request.query_params.get('device_type', '')
            brand = request.query_params.get('brand', '')
            search = request.query_params.get('search', '').strip()
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            qs = RecycleDeviceTemplate.objects.all()
            
            if device_type:
                qs = qs.filter(device_type=device_type)
            if brand:
                qs = qs.filter(brand=brand)
            if search:
                qs = qs.filter(
                    Q(device_type__icontains=search) |
                    Q(brand__icontains=search) |
                    Q(model__icontains=search)
                )
            
            total = qs.count()
            items = qs.order_by('device_type', 'brand', 'model')[(page-1)*page_size: page*page_size]
            serializer = RecycleDeviceTemplateListSerializer(items, many=True)
            return Response({'results': serializer.data, 'count': total})
    
    @admin_required(['recycle_template:create'])
    def post(self, request):
        """创建模板"""
        admin = request.admin
        
        data = request.data.copy()
        data['created_by'] = admin.id
        
        serializer = RecycleDeviceTemplateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    @admin_required(['recycle_template:update'])
    def put(self, request, template_id):
        """更新模板"""
        admin = request.admin
        
        try:
            template = RecycleDeviceTemplate.objects.get(id=template_id)
            serializer = RecycleDeviceTemplateSerializer(template, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '模板不存在'}, status=404)
    
    @admin_required(['recycle_template:delete'])
    def delete(self, request, template_id):
        """删除模板"""
        admin = request.admin
        
        try:
            template = RecycleDeviceTemplate.objects.get(id=template_id)
            template.delete()
            return Response({'success': True})
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '模板不存在'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class RecycleTemplateDownloadView(APIView):
    """下载机型模板文件（Excel格式）"""
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['recycle_template:view'])
    def get(self, request):
        admin = request.admin
        
        try:
            import io
            from django.http import HttpResponse
            
            # 尝试使用pandas生成Excel，如果没有则使用csv
            try:
                import pandas as pd
                use_excel = True
            except ImportError:
                use_excel = False
            
            # 检查是否导出现有机型（包含完整问卷配置）
            export_existing = request.query_params.get('export_existing', '').lower() == 'true'
            
            if export_existing:
                # 导出现有机型模板（包含完整问卷配置）
                from app.admin_api.models import RecycleDeviceTemplate
                templates = RecycleDeviceTemplate.objects.filter(is_active=True).order_by('device_type', 'brand', 'model')
                
                template_data = []
                question_data = []
                option_data = []
                
                for template in templates:
                    # 机型基础信息
                    storages = sorted((template.base_prices or {}).keys())
                    template_data.append({
                        '设备类型': template.device_type,
                        '品牌': template.brand,
                        '型号': template.model,
                        '系列': template.series or '',
                        '存储容量': ','.join(storages),
                        '是否启用': '是' if template.is_active else '否'
                    })
                    
                    # 该机型的问卷步骤和选项
                    questions = template.questions.filter(is_active=True).order_by('step_order')
                    for question in questions:
                        question_data.append({
                            '设备类型': template.device_type,
                            '品牌': template.brand,
                            '型号': template.model,
                            '步骤顺序': question.step_order,
                            '问题标识': question.key,
                            '问题标题': question.title,
                            '提示文本': question.helper or '',
                            '问题类型': question.question_type,
                            '是否必填': '是' if question.is_required else '否',
                            '是否启用': '是' if question.is_active else '否'
                        })
                        
                        # 该问题的选项（存储容量问题除外，会自动生成）
                        if question.key != 'storage':
                            options = question.options.filter(is_active=True).order_by('option_order', 'id')
                            for option in options:
                                option_data.append({
                                    '设备类型': template.device_type,
                                    '品牌': template.brand,
                                    '型号': template.model,
                                    '问题标识': question.key,
                                    '选项值': option.value,
                                    '选项标签': option.label,
                                    '选项描述': option.desc or '',
                                    '对估价的影响': option.impact or '',
                                    '选项顺序': option.option_order,
                                    '是否启用': '是' if option.is_active else '否'
                                })
            else:
                # 创建空模板（仅示例数据）
                template_data = []
                template_data.append({
                    '设备类型': '手机',
                    '品牌': '苹果',
                    '型号': 'iPhone 15 Pro Max',
                    '系列': '15系列',
                    '存储容量': '128GB,256GB,512GB,1TB',
                    '是否启用': '是'
                })
                
                # 创建问卷步骤数据（示例，使用默认问卷）
                from app.admin_api.management.commands.import_recycle_templates import DEFAULT_QUESTIONS
                question_data = []
                for q in DEFAULT_QUESTIONS:
                    question_data.append({
                        '设备类型': '手机',
                        '品牌': '苹果',
                        '型号': 'iPhone 15 Pro Max',
                        '步骤顺序': q['step_order'],
                        '问题标识': q['key'],
                        '问题标题': q['title'],
                        '提示文本': q.get('helper', ''),
                        '问题类型': q['question_type'],
                        '是否必填': '是' if q['is_required'] else '否',
                        '是否启用': '是'
                    })
                
                # 创建问卷选项数据（示例）
                option_data = []
                for q in DEFAULT_QUESTIONS:
                    if q['key'] == 'storage':
                        continue  # 存储容量选项会自动生成
                    for opt in q.get('options', []):
                        option_data.append({
                            '设备类型': '手机',
                            '品牌': '苹果',
                            '型号': 'iPhone 15 Pro Max',
                            '问题标识': q['key'],
                            '选项值': opt['value'],
                            '选项标签': opt['label'],
                            '选项描述': opt.get('desc', ''),
                            '对估价的影响': opt.get('impact', ''),
                            '选项顺序': opt['option_order'],
                            '是否启用': '是'
                        })
            
            if use_excel:
                # 使用pandas生成Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # 工作表1：机型模板
                    df_templates = pd.DataFrame(template_data)
                    df_templates.to_excel(writer, index=False, sheet_name='机型模板')
                    
                    # 工作表2：问卷步骤（如果有数据）
                    if question_data:
                        df_questions = pd.DataFrame(question_data)
                        df_questions.to_excel(writer, index=False, sheet_name='问卷步骤')
                    
                    # 工作表3：问卷选项（如果有数据）
                    if option_data:
                        df_options = pd.DataFrame(option_data)
                        df_options.to_excel(writer, index=False, sheet_name='问卷选项')
                    
                    # 工作表4：填写说明
                    instructions_text = [
                        '【使用方式】',
                        '方式一：导出现有机型（推荐）',
                        '1. 在管理端页面，点击"导出完整模板"按钮',
                        '2. 系统会导出所有现有机型及其完整问卷配置',
                        '3. 在Excel中修改机型信息或问卷配置',
                        '4. 保存后点击"上传导入"重新导入',
                        '',
                        '方式二：使用空模板',
                        '1. 点击"下载模板"按钮下载空模板',
                        '2. 在"机型模板"工作表中填写机型信息',
                        '3. 如果填写了"问卷步骤"和"问卷选项"工作表，会使用自定义配置',
                        '4. 如果没有填写问卷工作表，会使用默认13步问卷',
                        '',
                        '【机型模板工作表】',
                        '1. 设备类型：手机、平板、笔记本',
                        '2. 品牌：如苹果、华为、小米等',
                        '3. 型号：具体型号名称',
                        '4. 系列：可选，如"15系列"、"Pro系列"',
                        '5. 存储容量：多个容量用逗号分隔，如"128GB,256GB,512GB"',
                        '6. 是否启用：是/否',
                        '',
                        '【问卷步骤工作表】（可选）',
                        '如果填写此工作表，导入时会使用此配置创建问卷，否则使用默认13步问卷',
                        '1. 设备类型、品牌、型号：必须填写，用于指定该问卷配置适用于哪个机型',
                        '2. 步骤顺序：从1开始，控制问题显示顺序',
                        '3. 问题标识：唯一标识，如channel, color, storage',
                        '4. 问题标题：显示给用户的问题文本',
                        '5. 提示文本：辅助说明（可选）',
                        '6. 问题类型：single（单选）或multi（多选）',
                        '7. 是否必填：是/否',
                        '8. 是否启用：是/否',
                        '',
                        '【问卷选项工作表】（可选）',
                        '如果填写问卷步骤，必须填写对应的选项',
                        '1. 设备类型、品牌、型号：必须填写，对应机型模板中的机型',
                        '2. 问题标识：对应问卷步骤中的问题标识',
                        '3. 选项值：唯一标识，如official, black',
                        '4. 选项标签：显示给用户的文本',
                        '5. 选项描述：辅助说明（可选）',
                        '6. 对估价的影响：positive/minor/major/critical（可选）',
                        '7. 选项顺序：控制选项显示顺序',
                        '8. 是否启用：是/否',
                        '',
                        '注意：',
                        '- 存储容量问题的选项会自动从机型模板的存储容量生成',
                        '- 如果机型已存在，会更新存储容量和系列信息',
                        '- 如果提供了问卷配置，会替换现有问卷（如果存在）',
                        '- 每个机型可以有自己独立的问卷配置'
                    ]
                    instructions = pd.DataFrame({'说明': instructions_text})
                    instructions.to_excel(writer, index=False, sheet_name='填写说明')
                
                output.seek(0)
                response = HttpResponse(
                    output.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                if export_existing:
                    response['Content-Disposition'] = 'attachment; filename="机型模板完整导出.xlsx"'
                else:
                    response['Content-Disposition'] = 'attachment; filename="机型模板导入文件.xlsx"'
                return response
            else:
                # 使用CSV格式
                import csv
                response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="机型模板导入文件.csv"'
                
                writer = csv.DictWriter(response, fieldnames=['设备类型', '品牌', '型号', '系列', '存储容量', '是否启用'])
                writer.writeheader()
                writer.writerows(template_data)
                
                return response
        except Exception as e:
            return Response({'detail': f'生成模板文件失败: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RecycleTemplateImportView(APIView):
    """上传文件并批量导入机型模板"""
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['recycle_template:create'])
    def post(self, request):
        admin = request.admin
        
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'detail': '请上传文件'}, status=400)
        
        clear = request.data.get('clear', False)
        
        try:
            from app.admin_api.models import RecycleDeviceTemplate, RecycleQuestionTemplate, RecycleQuestionOption
            from app.admin_api.management.commands.import_recycle_templates import DEFAULT_QUESTIONS
            import io
            
            # 解析文件
            file_content = uploaded_file.read()
            file_name = uploaded_file.name.lower()
            
            devices_data = []
            custom_questions = None  # 自定义问卷步骤
            custom_options = None   # 自定义问卷选项
            
            # 判断文件类型并解析
            if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                try:
                    import pandas as pd
                    excel_file = io.BytesIO(file_content)
                    
                    # 读取机型模板工作表
                    try:
                        df_templates = pd.read_excel(excel_file, sheet_name='机型模板', engine='openpyxl')
                    except ValueError:
                        # 如果没有指定工作表名，读取第一个工作表
                        excel_file.seek(0)
                        df_templates = pd.read_excel(excel_file, engine='openpyxl')
                    
                    # 尝试读取问卷步骤工作表
                    try:
                        excel_file.seek(0)
                        df_questions = pd.read_excel(excel_file, sheet_name='问卷步骤', engine='openpyxl')
                        if not df_questions.empty:
                            custom_questions = df_questions
                    except (ValueError, KeyError):
                        pass  # 没有问卷步骤工作表，使用默认
                    
                    # 尝试读取问卷选项工作表
                    try:
                        excel_file.seek(0)
                        df_options = pd.read_excel(excel_file, sheet_name='问卷选项', engine='openpyxl')
                        if not df_options.empty:
                            custom_options = df_options
                    except (ValueError, KeyError):
                        pass  # 没有问卷选项工作表，使用默认
                    
                    df = df_templates
                except ImportError:
                    return Response({'detail': '系统未安装pandas和openpyxl，无法解析Excel文件。请安装：pip install pandas openpyxl'}, status=500)
                except Exception as e:
                    return Response({'detail': f'解析Excel文件失败: {str(e)}'}, status=400)
            elif file_name.endswith('.csv'):
                try:
                    import pandas as pd
                    df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8-sig')
                except ImportError:
                    import csv
                    import codecs
                    df_data = []
                    csv_reader = csv.DictReader(codecs.iterdecode(io.BytesIO(file_content), 'utf-8-sig'))
                    for row in csv_reader:
                        df_data.append(row)
                    df = pd.DataFrame(df_data)
                except Exception as e:
                    return Response({'detail': f'解析CSV文件失败: {str(e)}'}, status=400)
            else:
                return Response({'detail': '不支持的文件格式，请上传Excel(.xlsx/.xls)或CSV文件'}, status=400)
            
            # 验证必需的列
            required_columns = ['设备类型', '品牌', '型号', '存储容量']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({'detail': f'文件缺少必需的列: {", ".join(missing_columns)}'}, status=400)
            
            # 转换为字典列表
            for _, row in df.iterrows():
                device_type = str(row.get('设备类型', '')).strip()
                brand = str(row.get('品牌', '')).strip()
                model = str(row.get('型号', '')).strip()
                series = str(row.get('系列', '')).strip() if pd.notna(row.get('系列')) else ''
                storages_str = str(row.get('存储容量', '')).strip()
                is_active_str = str(row.get('是否启用', '是')).strip().lower()
                
                if not device_type or not brand or not model or not storages_str:
                    continue  # 跳过空行
                
                # 解析存储容量
                storages = [s.strip() for s in storages_str.split(',') if s.strip()]
                if not storages:
                    continue
                
                # 解析是否启用
                is_active = is_active_str in ['是', 'yes', 'true', '1', '启用']
                
                devices_data.append({
                    'device_type': device_type,
                    'brand': brand,
                    'model': model,
                    'series': series,
                    'storages': storages,
                    'is_active': is_active
                })
            
            if not devices_data:
                return Response({'detail': '文件中没有有效的机型数据'}, status=400)
            
            # 解析自定义问卷配置（支持按机型匹配，支持匹配优先级）
            # questions_config_by_device: {(device_type, brand, model): [questions]}
            questions_config_by_device = {}
            if custom_questions is not None and not custom_questions.empty:
                try:
                    for _, q_row in custom_questions.iterrows():
                        # 获取机型匹配条件（可选，用于灵活匹配）
                        device_type = str(q_row.get('设备类型', '')).strip() if pd.notna(q_row.get('设备类型')) else None
                        brand = str(q_row.get('品牌', '')).strip() if pd.notna(q_row.get('品牌')) else None
                        model = str(q_row.get('型号', '')).strip() if pd.notna(q_row.get('型号')) else None
                        
                        step_order = int(q_row.get('步骤顺序', 0))
                        key = str(q_row.get('问题标识', '')).strip()
                        title = str(q_row.get('问题标题', '')).strip()
                        helper = str(q_row.get('提示文本', '')).strip() if pd.notna(q_row.get('提示文本')) else ''
                        question_type = str(q_row.get('问题类型', 'single')).strip()
                        is_required_str = str(q_row.get('是否必填', '是')).strip().lower()
                        is_active_str = str(q_row.get('是否启用', '是')).strip().lower()
                        
                        if not key or not title:
                            continue
                        
                        # 创建匹配键：如果所有字段都为空，则匹配所有机型；否则按填写情况匹配
                        match_key = (device_type, brand, model)
                        if match_key not in questions_config_by_device:
                            questions_config_by_device[match_key] = []
                        
                        questions_config_by_device[match_key].append({
                            'step_order': step_order,
                            'key': key,
                            'title': title,
                            'helper': helper,
                            'question_type': question_type,
                            'is_required': is_required_str in ['是', 'yes', 'true', '1'],
                            'is_active': is_active_str in ['是', 'yes', 'true', '1', '启用']
                        })
                except Exception as e:
                    return Response({'detail': f'解析问卷步骤配置失败: {str(e)}'}, status=400)
            
            # options_config_by_device: {(device_type, brand, model, question_key): [options]}
            options_config_by_device = {}
            if custom_options is not None and not custom_options.empty:
                try:
                    for _, opt_row in custom_options.iterrows():
                        # 获取机型匹配条件（可选，用于灵活匹配）
                        device_type = str(opt_row.get('设备类型', '')).strip() if pd.notna(opt_row.get('设备类型')) else None
                        brand = str(opt_row.get('品牌', '')).strip() if pd.notna(opt_row.get('品牌')) else None
                        model = str(opt_row.get('型号', '')).strip() if pd.notna(opt_row.get('型号')) else None
                        question_key = str(opt_row.get('问题标识', '')).strip()
                        value = str(opt_row.get('选项值', '')).strip()
                        label = str(opt_row.get('选项标签', '')).strip()
                        desc = str(opt_row.get('选项描述', '')).strip() if pd.notna(opt_row.get('选项描述')) else ''
                        impact = str(opt_row.get('对估价的影响', '')).strip() if pd.notna(opt_row.get('对估价的影响')) else ''
                        option_order = int(opt_row.get('选项顺序', 0))
                        is_active_str = str(opt_row.get('是否启用', '是')).strip().lower()
                        
                        if not question_key or not value or not label:
                            continue
                        
                        # 创建匹配键
                        match_key = (device_type, brand, model, question_key)
                        if match_key not in options_config_by_device:
                            options_config_by_device[match_key] = []
                        
                        options_config_by_device[match_key].append({
                            'value': value,
                            'label': label,
                            'desc': desc,
                            'impact': impact,
                            'option_order': option_order,
                            'is_active': is_active_str in ['是', 'yes', 'true', '1', '启用']
                        })
                except Exception as e:
                    return Response({'detail': f'解析问卷选项配置失败: {str(e)}'}, status=400)
            
            # 清空现有数据（如果指定）
            if clear:
                RecycleQuestionOption.objects.all().delete()
                RecycleQuestionTemplate.objects.all().delete()
                RecycleDeviceTemplate.objects.all().delete()
            
            # 导入数据
            total_templates = 0
            total_questions = 0
            total_options = 0
            errors = []
            
            for device_data in devices_data:
                try:
                    # 创建或更新机型模板
                    template, created = RecycleDeviceTemplate.objects.get_or_create(
                        device_type=device_data['device_type'],
                        brand=device_data['brand'],
                        model=device_data['model'],
                        defaults={
                            'series': device_data['series'],
                            'is_active': device_data['is_active'],
                            'created_by': admin,
                        }
                    )
                    
                    if not created:
                        # 更新现有模板
                        template.series = device_data['series']
                        template.is_active = device_data['is_active']
                        template.save()
                    
                    if created:
                        total_templates += 1
                    
                    # 查找匹配的问卷配置（按优先级：精确匹配 > 品牌匹配 > 设备类型匹配 > 通用匹配 > 默认配置）
                    questions_to_create = None
                    
                    if questions_config_by_device:
                        # 尝试精确匹配（设备类型+品牌+型号）
                        exact_match = (device_data['device_type'], device_data['brand'], device_data['model'])
                        if exact_match in questions_config_by_device:
                            questions_to_create = questions_config_by_device[exact_match]
                        else:
                            # 尝试品牌匹配（设备类型+品牌）
                            brand_match = (device_data['device_type'], device_data['brand'], None)
                            if brand_match in questions_config_by_device:
                                questions_to_create = questions_config_by_device[brand_match]
                            else:
                                # 尝试设备类型匹配（设备类型）
                                device_match = (device_data['device_type'], None, None)
                                if device_match in questions_config_by_device:
                                    questions_to_create = questions_config_by_device[device_match]
                                else:
                                    # 尝试通用匹配（全部为空）
                                    general_match = (None, None, None)
                                    if general_match in questions_config_by_device:
                                        questions_to_create = questions_config_by_device[general_match]
                    
                    # 如果找到了匹配的配置，删除现有问卷并重新创建
                    if questions_to_create is not None:
                        template.questions.all().delete()
                    
                    # 如果模板还没有问卷，创建问卷
                    if not template.questions.exists():
                        # 使用匹配的自定义配置或默认配置
                        if questions_to_create is None:
                            questions_to_create = DEFAULT_QUESTIONS
                        
                        for q_data in questions_to_create:
                            question_key = q_data.get('key') if isinstance(q_data, dict) else q_data['key']
                            
                            # 处理存储容量问题（特殊处理，选项从机型存储容量生成）
                            if question_key == 'storage':
                                question = RecycleQuestionTemplate.objects.create(
                                    device_template=template,
                                    step_order=q_data.get('step_order', 3) if isinstance(q_data, dict) else q_data.get('step_order', 3),
                                    key='storage',
                                    title=q_data.get('title', '内存 / 存储') if isinstance(q_data, dict) else q_data.get('title', '内存 / 存储'),
                                    helper=q_data.get('helper', '选容量以便精准估价') if isinstance(q_data, dict) else q_data.get('helper', '选容量以便精准估价'),
                                    question_type=q_data.get('question_type', 'single') if isinstance(q_data, dict) else q_data.get('question_type', 'single'),
                                    is_required=q_data.get('is_required', True) if isinstance(q_data, dict) else q_data.get('is_required', True),
                                    is_active=q_data.get('is_active', True) if isinstance(q_data, dict) else q_data.get('is_active', True),
                                )
                                # 为存储容量问题创建选项（从机型存储容量生成）
                                for idx, storage in enumerate(device_data['storages']):
                                    RecycleQuestionOption.objects.create(
                                        question_template=question,
                                        value=storage.lower().replace('gb', 'gb').replace('tb', 'tb'),
                                        label=storage,
                                        desc='',
                                        impact='',
                                        option_order=idx,
                                        is_active=True,
                                    )
                                    total_options += 1
                            else:
                                # 普通问题
                                question = RecycleQuestionTemplate.objects.create(
                                    device_template=template,
                                    step_order=q_data.get('step_order') if isinstance(q_data, dict) else q_data['step_order'],
                                    key=question_key,
                                    title=q_data.get('title') if isinstance(q_data, dict) else q_data['title'],
                                    helper=q_data.get('helper', '') if isinstance(q_data, dict) else q_data.get('helper', ''),
                                    question_type=q_data.get('question_type', 'single') if isinstance(q_data, dict) else q_data.get('question_type', 'single'),
                                    is_required=q_data.get('is_required', True) if isinstance(q_data, dict) else q_data.get('is_required', True),
                                    is_active=q_data.get('is_active', True) if isinstance(q_data, dict) else q_data.get('is_active', True),
                                )
                                total_questions += 1
                                
                                # 查找匹配的选项配置（按优先级匹配）
                                opts_to_create = []
                                
                                if options_config_by_device:
                                    # 尝试精确匹配（设备类型+品牌+型号+问题标识）
                                    exact_match = (device_data['device_type'], device_data['brand'], device_data['model'], question_key)
                                    if exact_match in options_config_by_device:
                                        opts_to_create = options_config_by_device[exact_match]
                                    else:
                                        # 尝试品牌匹配（设备类型+品牌+问题标识）
                                        brand_match = (device_data['device_type'], device_data['brand'], None, question_key)
                                        if brand_match in options_config_by_device:
                                            opts_to_create = options_config_by_device[brand_match]
                                        else:
                                            # 尝试设备类型匹配（设备类型+问题标识）
                                            device_match = (device_data['device_type'], None, None, question_key)
                                            if device_match in options_config_by_device:
                                                opts_to_create = options_config_by_device[device_match]
                                            else:
                                                # 尝试通用匹配（全部为空+问题标识）
                                                general_match = (None, None, None, question_key)
                                                if general_match in options_config_by_device:
                                                    opts_to_create = options_config_by_device[general_match]
                                
                                # 如果没有找到匹配的选项配置，使用默认配置中的选项
                                if not opts_to_create:
                                    if isinstance(q_data, dict) and 'options' in q_data and q_data['options']:
                                        opts_to_create = q_data['options']
                                    else:
                                        opts_to_create = q_data.get('options', []) if isinstance(q_data, dict) else []
                                
                                for opt_data in opts_to_create:
                                    RecycleQuestionOption.objects.create(
                                        question_template=question,
                                        value=opt_data.get('value') if isinstance(opt_data, dict) else opt_data['value'],
                                        label=opt_data.get('label') if isinstance(opt_data, dict) else opt_data['label'],
                                        desc=opt_data.get('desc', '') if isinstance(opt_data, dict) else opt_data.get('desc', ''),
                                        impact=opt_data.get('impact', '') if isinstance(opt_data, dict) else opt_data.get('impact', ''),
                                        option_order=opt_data.get('option_order', 0) if isinstance(opt_data, dict) else opt_data.get('option_order', 0),
                                        is_active=opt_data.get('is_active', True) if isinstance(opt_data, dict) else opt_data.get('is_active', True),
                                    )
                                    total_options += 1
                except Exception as e:
                    errors.append(f"{device_data['brand']} {device_data['model']}: {str(e)}")
            
            result = {
                'success': True,
                'message': '导入完成',
                'statistics': {
                    'templates': total_templates,
                    'questions': total_questions,
                    'options': total_options,
                    'total_devices': len(devices_data)
                }
            }
            
            if errors:
                result['errors'] = errors
                result['error_count'] = len(errors)
            
            return Response(result)
        except Exception as e:
            import traceback
            return Response({'detail': f'导入失败: {str(e)}', 'traceback': traceback.format_exc()}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RecycleQuestionTemplateView(APIView):
    """问卷步骤模板管理"""
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['recycle_template:view'])
    def get(self, request, template_id, question_id=None):
        admin = request.admin
        
        try:
            device_template = RecycleDeviceTemplate.objects.get(id=template_id)
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '机型模板不存在'}, status=404)
        
        if question_id:
            # 获取单个问题详情
            try:
                question = RecycleQuestionTemplate.objects.get(id=question_id, device_template=device_template)
                serializer = RecycleQuestionTemplateSerializer(question)
                return Response(serializer.data)
            except RecycleQuestionTemplate.DoesNotExist:
                return Response({'detail': '问题不存在'}, status=404)
        else:
            # 获取问题列表
            questions = RecycleQuestionTemplate.objects.filter(device_template=device_template).order_by('step_order')
            serializer = RecycleQuestionTemplateSerializer(questions, many=True)
            return Response({'results': serializer.data})
    
    @admin_required(['recycle_template:create'])
    def post(self, request, template_id):
        """创建问题"""
        admin = request.admin
        
        try:
            device_template = RecycleDeviceTemplate.objects.get(id=template_id)
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '机型模板不存在'}, status=404)
        
        data = request.data.copy()
        data['device_template'] = template_id
        
        serializer = RecycleQuestionTemplateSerializer(data=data)
        if serializer.is_valid():
            serializer.save(device_template=device_template)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    @admin_required(['recycle_template:update'])
    def put(self, request, template_id, question_id):
        """更新问题"""
        admin = request.admin
        
        try:
            device_template = RecycleDeviceTemplate.objects.get(id=template_id)
            question = RecycleQuestionTemplate.objects.get(id=question_id, device_template=device_template)
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '机型模板不存在'}, status=404)
        except RecycleQuestionTemplate.DoesNotExist:
            return Response({'detail': '问题不存在'}, status=404)
        
        serializer = RecycleQuestionTemplateSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @admin_required(['recycle_template:delete'])
    def delete(self, request, template_id, question_id):
        """删除问题"""
        admin = request.admin
        
        try:
            device_template = RecycleDeviceTemplate.objects.get(id=template_id)
            question = RecycleQuestionTemplate.objects.get(id=question_id, device_template=device_template)
            question.delete()
            return Response({'success': True})
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '机型模板不存在'}, status=404)
        except RecycleQuestionTemplate.DoesNotExist:
            return Response({'detail': '问题不存在'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class RecycleQuestionOptionView(APIView):
    """问卷选项管理"""
    authentication_classes = []
    permission_classes = []
    
    @admin_required(['recycle_template:view'])
    def get(self, request, template_id, question_id, option_id=None):
        admin = request.admin
        
        try:
            device_template = RecycleDeviceTemplate.objects.get(id=template_id)
            question = RecycleQuestionTemplate.objects.get(id=question_id, device_template=device_template)
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '机型模板不存在'}, status=404)
        except RecycleQuestionTemplate.DoesNotExist:
            return Response({'detail': '问题不存在'}, status=404)
        
        if option_id:
            # 获取单个选项详情
            try:
                option = RecycleQuestionOption.objects.get(id=option_id, question_template=question)
                serializer = RecycleQuestionOptionSerializer(option)
                return Response(serializer.data)
            except RecycleQuestionOption.DoesNotExist:
                return Response({'detail': '选项不存在'}, status=404)
        else:
            # 获取选项列表
            options = RecycleQuestionOption.objects.filter(question_template=question).order_by('option_order', 'id')
            serializer = RecycleQuestionOptionSerializer(options, many=True)
            return Response({'results': serializer.data})
    
    @admin_required(['recycle_template:create'])
    def post(self, request, template_id, question_id):
        """创建选项"""
        admin = request.admin
        
        try:
            device_template = RecycleDeviceTemplate.objects.get(id=template_id)
            question = RecycleQuestionTemplate.objects.get(id=question_id, device_template=device_template)
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '机型模板不存在'}, status=404)
        except RecycleQuestionTemplate.DoesNotExist:
            return Response({'detail': '问题不存在'}, status=404)
        
        data = request.data.copy()
        data['question_template'] = question_id
        
        serializer = RecycleQuestionOptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(question_template=question)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    @admin_required(['recycle_template:update'])
    def put(self, request, template_id, question_id, option_id):
        """更新选项"""
        admin = request.admin
        
        try:
            device_template = RecycleDeviceTemplate.objects.get(id=template_id)
            question = RecycleQuestionTemplate.objects.get(id=question_id, device_template=device_template)
            option = RecycleQuestionOption.objects.get(id=option_id, question_template=question)
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '机型模板不存在'}, status=404)
        except RecycleQuestionTemplate.DoesNotExist:
            return Response({'detail': '问题不存在'}, status=404)
        except RecycleQuestionOption.DoesNotExist:
            return Response({'detail': '选项不存在'}, status=404)
        
        serializer = RecycleQuestionOptionSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @admin_required(['recycle_template:delete'])
    def delete(self, request, template_id, question_id, option_id):
        """删除选项"""
        admin = request.admin
        
        try:
            device_template = RecycleDeviceTemplate.objects.get(id=template_id)
            question = RecycleQuestionTemplate.objects.get(id=question_id, device_template=device_template)
            option = RecycleQuestionOption.objects.get(id=option_id, question_template=question)
            option.delete()
            return Response({'success': True})
        except RecycleDeviceTemplate.DoesNotExist:
            return Response({'detail': '机型模板不存在'}, status=404)
        except RecycleQuestionTemplate.DoesNotExist:
            return Response({'detail': '问题不存在'}, status=404)
        except RecycleQuestionOption.DoesNotExist:
            return Response({'detail': '选项不存在'}, status=404)
