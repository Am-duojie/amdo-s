# 支付宝异步通知地址配置指南

## 快速回答

**对于电脑网站支付（alipay.trade.page.pay）**：
- ✅ **无需在支付宝开放平台配置**
- ✅ 异步通知地址通过接口参数 `notify_url` 自动传入
- ✅ 代码中已自动配置：`notify_url = f'{settings.BACKEND_URL}/api/payment/alipay/notify/'`

## 详细配置说明

### 一、电脑网站支付的配置方式（本项目使用）

本项目使用的是 **电脑网站支付**（`alipay.trade.page.pay`），异步通知地址通过接口参数传入，**无需在开放平台额外配置**。

#### 1. 代码中的配置

**位置**：`backend/app/secondhand_app/payment_views.py`

```python
# 构建回调URL
notify_url = f'{getattr(settings, "BACKEND_URL", "http://127.0.0.1:8000")}/api/payment/alipay/notify/'

# 创建支付订单时传入
result = alipay.create_trade(
    out_trade_no=f'{order_type}_{order.id}',
    subject=product_title,
    total_amount=order.total_price,
    return_url=return_url,
    notify_url=notify_url  # 异步通知地址
)
```

#### 2. settings.py 配置

**位置**：`backend/core/settings.py`

```python
# 后端公网地址（用于构建 notify_url）
BACKEND_URL = 'https://yourdomain.com'  # 生产环境
# BACKEND_URL = 'https://your-ngrok-url.ngrok-free.app'  # 本地开发（使用ngrok）
```

#### 3. 本地开发配置（使用 ngrok）

**步骤1：启动 ngrok**

```bash
# 在终端中运行
ngrok http 8000
```

**步骤2：获取公网地址**

ngrok 会显示类似以下信息：
```
Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8000
```

**步骤3：配置 settings.py**

```python
# settings.py
BACKEND_URL = 'https://xxxx-xx-xx-xx-xx.ngrok-free.app'
```

**步骤4：验证地址可访问**

在浏览器中访问：
```
https://xxxx-xx-xx-xx-xx.ngrok-free.app/api/payment/alipay/notify/
```

应该能看到 Django 的响应（即使返回错误，也说明地址可访问）。

### 二、其他产品的配置方式（参考）

如果您使用的是其他支付宝产品（如转账到支付宝账号），可能需要在开放平台配置应用网关。

#### 配置步骤

1. **登录支付宝开放平台**
   - 访问：https://open.alipay.com/
   - 使用支付宝账号登录

2. **进入应用管理**
   - 点击右上角"控制台"
   - 左侧菜单选择"应用管理" -> "我的应用"
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
   - ✅ 地址必须是公网可访问的 HTTPS 地址
   - ✅ 本地开发需要使用内网穿透工具
   - ✅ 地址必须返回 HTTP 200 状态码
   - ✅ 地址不能包含查询参数（如 `?param=value`）

## 配置验证

### 1. 检查代码配置

确认 `settings.py` 中的 `BACKEND_URL` 已正确配置：

```python
# 生产环境
BACKEND_URL = 'https://yourdomain.com'

# 本地开发（使用ngrok）
BACKEND_URL = 'https://your-ngrok-url.ngrok-free.app'
```

### 2. 测试地址可访问性

**方法1：浏览器访问**
```
https://yourdomain.com/api/payment/alipay/notify/
```

**方法2：使用 curl**
```bash
curl -X POST https://yourdomain.com/api/payment/alipay/notify/
```

**预期结果**：
- 应该能看到 Django 的响应
- 即使返回错误（如缺少参数），也说明地址可访问

### 3. 查看支付日志

创建支付订单后，查看后端日志：

```python
# 日志中应该能看到类似信息
收到支付宝支付通知: method=POST, params={...}
支付宝订单号: normal_1, 状态: TRADE_SUCCESS
订单 normal_1 支付成功，状态已更新
```

## 常见问题

### Q1: 为什么不需要在开放平台配置？

**A**: 对于电脑网站支付（`alipay.trade.page.pay`），异步通知地址通过接口参数 `notify_url` 传入，支付宝会使用该地址发送通知，无需在开放平台额外配置。

### Q2: 本地开发如何接收异步通知？

**A**: 使用内网穿透工具（如 ngrok）将本地地址映射为公网地址，然后在 `settings.py` 中配置该公网地址。

### Q3: 异步通知地址有什么要求？

**A**: 
- ✅ 必须是公网可访问的地址
- ✅ 生产环境必须使用 HTTPS
- ✅ 地址必须返回 HTTP 200 状态码
- ✅ 地址不能包含查询参数

### Q4: 如何确认异步通知是否收到？

**A**: 
1. 查看后端日志，确认是否收到通知
2. 检查订单状态是否更新为 `paid`
3. 在支付宝开放平台的"交易管理"中查看交易记录

### Q5: 如果同时配置了接口参数和应用网关，哪个生效？

**A**: **接口参数中的 `notify_url` 优先级更高**。如果接口中传入了 `notify_url`，支付宝会使用接口参数中的地址，而不是应用网关中配置的地址。

## 总结

对于本项目使用的电脑网站支付：

1. ✅ **无需在开放平台配置**异步通知地址
2. ✅ 异步通知地址通过代码自动配置
3. ✅ 只需在 `settings.py` 中配置 `BACKEND_URL`
4. ✅ 本地开发使用 ngrok 进行内网穿透
5. ✅ 生产环境使用 HTTPS 公网地址

配置完成后，支付宝会在支付成功后自动调用您的异步通知接口。





