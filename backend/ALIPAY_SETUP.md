# 支付宝支付配置指南

本文档说明如何配置支付宝支付接口。

**参考文档**：
- [支付宝开放平台文档](https://opendocs.alipay.com/common/02kkv7)
- [应用管理](https://openhome.alipay.com/develop/sandbox/app)

## 一、获取支付宝配置信息

### 1. 登录支付宝开放平台

1. **访问支付宝开放平台**
   - 网址：https://open.alipay.com/
   - 使用支付宝账号登录（如果没有账号，需要先注册）

2. **进入开发者中心**
   - 登录后，点击右上角"控制台"进入开发者中心

### 2. 创建应用

1. **创建网页应用**
   - 在控制台选择"网页&移动应用"
   - 点击"创建应用"
   - 填写应用信息：
     - 应用名称：您的应用名称
     - 应用类型：网页应用
     - 行业分类：选择您的行业

2. **获取应用信息**
   - 创建成功后，在应用详情页获取 **APPID**
   - 这是应用的唯一标识

### 3. 配置密钥

1. **生成密钥对**
   - 使用支付宝密钥生成工具或 OpenSSL 生成密钥对
   - 推荐使用支付宝提供的密钥生成工具：
     - 下载地址：https://opendocs.alipay.com/common/02kkv7
   - 或使用 OpenSSL 生成：
     ```bash
     # 生成私钥（2048位）
     openssl genrsa -out app_private_key.pem 2048
     
     # 生成公钥
     openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem
     ```

2. **上传应用公钥**
   - 在应用详情页，点击"接口加签方式" -> "设置"
   - 选择"公钥"模式
   - 复制生成的公钥内容（包含 `-----BEGIN PUBLIC KEY-----` 和 `-----END PUBLIC KEY-----`）
   - 粘贴到"应用公钥"输入框
   - 点击"保存"

3. **获取支付宝公钥**
   - 保存后，页面会显示"支付宝公钥"
   - 复制这个公钥，用于配置 `ALIPAY_PUBLIC_KEY`

### 4. 配置回调地址

1. **配置异步通知地址**
   - 在应用详情页，找到"接口信息"
   - 配置"异步通知地址"（notify_url）
   - 格式：`https://yourdomain.com/api/payment/alipay/notify/`
   - 注意：生产环境必须使用 HTTPS

2. **配置同步跳转地址**
   - 在创建支付订单时，通过代码动态设置 `return_url`
   - 格式：`https://yourdomain.com/order/{order_id}`

## 二、配置 settings.py

在 `backend/core/settings.py` 文件中配置以下参数：

### 1. 基本配置

```python
# ========== 支付宝支付配置 ==========
# 文档：https://opendocs.alipay.com/common/02kkv7

# 支付宝网关地址
# 生产环境：https://openapi.alipay.com/gateway.do
# 沙箱环境（测试用）：https://openapi-sandbox.dl.alipaydev.com/gateway.do
ALIPAY_GATEWAY_URL = 'https://openapi.alipay.com/gateway.do'
```

### 2. 应用配置（必填）

从支付宝开放平台控制台获取以下信息：

```python
# 应用配置（从支付宝开放平台控制台获取）
ALIPAY_APP_ID = '您的APPID'  # APPID（必填，从控制台获取）

# 应用私钥（必填，RSA2格式，2048位）
# 注意：这是您自己生成的私钥，请妥善保管，不要泄露
ALIPAY_APP_PRIVATE_KEY = '''您的应用私钥（可以是完整格式或仅Base64字符串）'''

# 支付宝公钥（必填，从控制台获取）
# 注意：这是支付宝提供的公钥，用于验证支付宝返回的数据签名
ALIPAY_PUBLIC_KEY = '''支付宝返回的公钥（从控制台获取）'''
```

### 3. 前后端URL配置

```python
# 前后端URL配置（用于动态构建回调地址）
FRONTEND_URL = 'https://yourdomain.com'  # 前端地址（生产环境）
BACKEND_URL = 'https://yourdomain.com'  # 后端地址（生产环境）
```

**注意**：
- 本地开发可以使用 `http://localhost:5173` 和 `http://127.0.0.1:8000`
- 生产环境必须使用 HTTPS 和公网可访问的地址

## 三、密钥格式说明

### 应用私钥格式

应用私钥可以是以下两种格式之一：

1. **完整格式**（推荐）：
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
（密钥内容）
...
-----END RSA PRIVATE KEY-----
```

2. **仅Base64字符串**：
```
MIIEpAIBAAKCAQEA...（密钥内容，不含头尾标记）
```

### 支付宝公钥格式

支付宝公钥可以是以下两种格式之一：

1. **完整格式**（推荐）：
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
（密钥内容）
...
-----END PUBLIC KEY-----
```

2. **仅Base64字符串**：
```
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...（密钥内容，不含头尾标记）
```

## 四、安装依赖

确保已安装 `pycryptodome` 库：

```bash
pip install pycryptodome==3.20.0
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

## 五、验证配置

配置完成后，可以通过以下方式验证：

1. **查看后端日志**
   - 启动服务器后，查看日志中是否有配置错误提示
   - 尝试创建支付订单，查看是否有配置相关的错误

2. **测试支付流程**
   - 在前端创建订单
   - 选择支付宝支付
   - 检查是否能正常跳转到支付宝支付页面

## 六、使用说明

### 1. 创建支付订单（易淘订单）

**接口**：`POST /api/payment/create/`

**请求参数**：
```json
{
  "order_id": 1,
  "order_type": "normal"  // normal: 易淘订单, verified: 官方验订单
}
```

**响应**：
```json
{
  "success": true,
  "payment_url": "https://openapi.alipay.com/gateway.do?...",
  "payment_provider": "alipay"
}
```

### 2. 创建支付订单（官方验订单）

**接口**：`POST /api/payment/create/`

**请求参数**：
```json
{
  "order_id": 1,
  "order_type": "verified"
}
```

### 3. 查询支付状态

**接口**：`GET /api/payment/query/<order_id>/?order_type=normal`

**查询参数**：
- `order_type`: `normal` 或 `verified`

## 七、测试流程

1. **使用测试账号登录支付宝**
   - 在支付宝开放平台获取测试账号信息
   - 使用该账号登录支付宝进行测试

2. **创建订单并支付**
   - 在前端创建订单
   - 选择支付宝支付
   - 跳转到支付宝支付页面
   - 使用测试账号完成支付

3. **验证支付结果**
   - 支付成功后会自动跳转回前端页面
   - 订单状态会自动更新为 `paid`
   - 可以通过查询接口验证支付状态

## 八、注意事项

1. **私钥安全**
   - 应用私钥必须妥善保管，不要泄露
   - 不要将私钥提交到代码仓库
   - 建议使用环境变量或密钥管理服务

2. **公钥格式**
   - 支付宝公钥必须从支付宝控制台获取
   - 不能自己生成，必须使用支付宝返回的公钥

3. **回调地址**
   - 本地开发：可以使用 `http://127.0.0.1:8000` 或 `http://localhost:8000`
   - 生产环境：必须使用公网可访问的HTTPS地址
   - 需要在支付宝开放平台配置回调地址白名单

4. **订单号格式**
   - 易淘订单：`normal_<order_id>`
   - 官方验订单：`verified_<order_id>`

5. **签名算法**
   - 使用 RSA2 算法（SHA256）
   - 严格按照支付宝官方文档规范实现

## 九、常见问题

### 1. 签名验证失败

**可能原因**：
- 应用公钥未正确上传到支付宝平台
- 上传的应用公钥与代码中的私钥不匹配
- 支付宝公钥配置错误

**解决方案**：
1. 检查私钥和公钥是否匹配
2. 确认使用的是RSA2格式的密钥
3. 检查密钥内容是否完整
4. 确认支付宝公钥是从控制台获取的

### 2. 回调地址无法访问

**可能原因**：
- 本地开发环境无法接收公网回调
- 回调地址未配置白名单

**解决方案**：
1. 本地开发需要使用内网穿透工具（如ngrok）
2. 生产环境需要在支付宝控制台配置回调地址白名单

### 3. 支付页面无法打开

**可能原因**：
- 网关地址配置错误
- APPID和密钥配置错误

**解决方案**：
1. 检查网关地址是否正确
2. 确认APPID和密钥配置正确
3. 查看后端日志获取详细错误信息

## 十、相关文档

- 支付宝开放平台：https://open.alipay.com/
- 快速接入指南：https://opendocs.alipay.com/common/02kkv7
- 电脑网站支付文档：https://opendocs.alipay.com/open/270/105898
- 签名验签文档：https://opendocs.alipay.com/common/02kipl










