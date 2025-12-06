# 支付宝沙箱支付功能实现文档

## 概述

本实现严格按照支付宝官方文档规范开发，参考文档：
- [支付宝开放平台文档](https://opendocs.alipay.com/common/02kkv7)
- [签名验签文档](https://opendocs.alipay.com/common/02kipl)
- [电脑网站支付接口](https://opendocs.alipay.com/apis/api_1/alipay.trade.page.pay)

## 核心实现

### 1. 签名算法（RSA2）

严格按照支付宝官方规范实现：

1. **筛选参数**：获取所有请求参数，除去 `sign`、`sign_type` 两个参数外，其他参数都要参与签名
2. **排序**：按照参数名ASCII码从小到大排序（字典序）
3. **拼接**：将排序后的参数与其对应值，组合成 `参数=参数值` 的格式，用 `&` 字符连接
4. **签名**：使用RSA2算法（SHA256），对拼接后的字符串进行签名
5. **编码**：将签名结果进行Base64编码

**关键点**：
- 参数值使用原始值，不进行URL编码
- `sign_type` 不参与签名计算
- 空值（None、空字符串）不参与签名

### 2. 参数构建

#### 请求参数结构

```python
params = {
    'app_id': '应用ID',
    'method': 'alipay.trade.page.pay',  # 接口名称
    'charset': 'utf-8',  # 编码格式
    'sign_type': 'RSA2',  # 签名类型
    'timestamp': '2025-12-06 19:43:51',  # 时间戳
    'version': '1.0',  # 接口版本
    'biz_content': '{"out_trade_no":"...","product_code":"FAST_INSTANT_TRADE_PAY",...}',  # 业务参数（JSON字符串）
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
    "total_amount": "20.00",
    "subject": "订单标题"
}
```

**注意**：
- `biz_content` 必须是JSON字符串格式
- `return_url` 和 `notify_url` 作为顶级参数，不在 `biz_content` 中
- 金额格式：保留两位小数，字符串格式

### 3. URL构建

1. **签名**：使用原始参数值进行签名
2. **编码**：构建URL时，对参数名和参数值进行URL编码
3. **排序**：URL参数按参数名排序（与签名时一致）

**关键点**：
- 签名时使用原始值（未编码）
- URL编码时，空格编码为 `%20`（不是 `+`）
- 使用 `urllib.parse.quote` 进行编码

### 4. 密钥配置

#### 应用私钥（ALIPAY_SANDBOX_APP_PRIVATE_KEY）

- 用于签名发送给支付宝的请求
- 格式：RSA2，2048位
- 可以是完整格式（包含头尾标记）或仅Base64字符串

#### 应用公钥

- 从应用私钥生成的公钥
- 需要上传到支付宝开放平台
- 上传步骤：
  1. 登录 https://openhome.alipay.com/develop/sandbox/app
  2. 选择应用 -> 接口加签方式 -> 设置
  3. 粘贴应用公钥（包含头尾标记）
  4. 保存

#### 支付宝公钥（ALIPAY_SANDBOX_PUBLIC_KEY）

- 上传应用公钥后，支付宝返回的公钥
- 用于验证支付宝返回的数据签名
- 必须从支付宝控制台获取，不能自己生成

## 使用示例

### 创建支付订单

```python
from app.secondhand_app.alipay_sandbox import AlipaySandboxClient

alipay = AlipaySandboxClient()

# 验证配置
is_valid, error_msg = alipay.validate_config()
if not is_valid:
    print(f'配置错误: {error_msg}')
    return

# 创建支付订单
result = alipay.create_trade(
    out_trade_no='order_123',
    subject='测试商品',
    total_amount=20.00,
    return_url='http://localhost:5173/order/123',
    notify_url='http://127.0.0.1:8000/api/payment/alipay/notify/'
)

if result.get('success'):
    payment_url = result.get('payment_url')
    # 前端跳转到 payment_url
else:
    error_msg = result.get('msg', '创建支付失败')
    print(f'创建支付失败: {error_msg}')
```

### 验证支付通知

```python
# 在支付通知回调中
params = request.GET.dict()  # 或 request.POST.dict()

alipay = AlipaySandboxClient()
if alipay.verify_notify(params):
    # 签名验证成功，处理支付结果
    trade_status = params.get('trade_status')
    if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
        # 支付成功，更新订单状态
        pass
else:
    # 签名验证失败
    return HttpResponse('fail')
```

## 常见问题

### 1. 签名验证失败（invalid-signature）

**可能原因**：
- 应用公钥未正确上传到支付宝平台
- 上传的应用公钥与代码中的私钥不匹配
- 支付宝公钥配置错误

**解决方案**：
1. 使用 `generate_app_public_key.py` 生成应用公钥
2. 将应用公钥上传到支付宝平台
3. 更新配置文件中的支付宝公钥
4. 等待2-5分钟让配置生效

### 2. 参数格式错误

**检查点**：
- `biz_content` 必须是JSON字符串格式
- 金额格式：保留两位小数，字符串格式
- 时间戳格式：`YYYY-MM-DD HH:MM:SS`

### 3. URL编码问题

**注意**：
- 签名时使用原始值（未编码）
- URL编码时，空格编码为 `%20`
- 参数值中的特殊字符需要正确编码

## 测试工具

### 生成应用公钥

```bash
python generate_app_public_key.py
```

### 验证密钥配置

```bash
python verify_keys_from_screenshot.py
```

## 参考文档

- [支付宝开放平台](https://openhome.alipay.com/)
- [沙箱应用管理](https://openhome.alipay.com/develop/sandbox/app)
- [接口文档](https://opendocs.alipay.com/apis/api_1/alipay.trade.page.pay)
- [签名验签文档](https://opendocs.alipay.com/common/02kipl)

