# Ngrok 端点冲突终极解决方案

## 问题分析

即使配置文件格式正确，仍然出现端点冲突，可能的原因：

1. **之前的 ngrok 进程还在运行**（最常见）
2. **ngrok 服务器端资源未释放**（需要等待更长时间）
3. **免费版限制**：同一个 authtoken 可能分配到相同地址
4. **ngrok Web 界面还在运行**：即使进程停止，Web 界面可能还在占用资源

## 完整解决步骤

### 步骤 1：完全清理所有 ngrok 相关进程和连接

```powershell
# 停止所有 ngrok 进程
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force

# 停止可能占用端口的进程
$ports = @(4040, 4041, 8000, 5173)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        Write-Host "端口 $port 被占用" -ForegroundColor Yellow
    }
}

# 等待 5 秒
Start-Sleep -Seconds 5

# 再次检查
Get-Process ngrok -ErrorAction SilentlyContinue
```

### 步骤 2：等待足够长的时间

**重要**：免费版 ngrok 可能需要 5-10 分钟才能完全释放资源。

```powershell
# 等待 60 秒（最少）
Start-Sleep -Seconds 60

# 或者等待 5 分钟（推荐）
Write-Host "等待 5 分钟让服务器释放资源..." -ForegroundColor Yellow
Start-Sleep -Seconds 300
```

### 步骤 3：验证配置文件格式

确认配置文件格式正确：

**ngrok-backend.yml**:
```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq
tunnels:
  backend:
    addr: 8000
    proto: http
```

**ngrok-frontend.yml**:
```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq
tunnels:
  frontend:
    addr: 5173
    proto: http
```

### 步骤 4：使用不同的启动策略

#### 策略 A：先启动后端，等待后再启动前端

```powershell
# 终端 1 - 先启动后端
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-backend.yml backend

# 等待后端完全启动（看到地址后）
# 然后等待 30 秒

# 终端 2 - 再启动前端
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-frontend.yml frontend
```

#### 策略 B：使用不同的区域（如果支持）

修改配置文件，添加区域设置：

```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq
tunnels:
  backend:
    addr: 8000
    proto: http
    region: us  # 美国区域
```

```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq
tunnels:
  frontend:
    addr: 5173
    proto: http
    region: jp  # 日本区域（您当前使用的）
```

#### 策略 C：使用 --pooling-enabled（需要付费版）

如果您的 ngrok 账户支持，可以使用负载均衡：

```powershell
ngrok start --config ngrok-backend.yml --pooling-enabled backend
ngrok start --config ngrok-frontend.yml --pooling-enabled frontend
```

### 步骤 5：检查 ngrok Web 界面

访问 ngrok Web 界面，查看是否有残留的隧道：

- 后端：`http://127.0.0.1:4040`
- 前端：`http://127.0.0.1:4041`

如果有残留的隧道，尝试在 Web 界面中停止它们。

## 临时解决方案

如果以上方法都不行，可以：

### 方案 1：只使用一个 ngrok 隧道

只启动后端 ngrok，前端继续使用 localhost：

```python
# settings.py
FRONTEND_URL = 'http://localhost:5173'  # 本地前端
BACKEND_URL = 'https://xxxx-backend.ngrok-free.dev'  # ngrok 后端
```

这样支付回调会通过后端重定向页面跳转回前端。

### 方案 2：使用不同的 ngrok 账户

如果有另一个 ngrok 账户，可以为前端使用不同的 authtoken。

### 方案 3：等待更长时间

有时需要等待 10-15 分钟让 ngrok 服务器完全释放资源。

## 一键清理脚本

```powershell
# 完全清理 ngrok
Write-Host "正在清理所有 ngrok 进程和连接..." -ForegroundColor Yellow

# 停止所有进程
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force

# 等待
Start-Sleep -Seconds 5

# 验证
$remaining = Get-Process ngrok -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "警告: 仍有进程在运行" -ForegroundColor Red
} else {
    Write-Host "✓ 所有进程已停止" -ForegroundColor Green
}

Write-Host ""
Write-Host "请等待 5-10 分钟后再重新启动" -ForegroundColor Yellow
```

## 验证清单

- [ ] 所有 ngrok 进程已停止
- [ ] 已等待至少 5 分钟
- [ ] 配置文件格式正确（version: 3, agent.authtoken）
- [ ] 使用不同的隧道名称（backend 和 frontend）
- [ ] 在不同的终端窗口启动
- [ ] 检查 ngrok Web 界面是否有残留隧道

## 如果问题持续

1. **重启计算机**：完全清理所有进程和连接
2. **联系 ngrok 支持**：可能是服务器端问题
3. **考虑升级到付费版**：付费版支持更多隧道和固定域名




