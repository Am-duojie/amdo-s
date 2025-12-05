import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
from .models import AdminUser, AdminRole, AdminInspectionReport, AdminAuditQueueItem, AdminAuditLog, AdminRefreshToken, AdminTokenBlacklist
from app.secondhand_app.models import RecycleOrder, VerifiedProduct, VerifiedOrder, Order, Shop, Category, Product, Message, Address
from app.secondhand_app.easypay import EasyPayClient
from .serializers import AdminUserSerializer, RecycleOrderListSerializer, VerifiedProductListSerializer, AdminAuditQueueItemSerializer, ShopAdminSerializer
from .jwt import encode as jwt_encode, decode as jwt_decode
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def get_admin_from_request(request):
    auth = request.headers.get('Authorization','')
    if not auth.startswith('Bearer '):
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
    except Exception:
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
class LoginView(APIView):
    permission_classes = [AllowAny]
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
        refresh_token = request.data.get('refresh_token', '').strip()
        if not refresh_token:
            return Response({'detail': 'refresh_token required'}, status=400)
        try:
            rt_obj = AdminRefreshToken.objects.get(token=refresh_token, revoked=False)
            if rt_obj.expires_at < timezone.now():
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

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
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
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        user_data = AdminUserSerializer(admin).data
        return Response({'user': user_data})

@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(APIView):
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
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        perms = admin.role.permissions if admin.role else []
        return Response({'permissions': perms})

@method_decorator(csrf_exempt, name='dispatch')
class MenusView(APIView):
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
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        status_filter = request.query_params.get('status', '')
        search = request.query_params.get('search', '').strip()
        qs = RecycleOrder.objects.select_related('user').all().order_by('-created_at')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if search:
            qs = qs.filter(Q(user__username__icontains=search) | Q(brand__icontains=search) | Q(model__icontains=search) | Q(id__icontains=search))
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{
            'id': o.id,
            'user': {'id': o.user.id, 'username': o.user.username},
            'status': o.status,
            'device_type': o.device_type,
            'brand': o.brand,
            'model': o.model,
            'storage': o.storage or '',
            'condition': o.condition,
            'estimated_price': float(o.estimated_price) if o.estimated_price else None,
            'final_price': float(o.final_price) if o.final_price else None,
            'created_at': o.created_at.isoformat()
        } for o in items]
        return Response({'results': data, 'count': total})

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderDetailView(APIView):
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
        return Response({'success': True, 'item': {
            'id': o.id,
            'user': {'id': o.user.id, 'username': o.user.username},
            'status': o.status,
            'device_type': o.device_type,
            'brand': o.brand,
            'model': o.model,
            'storage': o.storage or '',
            'condition': o.condition,
            'estimated_price': float(o.estimated_price) if o.estimated_price else None,
            'final_price': float(o.final_price) if o.final_price else None,
            'bonus': float(o.bonus) if o.bonus else 0,
            'contact_name': o.contact_name,
            'contact_phone': o.contact_phone,
            'address': o.address,
            'note': o.note or '',
            'created_at': o.created_at.isoformat(),
            'updated_at': o.updated_at.isoformat(),
            'appointment_at': None,
            'report': {'check_items': (rep.check_items if rep else {}), 'remarks': (rep.remarks if rep else ''), 'created_at': (rep.created_at.isoformat() if rep else None)}
        }})
    def put(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        status_val = request.query_params.get('status')
        try:
            o = RecycleOrder.objects.get(id=order_id)
            o.status = status_val
            o.save()
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
        try:
            o = RecycleOrder.objects.get(id=order_id)
        except RecycleOrder.DoesNotExist:
            return Response({'success': False})
        AdminInspectionReport.objects.create(order=o, check_items=items, remarks=remarks)
        if o.status == 'shipped':
            o.status = 'inspected'
            o.save()
        AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='inspection_report', snapshot_json={'status': o.status})
        return Response({'success': True})

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderLogisticsView(APIView):
    def post(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        carrier = request.data.get('carrier', '').strip()
        tracking_number = request.data.get('tracking_number', '').strip()
        if not carrier or not tracking_number:
            return Response({'success': False, 'detail': '物流公司和运单号不能为空'}, status=400)
        try:
            o = RecycleOrder.objects.get(id=order_id)
            o.status = 'shipped'
            o.save()
            AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='logistics', snapshot_json={'carrier': carrier, 'tracking_number': tracking_number, 'status': o.status})
            return Response({'success': True})
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': '订单不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderPriceView(APIView):
    def put(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        final_price = request.data.get('final_price')
        bonus = request.data.get('bonus', 0)
        if final_price is None:
            return Response({'success': False, 'detail': '最终价格不能为空'}, status=400)
        try:
            final_price = float(final_price)
            bonus = float(bonus) if bonus else 0
        except (ValueError, TypeError):
            return Response({'success': False, 'detail': '价格格式错误'}, status=400)
        try:
            o = RecycleOrder.objects.get(id=order_id)
            o.final_price = final_price
            o.bonus = bonus
            o.save()
            AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='update_price', snapshot_json={'final_price': float(final_price), 'bonus': float(bonus)})
            return Response({'success': True})
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': '订单不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderPaymentView(APIView):
    def post(self, request, order_id):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['inspection:write']):
            return Response({'detail': 'Forbidden'}, status=403)
        payment_method = request.data.get('payment_method', 'bank')
        note = request.data.get('note', '')
        try:
            o = RecycleOrder.objects.get(id=order_id)
            if not o.final_price:
                return Response({'success': False, 'detail': '订单尚未确定最终价格'}, status=400)
            if o.status != 'completed':
                return Response({'success': False, 'detail': '订单状态不正确'}, status=400)
            AdminAuditLog.objects.create(actor=admin, target_type='RecycleOrder', target_id=o.id, action='payment', snapshot_json={'amount': float(o.final_price), 'payment_method': payment_method, 'note': note})
            return Response({'success': True, 'message': '打款成功'})
        except RecycleOrder.DoesNotExist:
            return Response({'success': False, 'detail': '订单不存在'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class InspectionOrderPublishVerifiedView(APIView):
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

# 回收商品相关视图
@method_decorator(csrf_exempt, name='dispatch')
class RecycledProductsView(APIView):
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
    def get(self, request):
        admin = get_admin_from_request(request)
        if not admin:
            return Response({'detail': 'Unauthorized'}, status=401)
        if not has_perms(admin, ['payment:view']):
            return Response({'detail': 'Forbidden'}, status=403)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        status_filter = request.query_params.get('status', '')
        qs = Order.objects.all().order_by('-created_at')
        if status_filter:
            qs = qs.filter(status=status_filter)
        total = qs.count()
        items = qs[(page-1)*page_size: page*page_size]
        data = [{
            'id': o.id,
            'product': o.product.title if o.product else '',
            'buyer': o.buyer.username if o.buyer else '',
            'total_price': float(o.total_price),
            'status': o.status,
            'created_at': o.created_at.isoformat()
        } for o in items]
        return Response({'results': data, 'count': total})

@method_decorator(csrf_exempt, name='dispatch')
class PaymentOrderActionView(APIView):
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
            client = EasyPayClient()
            result = client.query(order_id)
            return Response({'success': True, 'result': result})
        elif action == 'refund':
            if not has_perms(admin, ['payment:write']):
                return Response({'detail': 'Forbidden'}, status=403)
            client = EasyPayClient()
            result = client.refund(order_id, float(o.total_price))
            ok = (result.get('code') == 1)
            if ok:
                AdminAuditLog.objects.create(actor=admin, target_type='Order', target_id=o.id, action='refund', snapshot_json={'amount': float(o.total_price)})
            return Response({'success': ok, 'result': result})
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

# 官方验订单相关视图
@method_decorator(csrf_exempt, name='dispatch')
class VerifiedOrdersAdminView(APIView):
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

