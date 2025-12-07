# ngrok 配置指南

## 快速开始

### 1. 安装 ngrok

#### 方法一：手动下载（推荐）

1. 访问 https://ngrok.com/download
2. 下载 Windows 版本（ZIP 文件）
3. 解压到任意目录（如 `C:\ngrok`）
4. 将 `ngrok.exe` 所在目录添加到系统 PATH 环境变量

**添加到 PATH**：
- 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
- 在"系统变量"中找到 `Path`，点击"编辑"
- 点击"新建"，添加 ngrok.exe 所在目录（如 `C:\ngrok`）
- 点击"确定"保存

#### 方法二：使用包管理器

```powershell
# 如果安装了 Chocolatey
choco install ngrok

# 如果安装了 Scoop
scoop install ngrok
```

### 2. 注册 ngrok 账号

1. 访问 https://dashboard.ngrok.com/signup
2. 使用邮箱注册账号（免费）
3. 验证邮箱

### 3. 获取 authtoken

1. 登录后访问 https://dashboard.ngrok.com/get-started/your-authtoken
2. 复制您的 authtoken（类似：`2xxxxxxxxxxxxxxxxxxxxxxxxxxxxx_xxxxxxxxxxxxxxxxxxxxx`）

### 4. 配置 authtoken

#### 方法一：使用配置脚本（推荐）

```powershell
# 在项目 backend 目录下运行
.\setup_ngrok.ps1
```

脚本会引导您完成配置。

#### 方法二：手动配置

```powershell
ngrok config add-authtoken <your-authtoken>
```

### 5. 启动 ngrok

#### 方法一：使用启动脚本

```powershell
# 在项目 backend 目录下运行
.\start_ngrok.ps1
```

#### 方法二：手动启动

```powershell
# 确保 Django 服务正在运行
python manage.py runserver

# 在另一个终端启动 ngrok
ngrok http 8000
```

### 6. 获取公网地址

ngrok 启动后会显示类似以下信息：

```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       50ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**重要**：复制 `Forwarding` 中的 HTTPS 地址（如 `https://xxxx-xx-xx-xx-xx.ngrok-free.app`）

### 7. 更新配置

在 `backend/core/settings.py` 中更新 `BACKEND_URL`：

```python
# 开发环境配置（使用 ngrok）
BACKEND_URL = 'https://xxxx-xx-xx-xx-xx.ngrok-free.app'  # 替换为您的 ngrok 地址

# 或者根据环境变量动态配置
import os
if os.getenv('USE_NGROK'):
    BACKEND_URL = os.getenv('NGROK_URL', 'https://xxxx-xx-xx-xx-xx.ngrok-free.app')
else:
    BACKEND_URL = 'http://127.0.0.1:8000'
```

### 8. 配置支付宝回调地址

ngrok 地址配置后，支付宝异步通知地址会自动使用该地址：

```
https://xxxx-xx-xx-xx-xx.ngrok-free.app/api/payment/alipay/notify/
```

## 注意事项

### 1. 免费版限制

- **URL 会变化**：每次启动 ngrok，URL 都会变化（除非使用付费版）
- **需要重新配置**：URL 变化后，需要更新 `settings.py` 中的 `BACKEND_URL`
- **流量限制**：免费版有流量限制，但通常足够测试使用

### 2. 固定域名（付费版）

如果需要固定域名，可以：
- 升级到 ngrok 付费版
- 或使用其他内网穿透工具（如 natapp）

### 3. 同时运行多个服务

如果需要同时映射多个端口：

```powershell
# 终端 1：映射 8000 端口（后端）
ngrok http 8000

# 终端 2：映射 5173 端口（前端）
ngrok http 5173
```

### 4. ngrok Web 界面

ngrok 启动后，可以访问 http://127.0.0.1:4040 查看：
- 请求日志
- 请求详情
- 重放请求

## 测试

### 1. 测试 ngrok 连接

```powershell
# 启动 Django 服务
python manage.py runserver

# 启动 ngrok
ngrok http 8000

# 在浏览器中访问 ngrok 提供的地址
# 应该能看到 Django 应用的响应
```

### 2. 测试支付宝回调

1. 创建支付订单
2. 完成支付
3. 在 ngrok Web 界面（http://127.0.0.1:4040）查看请求日志
4. 确认支付宝回调请求已到达

## 常见问题

### Q: ngrok 启动后显示 "ERR_NGROK_108"

**A**: authtoken 未配置或配置错误，请重新运行 `ngrok config add-authtoken <your-token>`

### Q: 无法访问 ngrok 提供的地址

**A**: 
1. 检查 Django 服务是否正在运行
2. 检查防火墙设置
3. 确认 ngrok 显示的端口是否正确

### Q: URL 每次启动都变化

**A**: 这是免费版的限制，可以：
- 升级到付费版获得固定域名
- 或使用其他工具（如 natapp）

### Q: 如何停止 ngrok

**A**: 在运行 ngrok 的终端中按 `Ctrl+C`

## 生产环境

**注意**：ngrok 仅用于开发测试，生产环境应该：
- 部署到云服务器
- 使用真实域名
- 配置 SSL 证书

```python
# settings.py（生产环境）
if DEBUG:
    # 开发环境：使用 ngrok
    BACKEND_URL = os.getenv('NGROK_URL', 'http://127.0.0.1:8000')
else:
    # 生产环境：使用真实域名
    BACKEND_URL = 'https://api.yourdomain.com'
```

## 相关文档

- [ngrok 官方文档](https://ngrok.com/docs)
- [ngrok Dashboard](https://dashboard.ngrok.com/)
- [内网穿透方案对比](../INTRANET_PENETRATION_GUIDE.md)





