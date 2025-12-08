# 支付接口回调实现文档

## 概述

本项目实现了支付宝支付的异步通知回调（notify_url）和同步返回（return_url）机制，确保支付状态能够及时更新到系统中。

## 回调机制说明

### 1. 异步通知（notify_url）

**作用**：支付宝服务器在支付成功后，会主动向商户服务器发送支付结果通知。

**特点**：
- 由支付宝服务器主动发起
- 不依赖用户操作
- 更可靠，即使页面关闭也能收到通知
- 必须返回 `success` 或 `fail` 给支付宝

**实现位置**：
- URL路由：`/api/payment/alipay/notify/`
- 视图函数：`backend/app/secondhand_app/payment_views.py::alipay_payment_notify`

### 2. 同步返回（return_url）

**作用**：用户支付完成后，支付宝会跳转回商户指定的页面。

**特点**：
- 依赖用户浏览器跳转
- 可能因为网络问题导致跳转失败
- 仅用于展示支付结果，不作为支付成功的依据
- 实际支付状态以异步通知为准

**实现位置**：
- 前端页面：`/order/{order_id}` 或 `/verified-order/{order_id}`
- 前端会轮询查询支付状态

## 完整实现流程

### 步骤1：创建支付订单

**位置**：`backend/app/secondhand_app/payment_views.py::create_payment`

```python
# 构建回调URL
notify_url = f'{settings.BACKEND_URL}/api/payment/alipay/notify/'
return_url = f'{settings.FRONTEND_URL}/order/{order.id}'

# 创建支付订单
result = alipay.create_trade(
    out_trade_no=f'{order_type}_{order.id}',
    subject=product_title,
    total_amount=order.total_price,
    return_url=return_url,  # 同步返回地址
    notify_url=notify_url   # 异步通知地址
)
```

**关键点**：
- `out_trade_no` 格式：`{order_type}_{order_id}`，用于区分订单类型
- `notify_url` 必须是公网可访问的地址（本地开发需要使用内网穿透）
- `return_url` 是前端页面地址，用于用户支付后跳转

### 步骤2：用户完成支付

用户跳转到支付宝支付页面，完成支付操作。

### 步骤3：异步通知处理

**位置**：`backend/app/secondhand_app/payment_views.py::alipay_payment_notify`

```python
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def alipay_payment_notify(request):
    """
    支付宝支付异步通知回调
    支付宝会在支付成功后调用此接口
    """
    # 1. 获取通知参数
    params = request.GET.dict() if request.method == 'GET' else request.POST.dict()
    
    # 2. 验证签名（防止伪造通知）
    alipay = AlipayClient()
    if not alipay.verify_notify(params):
        logger.error('支付宝签名验证失败')
        return HttpResponse('fail')  # 返回fail，支付宝会重试
    
    # 3. 解析订单信息
    out_trade_no = params.get('out_trade_no', '')  # 商户订单号
    trade_status = params.get('trade_status', '')   # 交易状态
    trade_no = params.get('trade_no', '')          # 支付宝交易号
    
    # 4. 解析订单类型和ID
    if '_' in out_trade_no:
        parts = out_trade_no.split('_', 1)
        order_type = parts[0]  # 'normal' 或 'verified'
        order_id = parts[1]    # 订单ID
    else:
        order_type = 'normal'
        order_id = out_trade_no
    
    # 5. 处理支付成功
    if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
        try:
            # 获取订单
            if order_type == 'verified':
                order = VerifiedOrder.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id)
            
            # 防止重复处理（幂等性）
            if order.status == 'pending':
                # 更新订单状态
                order.status = 'paid'
                # 记录支付宝交易号
                if hasattr(order, 'alipay_trade_no'):
                    order.alipay_trade_no = trade_no
                order.save()
                
                logger.info(f'订单 {out_trade_no} 支付成功，状态已更新')
            else:
                logger.info(f'订单 {out_trade_no} 已处理过，当前状态：{order.status}')
        except Exception as e:
            logger.error(f'处理订单异常: {str(e)}')
            return HttpResponse('fail')
    
    # 6. 必须返回 success（告诉支付宝已收到通知）
    return HttpResponse('success')
```

**关键点**：
1. **CSRF豁免**：使用 `@csrf_exempt`，因为支付宝服务器无法提供CSRF token
2. **允许匿名访问**：使用 `@permission_classes([AllowAny])`，因为支付宝服务器没有认证信息
3. **签名验证**：必须验证签名，防止伪造通知
4. **幂等性处理**：检查订单状态，防止重复处理
5. **返回结果**：必须返回 `success` 或 `fail`，支付宝根据返回值决定是否重试

### 步骤4：签名验证

**位置**：`backend/app/secondhand_app/alipay_client.py::verify_notify`

```python
def verify_notify(self, params):
    """验证支付通知签名"""
    sign = params.get('sign', '')
    if not sign:
        return False
    
    # 移除sign和sign_type参数
    verify_params = {k: v for k, v in params.items() if k not in ['sign', 'sign_type']}
    
    return self._verify_sign(verify_params, sign)
```

**签名验证流程**：
1. 从参数中提取 `sign`（签名值）
2. 移除 `sign` 和 `sign_type` 参数
3. 过滤空值
4. 按参数名ASCII码排序
5. 拼接成签名字符串：`key1=value1&key2=value2`
6. 使用支付宝公钥验证签名

**详细实现**：`backend/app/secondhand_app/alipay_client.py::_verify_sign`

```python
def _verify_sign(self, data, sign):
    """验证签名"""
    try:
        # 1. 格式化公钥
        public_key_str = self._format_public_key(self.alipay_public_key)
        
        # 2. 加载公钥
        public_key = RSA.import_key(public_key_str)
        
        # 3. 过滤并排序参数
        filtered_data = {}
        for k, v in data.items():
            if k in ['sign', 'sign_type']:
                continue
            if v is None or v == '':
                continue
            filtered_data[k] = v
        
        sorted_data = sorted(filtered_data.items())
        
        # 4. 拼接签名字符串
        sign_str = '&'.join([f'{k}={v}' for k, v in sorted_data])
        
        # 5. 验证签名
        sign_bytes = base64.b64decode(sign)
        hash_obj = SHA256.new(sign_str.encode('utf-8'))
        verifier = pkcs1_15.new(public_key)
        verifier.verify(hash_obj, sign_bytes)
        
        return True
    except Exception as e:
        logger.error(f'签名验证失败: {str(e)}')
        return False
```

### 步骤5：同步返回处理

**位置**：前端页面 `frontend/src/pages/OrderDetail.vue`

用户支付完成后，支付宝会跳转到 `return_url`，前端页面会：

1. 显示支付结果
2. 轮询查询支付状态（因为异步通知可能延迟）
3. 更新订单状态显示

```javascript
// 轮询查询支付状态
const checkPaymentStatus = async () => {
  try {
    const res = await api.get(`/payment/query/${orderId}/?order_type=normal`)
    if (res.data?.paid) {
      // 支付成功，更新订单状态
      await loadOrder()
    }
  } catch (error) {
    console.error('查询支付状态失败:', error)
  }
}
```

## 配置说明

### 1. 后端配置

**位置**：`backend/core/settings.py`

```python
# 支付宝配置
ALIPAY_APP_ID = '9021000158624650'
ALIPAY_APP_PRIVATE_KEY = '...'  # 应用私钥
ALIPAY_PUBLIC_KEY = '...'       # 支付宝公钥
ALIPAY_GATEWAY_URL = 'https://openapi.alipay.com/gateway.do'  # 生产环境
# ALIPAY_GATEWAY_URL = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'  # 沙箱环境

# 回调URL配置
BACKEND_URL = 'https://yourdomain.com'  # 后端公网地址（用于notify_url）
FRONTEND_URL = 'https://yourdomain.com'  # 前端公网地址（用于return_url）
```

### 2. URL路由配置

**位置**：`backend/core/urls.py`

```python
urlpatterns = [
    # 支付相关路由
    path('api/payment/create/', payment_views.create_payment, name='create_payment'),
    path('api/payment/alipay/notify/', payment_views.alipay_payment_notify, name='alipay_payment_notify'),
    path('api/payment/query/<int:order_id>/', payment_views.query_payment, name='query_payment'),
]
```

## 安全措施

### 1. 签名验证
- 所有异步通知都必须验证签名
- 使用支付宝公钥验证，确保通知来自支付宝服务器

### 2. 幂等性处理
- 检查订单状态，防止重复处理
- 只有 `pending` 状态的订单才会更新为 `paid`

### 3. 异常处理
- 捕获所有异常，记录日志
- 返回 `fail` 让支付宝重试

### 4. CSRF豁免
- 异步通知接口使用 `@csrf_exempt`
- 因为支付宝服务器无法提供CSRF token

## 支付宝开放平台配置异步通知地址

### 配置位置和方法

根据您使用的支付宝产品类型，有两种配置方式：

#### 方式1：通过接口参数配置（推荐，适用于电脑网站支付）

**适用产品**：`alipay.trade.page.pay`（电脑网站支付）

**配置方法**：
- **无需在开放平台配置**，直接在调用支付接口时传入 `notify_url` 参数
- 代码中已自动配置：`notify_url = f'{settings.BACKEND_URL}/api/payment/alipay/notify/'`

**优点**：
- 配置灵活，可以为不同订单设置不同的通知地址
- 无需在开放平台额外配置

#### 方式2：通过应用网关配置（适用于资金营销类产品）

**适用产品**：转账到支付宝账号、商家券等资金营销类产品

**配置步骤**：

1. **登录支付宝开放平台**
   - 访问：https://open.alipay.com/
   - 使用支付宝账号登录

2. **进入应用管理**
   - 登录后，点击右上角"控制台"
   - 在左侧菜单选择"应用管理" -> "我的应用"
   - 找到您的应用，点击进入应用详情

3. **配置应用网关**
   - 在应用详情页面，找到"应用网关"或"消息通知"配置项
   - 点击"设置"或"修改"
   - 填写异步通知接收地址：
     ```
     https://yourdomain.com/api/payment/alipay/notify/
     ```
   - 点击"保存"

4. **配置要求**
   - 地址必须是公网可访问的 HTTPS 地址
   - 本地开发需要使用内网穿透工具（如 ngrok）
   - 地址必须返回 HTTP 200 状态码

**注意事项**：
- 如果同时使用接口参数和应用网关，**接口参数中的 `notify_url` 优先级更高**
- 对于电脑网站支付，推荐使用方式1（接口参数配置）

### 本地开发配置

本地开发时，需要使用内网穿透工具（如 ngrok）将本地地址映射为公网地址。

**配置示例**：

```python
# settings.py
BACKEND_URL = 'https://your-ngrok-url.ngrok-free.app'
FRONTEND_URL = 'http://localhost:5173'
```

**ngrok配置**：

```bash
# 启动ngrok，将本地8000端口映射到公网
ngrok http 8000
```

**获取公网地址**：
- ngrok 启动后会显示公网地址，例如：`https://xxxx-xx-xx-xx-xx.ngrok-free.app`
- 在 `settings.py` 中配置：`BACKEND_URL = 'https://xxxx-xx-xx-xx-xx.ngrok-free.app'`
- 代码会自动使用该地址构建 `notify_url`

**验证配置**：
- 访问：`https://your-ngrok-url.ngrok-free.app/api/payment/alipay/notify/`
- 应该能看到 Django 的响应（即使返回错误，也说明地址可访问）

## 测试流程

### 1. 测试异步通知

```bash
# 1. 创建支付订单
curl -X POST http://localhost:8000/api/payment/create/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "order_type": "normal"}'

# 2. 完成支付（在支付宝页面）

# 3. 查看后端日志，确认收到异步通知
# 4. 检查订单状态是否更新为 'paid'
```

### 2. 测试签名验证

```python
# 在 alipay_client.py 中添加测试代码
def test_verify_notify():
    alipay = AlipayClient()
    # 模拟支付宝通知参数
    params = {
        'out_trade_no': 'normal_1',
        'trade_status': 'TRADE_SUCCESS',
        'trade_no': '2023120622001234567890123456',
        'sign': '...',  # 支付宝返回的签名
        # ... 其他参数
    }
    result = alipay.verify_notify(params)
    print(f'签名验证结果: {result}')
```

## 常见问题

### 1. 异步通知未收到

**可能原因**：
- `notify_url` 配置错误
- 服务器无法访问（防火墙、内网等）
- 签名验证失败，返回了 `fail`

**解决方法**：
- 检查 `notify_url` 是否正确配置
- 使用内网穿透工具（本地开发）
- 检查服务器日志，查看签名验证结果

### 2. 签名验证失败

**可能原因**：
- 支付宝公钥配置错误
- 参数处理不正确（空值、排序等）
- 字符编码问题

**解决方法**：
- 检查支付宝公钥是否正确配置
- 查看日志中的签名字符串，与支付宝文档对比
- 确保参数处理符合支付宝规范

### 3. 订单状态未更新

**可能原因**：
- 异步通知处理异常
- 订单状态检查逻辑问题
- 数据库事务问题

**解决方法**：
- 查看后端日志，确认是否收到通知
- 检查订单状态更新逻辑
- 使用查询接口手动同步状态

## 总结

支付接口回调实现包括：

1. **异步通知（notify_url）**：支付宝服务器主动通知，更可靠
2. **签名验证**：确保通知来自支付宝，防止伪造
3. **幂等性处理**：防止重复处理，保证数据一致性
4. **异常处理**：完善的错误处理和日志记录
5. **同步返回（return_url）**：用户支付后跳转，配合轮询查询

整个流程确保了支付状态的及时更新和系统的安全性。

