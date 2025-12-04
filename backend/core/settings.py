from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-secondhand-platform-secret-key-2024'

DEBUG = True  # 开发模式
ALLOWED_HOSTS = ['*']

# 应用列表
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    'app.secondhand_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'secondhand_platform',
        'USER': 'root',
        'PASSWORD': '123456',  # MySQL密码
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件和媒体文件
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'app.secondhand_app.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}

# CORS 配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

CORS_ALLOW_CREDENTIALS = True

# Redis Channel Layer (用于WebSocket)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# ==================== 第三方估价API配置 ====================
# 是否启用第三方API（设置为True后才会调用第三方接口）
PRICE_API_ENABLED = False

# API提供商: 'local'（本地价格表）, 'aihuishou'（爱回收）, 'huishoubao'（回收宝）, 'custom'（自定义）
PRICE_API_PROVIDER = 'local'

# 价格缓存时间（秒），默认1小时
PRICE_CACHE_TIMEOUT = 3600

# 爱回收API配置（需要联系爱回收获取）
AIHUISHOU_API_URL = ''  # 例如: 'https://api.aihuishou.com/v1/estimate'
AIHUISHOU_API_KEY = ''
AIHUISHOU_API_SECRET = ''

# 回收宝API配置（需要联系回收宝获取）
HUISHOUBAO_API_URL = ''  # 例如: 'https://api.huishoubao.com/v1/price'
HUISHOUBAO_API_KEY = ''
HUISHOUBAO_API_SECRET = ''

# 自定义API配置（通用配置，支持任何第三方API）
CUSTOM_PRICE_API_URL = ''  # 您的API端点
CUSTOM_PRICE_API_KEY = ''  # API密钥（如果需要）
CUSTOM_PRICE_API_METHOD = 'POST'  # 请求方法: 'GET' 或 'POST'
CUSTOM_PRICE_API_AUTH_TYPE = 'bearer'  # 认证类型: 'bearer', 'header', 'query'

# ==================== 公开API服务配置 ====================
# 启用公开API服务（推荐使用）
ENABLE_PUBLIC_API = False  # 是否启用公开API服务

# 聚合数据API配置（推荐）
# 注册地址：https://www.juhe.cn
JUHE_API_KEY = ''  # 聚合数据API密钥
JUHE_PRICE_API_URL = ''  # 价格查询API地址（需要根据实际API文档配置）

# RapidAPI配置
# 注册地址：https://rapidapi.com
RAPIDAPI_KEY = ''  # RapidAPI密钥
RAPIDAPI_HOST = ''  # API Host
RAPIDAPI_PRICE_API_URL = ''  # 价格查询API地址

# 百度API配置
BAIDU_API_KEY = ''  # 百度API密钥
BAIDU_PRICE_API_URL = ''  # 价格查询API地址

# 阿里云API配置
ALIYUN_API_KEY = ''  # 阿里云API密钥
ALIYUN_API_SECRET = ''  # 阿里云API密钥
ALIYUN_PRICE_API_URL = ''  # 价格查询API地址

# API Store配置
APISPACE_API_KEY = ''  # API Store密钥
APISPACE_PRICE_API_URL = ''  # 价格查询API地址

# ⚠️ 爬取服务配置（仅供学习研究，不推荐用于生产环境）
# 警告：爬取第三方平台可能违反服务条款和法律，请谨慎使用
ENABLE_PRICE_SCRAPER = False  # 是否启用爬取服务

# 手动配置的API端点（如果找到了实际的API地址，可以在这里配置）
SCRAPER_API_URL = ''  # 例如: 'https://www.aihuishou.com/api/v1/estimate'
SCRAPER_API_METHOD = 'POST'  # GET 或 POST
SCRAPER_API_KEY = ''  # API密钥（如果需要）
SCRAPER_API_SECRET = ''  # API密钥（如果需要）

# ========== 易支付配置 ==========
# 支付平台：https://pay.myzfw.com/
# 文档地址：https://pay.myzfw.com/doc_old.html

# 易支付接口地址
EASYPAY_SUBMIT_URL = 'https://pay.myzfw.com/submit.php'  # 页面跳转支付
EASYPAY_MAPI_URL = 'https://pay.myzfw.com/mapi.php'      # API接口支付
EASYPAY_API_URL = 'https://pay.myzfw.com/api.php'        # 查询/退款接口

# 商户信息（必填）- 在后台 https://pay.myzfw.com/ 获取
EASYPAY_PID = '16839'  # 商户ID
EASYPAY_KEY = '0y5917ysBs509870GF97v1epG7f9E978'  # 商户密钥（MD5密钥）

# 回调地址配置
EASYPAY_NOTIFY_URL = 'http://127.0.0.1:8000/api/payment/notify/'  # 异步通知地址（本地测试用，生产环境需改为公网地址）
EASYPAY_RETURN_URL = 'http://localhost:5173/order/'  # 支付完成跳转地址

# 演示模式（仅用于测试界面，不进行真实支付）
EASYPAY_DEMO_MODE = False  # True=演示模式, False=真实支付（当前：真实支付）