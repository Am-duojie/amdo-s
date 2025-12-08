# 内网穿透方案指南 - 支付宝回调地址配置

## ZeroTier 方案说明

### ZeroTier 工作原理

ZeroTier 是一个软件定义的网络（SDN）解决方案，可以创建虚拟局域网（VLAN）。但它**不是传统的内网穿透工具**。

**特点**：
- ✅ 可以在多台设备间创建虚拟网络
- ✅ 设备通过 ZeroTier 分配的虚拟 IP 相互访问
- ❌ **支付宝服务器不在您的 ZeroTier 网络中，无法直接访问**

### ZeroTier 的局限性

对于支付宝异步通知场景：

1. **支付宝服务器无法访问**：
   - 支付宝的服务器不在您的 ZeroTier 网络中
   - 无法通过 ZeroTier 虚拟 IP 访问您的本地服务
   - ZeroTier 主要用于设备间的点对点连接

2. **需要公网 IP 中转**：
   - 如果有一台有公网 IP 的服务器在 ZeroTier 网络中
   - 可以在这台服务器上配置反向代理
   - 但这样就不如直接使用内网穿透工具方便

## 推荐的内网穿透方案

### 方案 1：ngrok（推荐，最简单）

**优点**：
- ✅ 免费版本可用
- ✅ 配置简单
- ✅ 自动生成 HTTPS 地址
- ✅ 支持 WebSocket

**安装和使用**：

```bash
# 1. 下载 ngrok
# Windows: 从 https://ngrok.com/download 下载
# 或使用包管理器
choco install ngrok  # Chocolatey
# 或
scoop install ngrok  # Scoop

# 2. 注册账号并获取 authtoken
# 访问 https://dashboard.ngrok.com/get-started/your-authtoken

# 3. 配置 authtoken
ngrok config add-authtoken <your-authtoken>

# 4. 启动内网穿透（映射本地 8000 端口）
ngrok http 8000

# 输出示例：
# Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8000
```

**配置支付宝回调地址**：

```python
# settings.py
BACKEND_URL = 'https://xxxx-xx-xx-xx-xx.ngrok-free.app'  # 使用 ngrok 生成的地址
```

**注意事项**：
- 免费版每次启动 URL 会变化（需要重新配置）
- 付费版可以固定域名
- 有流量限制

### 方案 2：natapp（国内，稳定）

**优点**：
- ✅ 国内服务，速度快
- ✅ 免费版可用
- ✅ 支持固定域名（付费）

**安装和使用**：

```bash
# 1. 下载 natapp
# 访问 https://natapp.cn/ 下载

# 2. 注册账号并获取 authtoken

# 3. 启动（Windows）
natapp.exe -authtoken=<your-authtoken> -subdomain=<your-subdomain> -port=8000

# 或使用配置文件 config.ini
# authtoken=your-token
# subdomain=your-subdomain
```

**配置**：

```python
# settings.py
BACKEND_URL = 'https://your-subdomain.natapp1.cc'  # 使用 natapp 生成的地址
```

### 方案 3：frp（自建，最灵活）

**优点**：
- ✅ 完全控制
- ✅ 可以自建服务器
- ✅ 免费开源

**缺点**：
- ❌ 需要一台有公网 IP 的服务器
- ❌ 配置相对复杂

**安装和使用**：

```bash
# 1. 在有公网 IP 的服务器上部署 frps（服务端）
# 2. 在本地部署 frpc（客户端）
# 3. 配置 frpc.ini

[common]
server_addr = your-server-ip
server_port = 7000
token = your-token

[web]
type = http
local_port = 8000
custom_domains = your-domain.com
```

### 方案 4：使用云服务器（生产环境推荐）

**最佳实践**：
- 部署到云服务器（阿里云、腾讯云等）
- 配置域名和 SSL 证书
- 使用真实的公网地址

```python
# settings.py（生产环境）
ALIPAY_GATEWAY_URL = 'https://openapi.alipay.com/gateway.do'
BACKEND_URL = 'https://api.yourdomain.com'  # 真实的公网地址
FRONTEND_URL = 'https://www.yourdomain.com'
```

## ZeroTier 替代方案（如果必须使用）

如果您确实想使用 ZeroTier，需要以下配置：

### 方案 A：ZeroTier + 公网服务器中转

1. **在公网服务器上**：
   - 安装 ZeroTier 并加入网络
   - 配置 Nginx 反向代理
   - 将公网请求转发到 ZeroTier 网络中的本地服务

```nginx
# nginx.conf
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://10.147.20.x:8000;  # ZeroTier 虚拟 IP
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **在本地**：
   - 安装 ZeroTier 并加入同一网络
   - 启动 Django 服务

**缺点**：需要额外的公网服务器，不如直接使用内网穿透工具方便。

### 方案 B：ZeroTier + Tailscale（更简单）

Tailscale 是基于 WireGuard 的 VPN 服务，类似 ZeroTier 但更易用：

```bash
# 1. 安装 Tailscale
# 2. 注册账号
# 3. 在多台设备上登录
# 4. 通过 Tailscale IP 访问
```

但同样的问题：支付宝服务器不在您的 Tailscale 网络中。

## 本地开发建议

### 临时方案：跳过异步通知

如果只是本地测试，可以：

1. **仅测试支付页面跳转**：
   - 创建支付订单后跳转到支付宝
   - 完成支付后手动查询订单状态
   - 不依赖异步通知

2. **手动更新订单状态**：
   - 支付完成后，通过查询接口同步订单状态
   - 或手动在后台更新

### 开发环境配置

```python
# settings.py（开发环境）
if DEBUG:
    # 本地开发，不使用异步通知
    BACKEND_URL = 'http://127.0.0.1:8000'
    # 或者使用内网穿透
    # BACKEND_URL = 'https://xxxx.ngrok-free.app'
else:
    # 生产环境
    BACKEND_URL = 'https://api.yourdomain.com'
```

## 推荐方案对比

| 方案 | 难度 | 成本 | 稳定性 | 适用场景 |
|------|------|------|--------|----------|
| ngrok | ⭐ | 免费/付费 | ⭐⭐⭐ | 快速测试 |
| natapp | ⭐ | 免费/付费 | ⭐⭐⭐⭐ | 国内开发 |
| frp | ⭐⭐⭐ | 服务器成本 | ⭐⭐⭐⭐⭐ | 自建服务 |
| 云服务器 | ⭐⭐ | 服务器成本 | ⭐⭐⭐⭐⭐ | 生产环境 |
| ZeroTier | ⭐⭐⭐⭐ | 免费 | ⭐⭐ | 不推荐用于此场景 |

## 总结

**对于支付宝回调地址配置**：

1. **本地开发**：
   - 推荐使用 **ngrok** 或 **natapp**
   - 简单快速，适合测试

2. **生产环境**：
   - 使用**云服务器**部署
   - 配置真实域名和 SSL 证书

3. **ZeroTier**：
   - ❌ **不适用于支付宝回调场景**
   - 因为支付宝服务器不在您的 ZeroTier 网络中
   - 如果必须使用，需要额外的公网服务器中转

**最佳实践**：
- 开发环境：使用 ngrok 或 natapp 快速测试
- 生产环境：部署到云服务器，使用真实域名










