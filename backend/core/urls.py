from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from app.secondhand_app import views
from app.secondhand_app import payment_views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'recycle-orders', views.RecycleOrderViewSet, basename='recycle-order')
router.register(r'verified-products', views.VerifiedProductViewSet, basename='verified-product')
router.register(r'verified-orders', views.VerifiedOrderViewSet, basename='verified-order')
router.register(r'verified-favorites', views.VerifiedFavoriteViewSet, basename='verified-favorite')

def api_root(request):
    """API根路径，返回API信息"""
    return JsonResponse({
        'message': '二手交易平台 API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'api_docs': '/api/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('admin-api/', include('app.admin_api.urls')),
    # 保留原有的token认证端点
    path('api/auth/login/', obtain_auth_token, name='api_token_auth'),
    # 易支付相关路由
    path('api/payment/create/', payment_views.create_payment, name='create_payment'),
    path('api/payment/create-url/', payment_views.create_payment_url, name='create_payment_url'),
    path('api/payment/notify/', payment_views.payment_notify, name='payment_notify'),
    path('api/payment/query/<int:order_id>/', payment_views.query_payment, name='query_payment'),
    path('api/payment/refund/<int:order_id>/', payment_views.refund_payment, name='refund_payment'),
    path('api/payment/demo-complete/<int:order_id>/', payment_views.demo_complete_payment, name='demo_complete_payment'),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
