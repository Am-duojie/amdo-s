"""
生产环境配置文件
从开发配置继承，覆盖关键设置
"""
from .settings import *
import os

# ==================== 安全设置 ====================
DEBUG = False  # 关闭调试模式（必须）
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-secondhand-platform-secret-key-2024-change-in-production')

# 允许的主机（必须配置你的域名或内网穿透域名）
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    # 添加你的外网访问地址（内网穿透域名或公网IP）
    # 例如：'xxxx.ngrok-free.app', 'xxxx.natapp.cc'
    # 可以使用通配符：'*.ngrok.io'
]

# ==================== 数据库配置 ====================
# 生产环境建议从环境变量读取敏感信息
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'secondhand_platform'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '123456'),  # 建议从环境变量读取
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# ==================== CORS 配置 ====================
# 允许跨域的来源（必须包含你的前端地址）
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # 添加你的前端外网地址（内网穿透域名）
    # 例如：'https://xxxx.ngrok-free.app'
]

# 如果需要允许所有来源（仅测试时使用，生产环境不推荐）
# CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

# ==================== 静态文件和媒体文件 ====================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==================== Redis Channel Layer (WebSocket) ====================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# ==================== 易支付配置 ====================
# 支付回调地址（必须改为你的公网可访问地址）
# 使用内网穿透时，替换为内网穿透的地址
EASYPAY_NOTIFY_URL = os.environ.get(
    'EASYPAY_NOTIFY_URL',
    'https://你的域名/api/payment/notify/'  # 替换为实际地址
)
EASYPAY_RETURN_URL = os.environ.get(
    'EASYPAY_RETURN_URL',
    'https://你的域名/order/'  # 替换为实际地址
)

# ==================== 日志配置 ====================
# 生产环境建议启用日志记录
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 确保日志目录存在
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# ==================== 其他生产环境优化 ====================
# 会话安全设置
SESSION_COOKIE_SECURE = False  # 使用 HTTPS 时设置为 True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # 使用 HTTPS 时设置为 True

# 安全头部
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 数据库连接池（可选，提高性能）
# DATABASES['default']['CONN_MAX_AGE'] = 600

print("=" * 50)
print("生产环境配置已加载")
print("DEBUG =", DEBUG)
print("ALLOWED_HOSTS =", ALLOWED_HOSTS)
print("=" * 50)




