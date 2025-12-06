# 支付宝沙箱支付配置指南

本文档说明如何配置支付宝沙箱支付接口。

**参考文档**：
- [支付宝开放平台文档](https://opendocs.alipay.com/common/02kkv7)
- [沙箱应用管理](https://openhome.alipay.com/develop/sandbox/app)
- [沙箱账号管理](https://openhome.alipay.com/develop/sandbox/account)

## 一、获取支付宝沙箱配置信息

### 1. 登录支付宝开放平台

1. **访问支付宝开放平台**
   - 网址：https://open.alipay.com/
   - 使用支付宝账号登录（如果没有账号，需要先注册）

2. **进入开发者中心**
   - 登录后，点击右上角"控制台"进入开发者中心

### 2. 进入沙箱环境

1. **访问沙箱控制台**
   - 直接访问：https://openhome.alipay.com/develop/sandbox/app
   - 或在开发者中心选择"沙箱环境"

2. **创建或选择沙箱应用**
   - 如果是第一次使用，系统会自动创建一个沙箱应用
   - 如果已有应用，选择要使用的应用

### 3. 获取应用配置信息

在沙箱应用详情页面，获取以下信息：

#### 3.1 应用基本信息
- **APPID**：应用唯一标识（如：9021000158624650）
  - 位置：应用详情页顶部
  - 格式：数字字符串

#### 3.2 密钥配置

1. **生成密钥对**（如果还没有）
   - 点击"接口加签方式" -> "设置"
   - 选择"公钥"模式（沙箱环境仅支持公钥模式）
   - 使用支付宝提供的密钥生成工具生成密钥对
   - 或使用 OpenSSL 生成：
     ```bash
     # 生成私钥（2048位）
     openssl genrsa -out app_private_key.pem 2048
     
     # 生成公钥
     openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem
     ```

2. **上传应用公钥**
   - 复制生成的公钥内容（包含 `-----BEGIN PUBLIC KEY-----` 和 `-----END PUBLIC KEY-----`）
   - 在支付宝控制台"接口加签方式"中上传
   - 保存后，支付宝会返回"支付宝公钥"

3. **获取密钥信息**
   - **应用私钥**：从本地生成的 `app_private_key.pem` 文件中获取
   - **应用公钥**：已上传到支付宝的公钥（用于验证）
   - **支付宝公钥**：从支付宝控制台获取的公钥（用于验证支付宝返回的数据）

#### 3.3 网关地址
- **沙箱网关**：`https://openapi-sandbox.dl.alipaydev.com/gateway.do`
- **生产网关**：`https://openapi.alipay.com/gateway.do`（生产环境使用）

### 4. 获取沙箱账号信息

1. **访问沙箱账号页面**
   - 网址：https://openhome.alipay.com/develop/sandbox/account

2. **查看测试账号**
   - **买家账号**：用于测试支付功能
     - 账号：通常是手机号或邮箱
     - 登录密码：在沙箱账号页面查看
   - **卖家账号**：用于测试收款功能

3. **账号登录**
   - 使用买家账号登录支付宝沙箱环境
   - 网址：https://sandbox.alipaydev.com/
   - 用于测试支付流程

## 二、配置 settings.py

在 `backend/core/settings.py` 文件中配置以下参数：

### 2.1 基本配置

```python
# ========== 支付宝沙箱支付配置 ==========
# 文档：https://opendocs.alipay.com/common/02kkv7
# 沙箱控制台：https://openhome.alipay.com/develop/sandbox/app

# 支付宝沙箱网关地址
ALIPAY_SANDBOX_GATEWAY_URL = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
```

### 2.2 应用配置（必填）

从支付宝沙箱控制台获取以下信息：

```python
# 应用配置（从支付宝开放平台沙箱控制台获取）
ALIPAY_SANDBOX_APP_ID = '9021000158624650'  # APPID（必填，从控制台获取）

# 应用私钥（必填，RSA2格式，2048位）
# 注意：这是您自己生成的私钥，不要泄露
# 格式：可以是完整格式（包含头尾标记）或仅Base64字符串
ALIPAY_SANDBOX_APP_PRIVATE_KEY = '''MIIEpAIBAAKCAQEAiUu8rsRcQ0R8oKPVjZjsIWkWChaKIyzSpgp5SUaOd59hfnjbWMLaYBdKhJSURlN34xQayH8jYnr7zy6vjxkk/Yxjop5KUNMSJsRByM0Rdh9eUbQLz1Qaic/dPf5MRRb1BjzQpaXyGne+0KxyOjPBTl7eEr1819MIO7tuqgBfskJ86wcSVHC1qxIrqnt3LJdjgv4+qe5DsxkVQkel/DzUFllknwLsANY5Lt4XIKhVQNmmsTFMmSmT1ru5qJTM0b+0UJRxROAf6wWt2xgZut1kQMllIgF4nDqU4o47M21WegD2jhg4vk53mWqgtcVQgakbXmxJBmfbTrdmErPrAbkIpwIDAQABAoIBABBCyhwg4ZSN/fzAqsBUhlMGsTeMp9u2qVRFFUxacPE2DUP/aGtA2MBcwdSmDFGv/RkF/o4UkMpPKpfFPcHDBqCJChvuh3q/JP02bVws/Y5x9KfUnTl3CpWb6uY2wi3EpEyS01trJhuAZzcr1XOTQafYkJDDpI+jTOxWLKsx1CO2kn/hAQKdWYn+9Fp5nh8RgM6GUqMa6+lpzEZ9ji0rVrcRFp6XK6GKie/Xjl+Df8n72NQw/r9KmbZHo/9cYIPiRuexOWsfRNmT+X3y4dzBE3BeRoOH1SIUgD0EP1TfR+S6bLpGLqCLRMFDsg5Qjyb2q/Mfm5yYs3A6TEvRswGiRRECgYEA7vcUprUzt0Epx+HdiK/lIljaBfZ7PKfSoWosyl2QWg4lOO6hKa+1vRwlOukzYV4rmqLmLacrcAkXi5Aeg2gVJJRHBs+2Q721eGafMw3Ipdi44qXZPbnA0EczvSVAtk30PlJFlFZiFCQplykd/dkVoTpo8POZFkpcHvIPWjL5WQsCgYEAkxVGOrDFuo9brjVCBr0WhYAvZZMCqPh8ScAqiPHvKyCurFODhkSFwQ6mL47LlZOJeiVR8zPpIXcvnYn4kQoPhhsm7FOAAgLwMsDHRUc0RHXcLCWJgKz+AxbRrMkoUBfrsMHDLWLIId+z1ZIbsrco2g6GH4l2tWtVIEWU+KeGaFUCgYEAlk14gsa0SY5F/j/1fFTONUVXlKqMpwETvY0vsPUap1oAVYfafILVN6YtUJl/RL3bhT7yskJUUvqVAaZbWuGrcr+E0SbyiDcZnipF9fG0g4QF/iC8vFNKkHZId66nvkLX3h8XPo76z5pTQo2NHK5fKXK4sN03K8sHmDs+JsirBzMCgYAgjjLvRrVdZ+HZG3yz1SKpBgh3qSSLlgScpmZDzZksqJ1BE3MnQv+ADegG2sqBHxjs6lnLRRAzEhh9/E4CfIGXI2doI8tPpqrX8Qeqc+pDxPqo4t4elyvaLzDV1+iOYd0PULQM1bKKnONHQIHU+umV6mURkfGukkVTUVN5/kqnyQKBgQDUXp2CbmY/UmojJEGOmahwsAF702T0LQNl2M0DEnJEid+pv9OOaoeJ/+vPVfospeH2D4DDgNdBLcLBgTcsInW16lmG6pFPCVJ4P1H7LwpdMNptuUEOYHqiyqYcDvJT2CBqMtVawcZlig/PtMg9RR0JvMLXfmjxsK4GAza1jgWaSA=='''

# 支付宝公钥（必填，从沙箱控制台获取）
# 注意：这是支付宝提供的公钥，用于验证支付宝返回的数据
ALIPAY_SANDBOX_PUBLIC_KEY = '''MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjvYXLvwQOhTEtpuDEGJB5+TFhqgAObVy9LD4qfi60xS78kl8EkWg3AMq4n5mwwIvkExF3sByHKJQ5M12RsnUFCxaQUwdiGpPeFk9nkB6BZoDyegj68Na5HnC50kvwO5C9f+dKEBsTGaUsrXjBWlGqj6g+XnCeUffY9Xi9XHIwn/lXC0uekoXYR1qU5/QKLGuwXiPuBQVvyRVZBEUO7rZWPbhvbG48WWmgytdMeTIYdvPnjI7u5oEITTwCwCL2h8swQu3W7sxBEz9vA/G3IpYbZbuutVTjrnP/vWuY9nc0wwutPGEn6xWiZ2raj/pJ5kgOPSSkqIIBDE2Q0yssbMzTwIDAQAB'''
```

### 2.3 回调地址配置

```python
# 回调地址配置
# 注意：生产环境必须使用HTTPS和公网可访问的地址
ALIPAY_SANDBOX_NOTIFY_URL = 'http://127.0.0.1:8000/api/payment/alipay/notify/'  # 异步通知地址（本地测试用）
ALIPAY_SANDBOX_RETURN_URL = 'http://localhost:5173/order/'  # 支付完成跳转地址（本地测试用）

# 前后端URL配置（用于动态构建回调地址）
FRONTEND_URL = 'http://localhost:5173'  # 前端地址
BACKEND_URL = 'http://127.0.0.1:8000'  # 后端地址
```

### 2.4 演示模式（可选）

```python
# 演示模式（仅用于测试界面，不进行真实支付）
# 注意：支付宝沙箱环境本身就是测试环境，此选项主要用于本地调试
ALIPAY_SANDBOX_DEMO_MODE = False  # True=演示模式, False=真实支付
```

### 2.5 配置验证

配置完成后，可以通过以下方式验证：

1. **运行配置检查脚本**（如果已创建）：
   ```bash
   python test_alipay_sign.py
   ```

2. **查看后端日志**：
   - 启动服务器后，查看日志中是否有配置错误提示
   - 尝试创建支付订单，查看是否有配置相关的错误

## 三、密钥生成（如果还没有密钥对）

### 3.1 使用支付宝密钥生成工具（推荐）

1. **下载密钥生成工具**
   - 访问：https://opendocs.alipay.com/common/02kkv7
   - 下载支付宝提供的密钥生成工具

2. **生成密钥对**
   - 运行工具，选择"RSA2（推荐）"
   - 密钥长度选择"2048"
   - 点击"生成密钥"
   - 保存生成的私钥和公钥

### 3.2 使用 OpenSSL 生成（命令行）

```bash
# 生成私钥（2048位）
openssl genrsa -out app_private_key.pem 2048

# 生成公钥
openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem

# 查看私钥内容
cat app_private_key.pem

# 查看公钥内容
cat app_public_key.pem
```

### 3.3 上传应用公钥到支付宝

1. **登录沙箱控制台**
   - 访问：https://openhome.alipay.com/develop/sandbox/app
   - 选择您的应用

2. **配置接口加签方式**
   - 点击"接口加签方式" -> "设置"
   - 选择"公钥"模式（沙箱环境仅支持公钥模式）
   - 复制 `app_public_key.pem` 文件中的公钥内容（包含头尾标记）
   - 粘贴到"应用公钥"输入框
   - 点击"保存"

3. **获取支付宝公钥**
   - 保存后，页面会显示"支付宝公钥"
   - 复制这个公钥，用于配置 `ALIPAY_SANDBOX_PUBLIC_KEY`

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

配置完成后，运行配置检查工具：

```bash
python check_alipay_config.py
```

该工具会检查：
- ✓ 基本配置项是否存在
- ✓ APPID格式是否正确
- ✓ 私钥格式和长度是否正确
- ✓ 公钥格式和长度是否正确
- ✓ 回调地址配置
- ✓ 使用AlipaySandboxClient验证配置

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
  "payment_url": "https://openapi-sandbox.dl.alipaydev.com/gateway.do?...",
  "payment_provider": "alipay_sandbox"
}
```

### 2. 创建支付订单（官方验订单）

**接口**：`POST /api/payment/create/`

**请求参数**：
```json
{
  "order_id": 1,
  "order_type": "verified",
  "payment_provider": "alipay_sandbox"
}
```

### 3. 查询支付状态

**接口**：`GET /api/payment/query/<order_id>/?order_type=normal&payment_provider=alipay_sandbox`

**查询参数**：
- `order_type`: `normal` 或 `verified`

### 4. 管理端打款功能

在管理端的回收订单详情页面，当订单状态为 `completed` 或 `inspected` 时，可以执行打款操作。

**打款方式**：
- 选择打款方式为 `alipay`
- 输入用户的支付宝账号（手机号或邮箱）
- 系统会自动调用支付宝沙箱转账接口完成打款

## 七、测试流程

1. **使用沙箱买家账号登录支付宝**
   - 在沙箱控制台获取买家账号信息
   - 使用该账号登录支付宝（沙箱环境）

2. **创建订单并支付**
   - 在前端创建订单
   - 选择支付宝沙箱支付
   - 跳转到支付宝支付页面
   - 使用沙箱买家账号完成支付

3. **验证支付结果**
   - 支付成功后会自动跳转回前端页面
   - 订单状态会自动更新为 `paid`
   - 可以通过查询接口验证支付状态

## 八、注意事项

1. **私钥格式**：应用私钥必须是RSA2格式，包含 `-----BEGIN RSA PRIVATE KEY-----` 和 `-----END RSA PRIVATE KEY-----` 标记

2. **公钥格式**：支付宝公钥必须包含 `-----BEGIN PUBLIC KEY-----` 和 `-----END PUBLIC KEY-----` 标记

3. **回调地址**：
   - 本地开发：使用 `http://127.0.0.1:8000` 或 `http://localhost:8000`
   - 生产环境：必须使用公网可访问的HTTPS地址
   - 需要在支付宝开放平台配置回调地址白名单

4. **沙箱环境限制**：
   - 沙箱环境仅用于测试，不会产生真实交易
   - 沙箱账号有余额限制
   - 沙箱环境的数据不会影响生产环境

5. **订单号格式**：
   - 易淘订单：`normal_<order_id>`
   - 官方验订单：`verified_<order_id>`

## 九、常见问题

### 1. 签名验证失败
- 检查私钥和公钥格式是否正确
- 确认使用的是RSA2格式的密钥
- 检查密钥内容是否完整

### 2. 回调地址无法访问
- 本地开发需要使用内网穿透工具（如ngrok）
- 或使用支付宝提供的沙箱测试工具

### 3. 支付页面无法打开
- 检查网关地址是否正确
- 确认APPID和密钥配置正确
- 查看后端日志获取详细错误信息

## 十、相关文档

- 支付宝开放平台：https://open.alipay.com/
- 沙箱控制台：https://openhome.alipay.com/develop/sandbox/account
- 快速接入指南：https://opendocs.alipay.com/common/02kkv7
- 电脑网站支付文档：https://opendocs.alipay.com/open/270/105898

