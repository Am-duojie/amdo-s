from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app.secondhand_app import views
from app.secondhand_app import payment_views
from app.secondhand_app.jwt import CustomTokenObtainPairView

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
    path('api/recycle-catalog/', views.RecycleCatalogView.as_view(), name='recycle_catalog'),
    path('api/geo/districts/', views.GeoDistrictsView.as_view(), name='geo_districts'),
    path('api/products/recommend/', views.RecommendProductsView.as_view(), name='products_recommend'),
    path('api/products/latest/', views.LatestProductsView.as_view(), name='products_latest'),
    path('api/products/nearby/', views.NearbyProductsView.as_view(), name='products_nearby'),
    path('api/products/low-price/', views.LowPriceProductsView.as_view(), name='products_low_price'),
    path('api/recycle-templates/question-template/', views.RecycleQuestionTemplateView.as_view(), name='recycle_question_template'),
    path('api/geo/ip/', views.GeoIpView.as_view(), name='geo_ip'),
    path('api/', include(router.urls)),
    path('admin-api/', include('app.admin_api.urls')),
    # 使用SimpleJWT进行认证
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 支付相关路由（支付宝支付）
    path('api/payment/create/', payment_views.create_payment, name='create_payment'),
    path('api/payment/create-url/', payment_views.create_payment_url, name='create_payment_url'),
    path('api/payment/query/<int:order_id>/', payment_views.query_payment, name='query_payment'),
    path('api/payment/redirect/', payment_views.payment_redirect, name='payment_redirect'),
    path('api/payment/alipay/notify/', payment_views.alipay_payment_notify, name='alipay_payment_notify'),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
