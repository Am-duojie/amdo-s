# 支付宝支付接口开发指南

## 目录

1. [概述](#概述)
2. [技术原理](#技术原理)
3. [开发环境准备](#开发环境准备)
4. [代码实现](#代码实现)
5. [配置说明](#配置说明)
6. [接口使用](#接口使用)
7. [常见问题](#常见问题)
8. [最佳实践](#最佳实践)

---

## 概述

本文档详细说明如何在 Django 项目中集成支付宝电脑网站支付功能。支付宝电脑网站支付适用于 PC 端网站，用户点击支付后跳转到支付宝收银台完成支付。

### 支付流程

```
用户下单 → 创建支付订单 → 跳转支付宝收银台 → 用户支付 → 支付成功回调 → 更新订单状态
```

### 核心接口

- **创建支付订单**：`alipay.trade.page.pay` - 生成支付URL，用户跳转支付
- **查询支付状态**：`alipay.trade.query` - 查询订单支付状态
- **异步通知**：接收支付宝支付结果通知

---

## 技术原理

### 1. 签名算法（RSA2）

支付宝使用 RSA2 签名算法（SHA256withRSA）确保请求的安全性和完整性。

#### 签名计算步骤

1. **筛选参数**：
   - 获取所有请求参数
   - **只排除 `sign` 参数**（不参与签名）
   - **`sign_type` 必须参与签名**（重要！）
   - 排除空值（None、空字符串）

2. **排序**：
   - 按照参数名 ASCII 码从小到大排序（字典序）

3. **拼接**：
   - 将排序后的参数与其对应值，组合成 `参数=参数值` 的格式
   - 用 `&` 字符连接起来

4. **签名**：
   - 使用 SHA256 计算哈希值
   - 使用应用私钥进行 RSA2 签名
   - Base64 编码签名结果

#### 签名示例

```python
# 原始参数
params = {
    'app_id': '9021000158624650',
    'method': 'alipay.trade.page.pay',
    'charset': 'utf-8',
    'sign_type': 'RSA2',  # 注意：sign_type 参与签名
    'timestamp': '2025-12-06 21:39:56',
    'version': '1.0',
    'biz_content': '{"out_trade_no":"normal_90",...}',
    'notify_url': 'http://127.0.0.1:8000/api/payment/alipay/notify/',
    'return_url': 'http://localhost:5173/order/90',
}

# 筛选并排序（排除 sign，保留 sign_type）
filtered = {k: v for k, v in params.items() if k != 'sign' and v}
sorted_params = sorted(filtered.items())

# 拼接签名字符串
sign_str = '&'.join([f'{k}={v}' for k, v in sorted_params])
# 结果：app_id=9021000158624650&biz_content={...}&charset=utf-8&method=alipay.trade.page.pay&notify_url=...&return_url=...&sign_type=RSA2&timestamp=...&version=1.0

# 签名
hash_obj = SHA256.new(sign_str.encode('utf-8'))
signature = private_key.sign(hash_obj)
sign = base64.b64encode(signature).decode('utf-8')
```

### 2. 密钥体系

支付宝使用非对称加密（RSA）确保通信安全：

- **应用私钥**：商户自己生成，用于签名请求
- **应用公钥**：从应用私钥生成，上传到支付宝平台
- **支付宝公钥**：支付宝返回，用于验证支付宝的响应

```
商户端：使用应用私钥签名 → 发送请求
支付宝：使用应用公钥验签 → 处理请求 → 使用支付宝私钥签名 → 返回响应
商户端：使用支付宝公钥验签 → 处理响应
```

### 3. 请求参数结构

#### 顶层参数

```python
{
    'app_id': '应用ID',
    'method': 'alipay.trade.page.pay',  # 接口名称
    'charset': 'utf-8',  # 编码格式
    'sign_type': 'RSA2',  # 签名类型
    'timestamp': '2025-12-06 21:39:56',  # 时间戳
    'version': '1.0',  # 接口版本
    'biz_content': '{"out_trade_no":"...",...}',  # 业务参数（JSON字符串）
    'return_url': '支付成功跳转地址',  # 可选
    'notify_url': '异步通知地址',  # 可选
    'sign': '签名结果'  # 最后添加
}
```

#### 业务参数（biz_content）

```json
{
    "out_trade_no": "商户订单号",
    "product_code": "FAST_INSTANT_TRADE_PAY",
    "total_amount": "195.00",
    "subject": "订单标题"
}
```

**注意**：
- `biz_content` 必须是 JSON 字符串格式
- `return_url` 和 `notify_url` 作为顶层参数，不在 `biz_content` 中
- 金额格式：保留两位小数，字符串格式

---

## 开发环境准备

### 1. 安装依赖

```bash
pip install pycryptodome==3.20.0
```

### 2. 注册支付宝开放平台账号

1. 访问 https://open.alipay.com/
2. 使用支付宝账号登录
3. 完成企业实名认证（生产环境需要）

### 3. 创建应用

1. 进入控制台 → 网页&移动应用
2. 创建应用，填写应用信息
3. 获取 **APPID**

### 4. 生成密钥对

#### 方法一：使用支付宝密钥生成工具（推荐）

1. 下载支付宝密钥生成工具
2. 选择 RSA2（2048位）
3. 生成密钥对

#### 方法二：使用 OpenSSL

```bash
# 生成私钥（2048位）
openssl genrsa -out app_private_key.pem 2048

# 生成公钥
openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem
```

### 5. 配置密钥

1. 在应用详情页，点击"接口加签方式" → "设置"
2. 选择"公钥"模式
3. 上传应用公钥（从私钥生成）
4. 保存后，获取支付宝返回的"支付宝公钥"

---

## 代码实现

### 1. 支付宝客户端类（`alipay_client.py`）

#### 核心方法

```python
class AlipayClient:
    """支付宝支付客户端"""
    
    def __init__(self):
        """初始化，从 settings 读取配置"""
        self.app_id = settings.ALIPAY_APP_ID
        self.app_private_key = settings.ALIPAY_APP_PRIVATE_KEY
        self.alipay_public_key = settings.ALIPAY_PUBLIC_KEY
        self.gateway_url = settings.ALIPAY_GATEWAY_URL
    
    def _sign(self, data):
        """RSA2 签名"""
        # 1. 筛选参数（只排除 sign）
        # 2. 排序
        # 3. 拼接
        # 4. SHA256 哈希
        # 5. RSA2 签名
        # 6. Base64 编码
        pass
    
    def create_trade(self, out_trade_no, subject, total_amount, 
                     return_url=None, notify_url=None):
        """创建支付订单"""
        # 1. 构建 biz_content
        # 2. 构建请求参数
        # 3. 生成签名
        # 4. 构建支付URL
        pass
    
    def verify_notify(self, params):
        """验证支付通知签名"""
        pass
```

#### 关键实现细节

**签名计算**：

```python
def _sign(self, data):
    """使用RSA2签名"""
    # 关键：只排除 sign，sign_type 必须参与签名
    filtered_data = {}
    for k, v in data.items():
        if k == 'sign':  # 只排除 sign
            continue
        if v is None or v == '':
            continue
        filtered_data[k] = str(v)
    
    # 按字典序排序
    sorted_data = sorted(filtered_data.items())
    
    # 拼接签名字符串
    sign_str = '&'.join([f'{k}={v}' for k, v in sorted_data])
    
    # SHA256 哈希
    hash_obj = SHA256.new(sign_str.encode('utf-8'))
    
    # RSA2 签名
    signer = pkcs1_15.new(private_key)
    signature = signer.sign(hash_obj)
    
    # Base64 编码
    sign = base64.b64encode(signature).decode('utf-8')
    return sign
```

**创建支付订单**：

```python
def create_trade(self, out_trade_no, subject, total_amount, 
                 return_url=None, notify_url=None):
    """创建交易订单（电脑网站支付）"""
    # 构建业务参数
    biz_content = {
        'out_trade_no': str(out_trade_no),
        'product_code': 'FAST_INSTANT_TRADE_PAY',
        'total_amount': f'{float(total_amount):.2f}',
        'subject': str(subject)[:256],
    }
    
    # 构建请求参数
    params = {
        'app_id': self.app_id,
        'method': 'alipay.trade.page.pay',
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0',
        'biz_content': json.dumps(biz_content, ensure_ascii=False, 
                                  separators=(',', ':')),
    }
    
    # return_url 和 notify_url 作为顶层参数
    if return_url:
        params['return_url'] = str(return_url)
    if notify_url:
        params['notify_url'] = str(notify_url)
    
    # 生成签名
    params['sign'] = self._sign(params)
    
    # 构建支付URL（GET方式，需要URL编码）
    sorted_params = sorted(params.items())
    query_parts = []
    for k, v in sorted_params:
        if v is not None:
            encoded_key = quote(str(k), safe='')
            encoded_value = quote(str(v), safe='')
            query_parts.append(f'{encoded_key}={encoded_value}')
    query_string = '&'.join(query_parts)
    payment_url = f'{self.gateway_url}?{query_string}'
    
    return {'success': True, 'payment_url': payment_url}
```

### 2. 支付视图（`payment_views.py`）

#### 创建支付订单接口

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """创建支付订单"""
    order_id = request.data.get('order_id')
    order_type = request.data.get('order_type', 'normal')
    
    # 获取订单
    if order_type == 'verified':
        order = VerifiedOrder.objects.get(id=order_id)
    else:
        order = Order.objects.get(id=order_id)
    
    # 检查权限和状态
    if order.buyer != request.user:
        return Response({'error': '无权限'}, status=403)
    if order.status != 'pending':
        return Response({'error': '订单状态不正确'}, status=400)
    
    # 创建支付订单
    alipay = AlipayClient()
    result = alipay.create_trade(
        out_trade_no=f'{order_type}_{order.id}',
        subject=order.product.title[:256],
        total_amount=order.total_price,
        return_url=f'{settings.FRONTEND_URL}/order/{order.id}',
        notify_url=f'{settings.BACKEND_URL}/api/payment/alipay/notify/'
    )
    
    if result.get('success'):
        return Response({
            'success': True,
            'payment_url': result.get('payment_url'),
        })
    else:
        return Response({'error': '创建支付失败'}, status=400)
```

#### 异步通知接口

```python
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def alipay_payment_notify(request):
    """支付宝支付异步通知回调"""
    # 获取通知参数
    params = request.GET.dict() if request.method == 'GET' else request.POST.dict()
    
    # 验证签名
    alipay = AlipayClient()
    if not alipay.verify_notify(params):
        logger.error('支付宝签名验证失败')
        return HttpResponse('fail')
    
    # 解析订单信息
    out_trade_no = params.get('out_trade_no', '')
    trade_status = params.get('trade_status', '')
    
    # 处理支付成功
    if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
        # 解析订单类型和ID
        if '_' in out_trade_no:
            order_type, order_id = out_trade_no.split('_', 1)
        else:
            order_type, order_id = 'normal', out_trade_no
        
        # 更新订单状态
        if order_type == 'verified':
            order = VerifiedOrder.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id)
        
        if order.status == 'pending':
            order.status = 'paid'
            order.save()
            logger.info(f'订单 {out_trade_no} 支付成功')
    
    return HttpResponse('success')  # 必须返回 success
```

### 3. URL 配置

```python
# urls.py
urlpatterns = [
    path('api/payment/create/', payment_views.create_payment, name='create_payment'),
    path('api/payment/query/<int:order_id>/', payment_views.query_payment, name='query_payment'),
    path('api/payment/alipay/notify/', payment_views.alipay_payment_notify, name='alipay_payment_notify'),
]
```

---

## 配置说明

### settings.py 配置

```python
# ========== 支付宝支付配置 ==========
# 支付宝网关地址
ALIPAY_GATEWAY_URL = 'https://openapi.alipay.com/gateway.do'  # 生产环境
# ALIPAY_GATEWAY_URL = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'  # 沙箱环境

# 应用配置
ALIPAY_APP_ID = '您的APPID'  # 从支付宝开放平台获取
ALIPAY_APP_PRIVATE_KEY = '您的应用私钥'  # RSA2格式，2048位
ALIPAY_PUBLIC_KEY = '支付宝公钥'  # 从支付宝平台获取

# 前后端URL配置
FRONTEND_URL = 'https://yourdomain.com'  # 前端地址
BACKEND_URL = 'https://yourdomain.com'  # 后端地址
```

### 密钥格式

**应用私钥**（可以是完整格式或仅Base64字符串）：
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
（密钥内容）
...
-----END RSA PRIVATE KEY-----
```

**支付宝公钥**（从支付宝平台获取）：
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
（密钥内容）
...
-----END PUBLIC KEY-----
```

---

## 接口使用

### 1. 创建支付订单

**请求**：
```http
POST /api/payment/create/
Content-Type: application/json
Authorization: Bearer <token>

{
    "order_id": 90,
    "order_type": "normal"  // normal: 易淘订单, verified: 官方验订单
}
```

**响应**：
```json
{
    "success": true,
    "payment_url": "https://openapi.alipay.com/gateway.do?app_id=..."
}
```

**前端处理**：
```javascript
// 跳转到支付页面
window.location.href = response.data.payment_url;
```

### 2. 查询支付状态

**请求**：
```http
GET /api/payment/query/90/?order_type=normal
Authorization: Bearer <token>
```

**响应**：
```json
{
    "success": true,
    "trade_status": "TRADE_SUCCESS",
    "paid": true,
    "order_status": "paid"
}
```

### 3. 异步通知

支付宝会在支付成功后调用异步通知接口，无需前端处理。

---

## 常见问题

### 1. 签名验证失败（invalid-signature）

**可能原因**：
- `sign_type` 参数被错误排除（最常见）
- 应用公钥未正确上传到支付宝平台
- 支付宝公钥配置错误
- JSON 字符串格式问题

**解决方案**：
1. 确认 `sign_type` 参与签名
2. 检查应用公钥是否与私钥匹配
3. 确认支付宝公钥是从平台获取的
4. 使用 `ensure_ascii=False` 保持中文字符原样

### 2. 回调地址无法访问

**问题**：本地开发时，支付宝无法访问 `http://127.0.0.1:8000`

**解决方案**：
- 使用内网穿透工具（如 ngrok、natapp）
- 或先跳过异步通知，仅测试支付页面跳转

**详细说明**：参考 `INTRANET_PENETRATION_GUIDE.md` 了解各种内网穿透方案的配置方法

### 3. 支付页面无法打开

**可能原因**：
- 网关地址配置错误
- APPID 或密钥配置错误
- 签名计算错误

**解决方案**：
- 检查网关地址（生产/沙箱）
- 查看后端日志中的签名原文
- 使用测试工具验证配置

---

## 最佳实践

### 1. 安全性

- **私钥安全**：不要将私钥提交到代码仓库，使用环境变量或密钥管理服务
- **HTTPS**：生产环境必须使用 HTTPS
- **签名验证**：始终验证支付宝返回的签名

### 2. 错误处理

- **日志记录**：记录完整的签名原文和错误信息
- **异常处理**：妥善处理网络异常和签名验证失败
- **重试机制**：对于网络错误，实现合理的重试机制

### 3. 测试

- **沙箱环境**：先在沙箱环境测试
- **测试工具**：使用 `check_alipay_config.py` 和 `test_alipay_signature.py` 验证配置
- **完整流程**：测试完整的支付流程，包括异步通知

### 4. 代码规范

- **参数验证**：验证所有输入参数
- **错误信息**：提供清晰的错误信息
- **代码注释**：关键逻辑添加注释

### 5. 性能优化

- **连接池**：使用 HTTP 连接池
- **超时设置**：设置合理的超时时间
- **异步处理**：异步通知处理使用异步任务队列

---

## 调试工具

### 1. 配置检查工具

```bash
python check_alipay_config.py
```

功能：
- 检查基本配置
- 验证密钥格式
- 测试签名和验签
- 显示应用公钥（用于上传）

### 2. 签名格式测试工具

```bash
python test_alipay_signature.py
```

功能：
- 对比签名原文格式
- 验证参数是否正确
- 帮助定位签名问题

---

## 相关文档

- [支付宝开放平台](https://open.alipay.com/)
- [快速接入指南](https://opendocs.alipay.com/common/02kkv7)
- [签名验签文档](https://opendocs.alipay.com/common/02kipl)
- [电脑网站支付接口](https://opendocs.alipay.com/apis/api_1/alipay.trade.page.pay)

---

## 总结

支付宝支付接口开发的核心要点：

1. **签名算法**：严格按照官方文档实现，`sign_type` 必须参与签名
2. **密钥配置**：确保应用公钥正确上传，支付宝公钥正确配置
3. **参数格式**：JSON 字符串格式要正确，中文字符保持原样
4. **错误处理**：完善的错误处理和日志记录
5. **测试验证**：使用测试工具验证配置和签名格式

遵循以上要点，可以成功集成支付宝支付功能。

