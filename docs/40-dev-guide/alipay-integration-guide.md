# 支付宝支付功能配置与开发指南

> 本文档面向需要在本项目中配置或开发支付宝支付功能的开发者。

## 目录

1. [快速开始](#快速开始)
2. [支付宝账号准备](#支付宝账号准备)
3. [密钥配置](#密钥配置)
4. [本地开发配置](#本地开发配置)
5. [代码实现说明](#代码实现说明)
6. [接口使用](#接口使用)
7. [常见问题](#常见问题)
8. [生产环境部署](#生产环境部署)

---

## 快速开始

### 前置条件

- Python 3.8+
- 已安装项目依赖：`pip install -r requirements.txt`
- 支付宝开放平台账号（沙箱或正式）

### 配置步骤概览

1. 注册支付宝开放平台账号并创建应用
2. 生成 RSA2 密钥对
3. 上传应用公钥到支付宝平台
4. 配置 `backend/core/settings.py`
5. 本地开发配置内网穿透（ngrok）
6. 测试支付流程

---

## 支付宝账号准备

### 1. 注册与登录

**沙箱环境（推荐用于开发测试）**：
- 访问：https://open.alipay.com/
- 使用支付宝账号登录
- 进入"开发者中心" → "研发服务" → "沙箱"

**生产环境**：
- 需要完成企业实名认证
- 创建正式应用

### 2. 创建应用

1. 进入控制台 → "网页&移动应用"
2. 点击"创建应用"
3. 填写应用信息：
   - 应用名称：您的应用名称
   - 应用类型：网页应用
   - 行业分类：选择您的行业
4. 创建成功后，记录 **APPID**（例如：`9021000158624650`）

---

## 密钥配置

### 1. 生成 RSA2 密钥对

**方法一：使用 OpenSSL（推荐）**

```bash
# 生成私钥（2048位）
openssl genrsa -out app_private_key.pem 2048

# 从私钥生成公钥
openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem
```

**方法二：使用支付宝密钥生成工具**

- 下载地址：https://opendocs.alipay.com/common/02kkv7
- 选择 RSA2（2048位）
- 生成密钥对

### 2. 上传应用公钥

1. 在应用详情页，找到"接口加签方式" → 点击"设置"
2. 选择"公钥"模式
3. 打开 `app_public_key.pem` 文件，复制完整内容（包含 `-----BEGIN PUBLIC KEY-----` 和 `-----END PUBLIC KEY-----`）
4. 粘贴到"应用公钥"输入框
5. 点击"保存"

### 3. 获取支付宝公钥

- 保存后，页面会显示"支付宝公钥"
- 复制这个公钥（完整内容），用于配置 `ALIPAY_PUBLIC_KEY`

### 4. 配置 settings.py

编辑 `backend/core/settings.py`，找到支付宝配置部分（约第 240 行）：

```python
# ========== 支付宝支付配置 ==========

# 支付宝网关地址
# 沙箱环境（开发测试）
ALIPAY_GATEWAY_URL = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
# 生产环境（上线后使用）
# ALIPAY_GATEWAY_URL = 'https://openapi.alipay.com/gateway.do'

# 应用配置
ALIPAY_APP_ID = '您的APPID'  # 从支付宝控制台获取

# 应用私钥（您生成的私钥）
ALIPAY_APP_PRIVATE_KEY = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA...（您的私钥内容）...
-----END RSA PRIVATE KEY-----
'''

# 支付宝公钥（从支付宝平台获取）
ALIPAY_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...（支付宝返回的公钥）...
-----END PUBLIC KEY-----
'''

# 前后端URL配置
FRONTEND_URL = 'http://localhost:5173'  # 前端地址
BACKEND_URL = 'http://127.0.0.1:8000'  # 后端地址（本地开发先用这个）
```

**重要提示**：
- 私钥必须妥善保管，不要泄露或提交到代码仓库
- 支付宝公钥必须从支付宝平台获取，不能自己生成
- 密钥可以是完整格式（含头尾标记）或仅 Base64 字符串

---

## 本地开发配置

### 问题说明

支付宝异步通知需要公网可访问的地址，本地开发环境（`http://127.0.0.1:8000`）无法接收支付宝的回调通知。

### 解决方案：使用 ngrok 内网穿透

#### 1. 安装 ngrok

**Windows**：
```powershell
# 使用 Chocolatey
choco install ngrok

# 或下载安装包
# 访问 https://ngrok.com/download
```

**macOS**：
```bash
brew install ngrok
```

**Linux**：
```bash
# 下载并解压
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

#### 2. 注册 ngrok 账号

1. 访问 https://ngrok.com/
2. 注册账号并登录
3. 获取 authtoken：https://dashboard.ngrok.com/get-started/your-authtoken
4. 配置 authtoken：
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

#### 3. 启动 ngrok 隧道

**启动后端隧道（8000端口）**：
```bash
ngrok http 8000
```

**输出示例**：
```
Forwarding  https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev -> http://localhost:8000
```

#### 4. 配置 BACKEND_URL

将 ngrok 生成的公网地址配置到 `settings.py`：

```python
# backend/core/settings.py
BACKEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'
```

#### 5. 验证配置

在浏览器访问：
```
https://your-ngrok-url.ngrok-free.dev/api/payment/alipay/notify/
```

应该能看到 Django 的响应（即使返回错误，也说明地址可访问）。

---

## 代码实现说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `backend/app/secondhand_app/alipay_client.py` | 支付宝客户端类，封装所有支付宝接口 |
| `backend/app/secondhand_app/payment_views.py` | 支付相关视图（创建支付、查询、回调） |
| `backend/core/urls.py` | 路由配置 |

### 关键接口

#### 1. 创建支付订单

**接口**：`alipay.trade.page.pay`（电脑网站支付）

**实现位置**：`alipay_client.py` → `create_trade()` 方法

**流程**：
1. 构建业务参数（`biz_content`）
2. 构建请求参数（包含 `return_url`、`notify_url`）
3. 使用 RSA2 算法签名
4. 构建支付 URL
5. 返回支付 URL 给前端

#### 2. 异步通知处理

**接口**：`/api/payment/alipay/notify/`

**实现位置**：`payment_views.py` → `alipay_payment_notify()` 视图

**流程**：
1. 接收支付宝 POST 请求
2. 验证签名（使用支付宝公钥）
3. 解析订单号和支付状态
4. 更新订单状态为 `paid`
5. 返回 `success` 给支付宝

#### 3. 查询支付状态

**接口**：`alipay.trade.query`

**实现位置**：`alipay_client.py` → `query_trade()` 方法

**流程**：
1. 构建查询参数
2. 调用支付宝查询接口
3. 返回支付状态

### 签名算法说明

支付宝使用 **RSA2（SHA256withRSA）** 签名算法：

**签名步骤**：
1. 筛选参数：排除 `sign` 参数，**保留 `sign_type`**
2. 排序：按参数名 ASCII 码排序
3. 拼接：`key1=value1&key2=value2`
4. 签名：SHA256 哈希 → RSA2 签名 → Base64 编码

**关键点**：
- `sign_type` 必须参与签名（常见错误）
- 参数值使用原始值（不进行 URL 编码）
- URL 编码只在构建 URL 时进行

**代码位置**：`alipay_client.py` → `_sign()` 方法

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
    "order_type": "normal"  // normal: 普通订单, verified: 官方验订单
}
```

**响应**：
```json
{
    "success": true,
    "payment_url": "https://openapi-sandbox.dl.alipaydev.com/gateway.do?app_id=...",
    "payment_provider": "alipay"
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

### 3. 异步通知（支付宝调用）

**请求**（由支付宝发起）：
```http
POST /api/payment/alipay/notify/
Content-Type: application/x-www-form-urlencoded

out_trade_no=normal_90&trade_status=TRADE_SUCCESS&trade_no=2024...&sign=...
```

**响应**：
```
success
```

---

## 常见问题

### Q1: 签名验证失败（invalid-signature）

**原因**：
- `sign_type` 参数被错误排除（最常见）
- 应用公钥与私钥不匹配
- 支付宝公钥配置错误
- JSON 字符串格式问题

**解决方案**：
1. 确认 `sign_type` 参与签名（查看 `alipay_client.py` 第 199-205 行）
2. 重新生成密钥对并上传应用公钥
3. 从支付宝平台重新获取支付宝公钥
4. 使用 `ensure_ascii=False` 保持中文字符原样

### Q2: 本地开发收不到异步通知

**原因**：
- 本地地址（`http://127.0.0.1:8000`）无法被支付宝访问

**解决方案**：
1. 使用 ngrok 内网穿透（见上文"本地开发配置"）
2. 配置 `BACKEND_URL` 为 ngrok 公网地址
3. 验证地址可访问性

### Q3: 支付页面空白或无法打开

**原因**：
- 网关地址配置错误
- APPID 或密钥配置错误
- 签名计算错误

**解决方案**：
1. 检查 `ALIPAY_GATEWAY_URL` 是否正确（沙箱/生产）
2. 确认 APPID 和密钥配置正确
3. 查看后端日志获取详细错误信息

### Q4: 订单状态未更新

**原因**：
- 异步通知未收到
- 签名验证失败
- 订单号解析错误

**解决方案**：
1. 查看后端日志确认是否收到通知
2. 检查签名验证逻辑
3. 使用查询接口手动同步状态

### Q5: 沙箱环境与生产环境切换

**步骤**：
1. 修改 `ALIPAY_GATEWAY_URL`：
   - 沙箱：`https://openapi-sandbox.dl.alipaydev.com/gateway.do`
   - 生产：`https://openapi.alipay.com/gateway.do`
2. 更换 APPID（生产环境应用的 APPID）
3. 更换密钥对（生产环境应用的密钥）
4. 更新 `BACKEND_URL` 为生产环境公网地址（HTTPS）

---

## 生产环境部署

### 1. 配置检查清单

- [ ] 使用生产环境网关地址
- [ ] 使用生产环境 APPID
- [ ] 使用生产环境密钥对
- [ ] `BACKEND_URL` 配置为 HTTPS 公网地址
- [ ] `FRONTEND_URL` 配置为 HTTPS 公网地址
- [ ] 私钥已从环境变量或密钥管理服务读取（不硬编码）
- [ ] 支付宝应用已通过审核并上线

### 2. 安全建议

**私钥管理**：
```python
# 推荐：从环境变量读取
import os
ALIPAY_APP_PRIVATE_KEY = os.environ.get('ALIPAY_APP_PRIVATE_KEY')

# 或使用密钥管理服务（如 AWS Secrets Manager、Azure Key Vault）
```

**HTTPS 要求**：
- 生产环境必须使用 HTTPS
- 配置 SSL 证书（Let's Encrypt 免费证书）
- 确保回调地址支持 HTTPS

**日志记录**：
- 记录所有支付相关操作
- 不要在日志中记录完整私钥
- 记录签名原文用于调试

### 3. 测试流程

1. **沙箱环境测试**：
   - 使用沙箱账号完成支付流程
   - 验证异步通知接收
   - 验证订单状态更新

2. **生产环境测试**：
   - 使用小额订单测试
   - 验证完整支付流程
   - 验证退款流程（如有）

3. **压力测试**：
   - 模拟并发支付请求
   - 验证系统稳定性

---

## 相关文档

### 支付宝官方文档
- [支付宝开放平台](https://open.alipay.com/)
- [快速接入指南](https://opendocs.alipay.com/common/02kkv7)
- [电脑网站支付](https://opendocs.alipay.com/open/270/105898)
- [签名验签文档](https://opendocs.alipay.com/common/02kipl)

### 项目内部文档
- 支付宝沙箱接口梳理：`docs/_archive/支付宝沙箱接口梳理.md`
- 支付宝签名修复总结：`docs/_archive/ALIPAY_SIGNATURE_FIX_SUMMARY.md`
- 内网穿透指南：`docs/_archive/INTRANET_PENETRATION_GUIDE.md`

### 代码位置
- 支付宝客户端：`backend/app/secondhand_app/alipay_client.py`
- 支付视图：`backend/app/secondhand_app/payment_views.py`
- 配置文件：`backend/core/settings.py`（第 240-290 行）

---

## 附录：配置示例

### settings.py 完整配置示例

```python
# ========== 支付宝支付配置 ==========

# 支付宝网关地址
ALIPAY_GATEWAY_URL = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'  # 沙箱环境

# 应用配置
ALIPAY_APP_ID = '9021000158624650'  # 沙箱 APPID

# 应用私钥（RSA2，2048位）
ALIPAY_APP_PRIVATE_KEY = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEApdiTemjXz2N105BvALkPBuHrp2dJwNJnO9SqtGGfXq+Lvu8r
（省略中间内容）
-----END RSA PRIVATE KEY-----
'''

# 支付宝公钥
ALIPAY_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjvYXLvwQOhTEtpuDEGJB
（省略中间内容）
-----END PUBLIC KEY-----
'''

# 前后端URL配置
FRONTEND_URL = 'http://localhost:5173'  # 前端地址
BACKEND_URL = 'https://your-ngrok-url.ngrok-free.dev'  # 后端 ngrok 地址
```

### ngrok 配置文件示例（可选）

创建 `ngrok.yml`：

```yaml
version: "2"
authtoken: YOUR_AUTHTOKEN
tunnels:
  backend:
    proto: http
    addr: 8000
  frontend:
    proto: http
    addr: 5173
```

启动：
```bash
ngrok start --all --config ngrok.yml
```

---

## 总结

支付宝支付功能配置的核心要点：

1. **密钥配置**：正确生成和配置 RSA2 密钥对
2. **签名算法**：严格按照官方文档实现，`sign_type` 必须参与签名
3. **内网穿透**：本地开发使用 ngrok 使回调地址可访问
4. **环境切换**：沙箱/生产环境配置的区别
5. **安全性**：私钥保护、HTTPS、日志记录

遵循本文档，可以成功配置并开发支付宝支付功能。如有问题，请查看项目内部文档或联系项目维护者。



