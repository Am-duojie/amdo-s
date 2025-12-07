# Ngrok 多隧道冲突解决方案

## 问题描述

当您同时启动前端和后端 ngrok 隧道时，如果它们使用相同的域名（如 `hypochondriacally-nondiscretionary-kylie.ngrok-free.dev`），会出现错误：

```
错误代码 NGROK_6030
网址有多个端点，但并非所有端点都启用了池化。
```

这是因为免费版 ngrok 不支持同一个域名映射到多个端口。

## 解决方案

### 方案 1：使用不同的 ngrok 配置文件（推荐）

为前端和后端创建不同的 ngrok 配置文件，这样它们会使用不同的域名。

#### 步骤 1：创建后端 ngrok 配置

在 `backend` 目录下创建 `ngrok-backend.yml`：

```yaml
version: "2"
authtoken: YOUR_NGROK_AUTH_TOKEN  # 替换为您的 ngrok authtoken
tunnels:
  backend:
    addr: 8000
    proto: http
```

#### 步骤 2：创建前端 ngrok 配置

在 `backend` 目录下创建 `ngrok-frontend.yml`：

```yaml
version: "2"
authtoken: YOUR_NGROK_AUTH_TOKEN  # 替换为您的 ngrok authtoken
tunnels:
  frontend:
    addr: 5173
    proto: http
```

#### 步骤 3：使用配置文件启动

**后端 ngrok**（在第一个终端）：
```powershell
ngrok start --config ngrok-backend.yml backend
```

**前端 ngrok**（在第二个终端）：
```powershell
ngrok start --config ngrok-frontend.yml frontend
```

### 方案 2：在不同的终端窗口启动（简单但可能冲突）

如果您不想创建配置文件，可以在不同的终端窗口分别启动：

**终端 1 - 后端 ngrok**：
```powershell
ngrok http 8000
```

**终端 2 - 前端 ngrok**：
```powershell
ngrok http 5173
```

**注意**：这种方法可能会随机分配到相同的域名，如果遇到冲突，需要重新启动。

### 方案 3：使用 ngrok 的多个隧道功能（需要付费版）

如果您有 ngrok 付费账户，可以在一个配置文件中定义多个隧道：

```yaml
version: "2"
authtoken: YOUR_NGROK_AUTH_TOKEN
tunnels:
  backend:
    addr: 8000
    proto: http
  frontend:
    addr: 5173
    proto: http
```

然后使用：
```powershell
ngrok start --all --config ngrok.yml
```

## 推荐操作步骤

### 1. 停止当前所有 ngrok 进程

在运行 ngrok 的终端窗口按 `Ctrl+C` 停止所有 ngrok 进程。

### 2. 获取 ngrok authtoken

如果您还没有 authtoken，访问 https://dashboard.ngrok.com/get-started/your-authtoken 获取。

### 3. 创建配置文件并启动

使用方案 1（推荐），创建两个配置文件并分别启动。

### 4. 更新 settings.py

启动后，您会得到两个不同的 ngrok 地址：

- **后端地址**：`https://xxxx-backend.ngrok-free.dev` → `http://localhost:8000`
- **前端地址**：`https://yyyy-frontend.ngrok-free.dev` → `http://localhost:5173`

更新 `backend/core/settings.py`：

```python
# 前端地址（使用前端 ngrok 公网地址）
FRONTEND_URL = 'https://yyyy-frontend.ngrok-free.dev'  # 替换为您的前端 ngrok 地址

# 后端地址（使用后端 ngrok 公网地址）
BACKEND_URL = 'https://xxxx-backend.ngrok-free.dev'  # 替换为您的后端 ngrok 地址
```

## 快速脚本

我已经创建了 PowerShell 脚本来帮助您：

- `start_ngrok_backend.ps1` - 启动后端 ngrok（使用配置文件）
- `start_ngrok_frontend.ps1` - 启动前端 ngrok（使用配置文件）
- `start_ngrok_both.ps1` - 同时启动两个 ngrok（需要付费版）

## 验证

启动后，检查：

1. **后端 ngrok** 应该显示：
   ```
   Forwarding  https://xxxx-backend.ngrok-free.dev -> http://localhost:8000
   ```

2. **前端 ngrok** 应该显示：
   ```
   Forwarding  https://yyyy-frontend.ngrok-free.dev -> http://localhost:5173
   ```

3. 两个地址应该**不同**。

4. 分别访问两个地址，确认都能正常工作。

## 如果仍然遇到问题

1. **确认两个 ngrok 进程都在运行**：
   ```powershell
   Get-Process ngrok
   ```

2. **检查 ngrok Web 界面**：
   - 后端：`http://127.0.0.1:4040`
   - 前端：`http://127.0.0.1:4041`（如果端口冲突会自动使用下一个端口）

3. **查看 ngrok 日志**：在终端窗口中查看是否有错误信息。

4. **重启 ngrok**：完全停止所有 ngrok 进程，然后重新启动。



