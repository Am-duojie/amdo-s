# 手动启动前后端 Ngrok 指南

## 前提条件

1. **已安装 ngrok**：确保 ngrok 已安装并添加到 PATH
2. **获取 authtoken**：访问 https://dashboard.ngrok.com/get-started/your-authtoken 获取您的 authtoken
3. **服务正在运行**：
   - 后端 Django：`python manage.py runserver`（端口 8000）
   - 前端服务：`npm run dev`（端口 5173）

## 方法一：使用配置文件（推荐，避免冲突）

### 步骤 1：创建后端 ngrok 配置文件

在 `backend` 目录下创建文件 `ngrok-backend.yml`：

```yaml
version: "2"
authtoken: YOUR_NGROK_AUTHTOKEN  # 替换为您的 authtoken
tunnels:
  backend:
    addr: 8000
    proto: http
```

### 步骤 2：创建前端 ngrok 配置文件

在 `backend` 目录下创建文件 `ngrok-frontend.yml`：

```yaml
version: "2"
authtoken: YOUR_NGROK_AUTHTOKEN  # 替换为您的 authtoken（与后端相同）
tunnels:
  frontend:
    addr: 5173
    proto: http
```

### 步骤 3：启动后端 ngrok

打开**第一个终端窗口**，进入 `backend` 目录：

```powershell
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-backend.yml backend
```

您会看到类似以下输出：

```
Forwarding  https://xxxx-backend.ngrok-free.dev -> http://localhost:8000
```

**复制这个地址**：`https://xxxx-backend.ngrok-free.dev`

### 步骤 4：启动前端 ngrok

打开**第二个终端窗口**，进入 `backend` 目录：

```powershell
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-frontend.yml frontend
```

您会看到类似以下输出：

```
Forwarding  https://yyyy-frontend.ngrok-free.dev -> http://localhost:5173
```

**复制这个地址**：`https://yyyy-frontend.ngrok-free.dev`

### 步骤 5：更新 settings.py

打开 `backend/core/settings.py`，更新配置：

```python
# 前端地址（使用前端 ngrok 公网地址）
FRONTEND_URL = 'https://yyyy-frontend.ngrok-free.dev'  # 替换为您的前端 ngrok 地址

# 后端地址（使用后端 ngrok 公网地址）
BACKEND_URL = 'https://xxxx-backend.ngrok-free.dev'  # 替换为您的后端 ngrok 地址
```

## 方法二：直接启动（简单但可能冲突）

### 启动后端 ngrok

打开**第一个终端窗口**：

```powershell
ngrok http 8000
```

您会看到类似以下输出：

```
Forwarding  https://xxxx.ngrok-free.dev -> http://localhost:8000
```

**复制这个地址**，更新 `settings.py` 中的 `BACKEND_URL`。

### 启动前端 ngrok

打开**第二个终端窗口**：

```powershell
ngrok http 5173
```

您会看到类似以下输出：

```powershell
Forwarding  https://yyyy.ngrok-free.dev -> http://localhost:5173
```

**复制这个地址**，更新 `settings.py` 中的 `FRONTEND_URL`。

⚠️ **注意**：如果两个 ngrok 分配到相同的地址，会出现冲突。如果遇到这种情况，请使用方法一（配置文件方式）。

## 方法三：使用 ngrok authtoken 命令（首次使用）

如果是第一次使用 ngrok，需要先配置 authtoken：

```powershell
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

然后使用方法一或方法二启动。

## 验证配置

### 1. 检查后端 ngrok

在浏览器中访问：`https://您的后端ngrok地址/api/`

应该看到 API 根目录的 JSON 响应。

### 2. 检查前端 ngrok

在浏览器中访问：`https://您的前端ngrok地址`

应该看到前端页面正常加载。

### 3. 检查 ngrok Web 界面

- 后端 ngrok Web 界面：`http://127.0.0.1:4040`
- 前端 ngrok Web 界面：`http://127.0.0.1:4041`（如果端口冲突会自动使用下一个端口）

在 Web 界面中可以查看：
- 请求日志
- 请求/响应详情
- 隧道状态

## 完整启动流程示例

### 终端 1 - Django 后端
```powershell
cd D:\AAA\毕业设计\backend
python manage.py runserver
```

### 终端 2 - 前端服务
```powershell
cd D:\AAA\毕业设计\frontend
npm run dev
```

### 终端 3 - 后端 ngrok
```powershell
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-backend.yml backend
```

### 终端 4 - 前端 ngrok
```powershell
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-frontend.yml frontend
```

## 常见问题

### Q1: 两个 ngrok 使用相同地址怎么办？

**A**: 使用配置文件方式（方法一）可以避免这个问题。如果仍然冲突：
1. 完全停止所有 ngrok 进程
2. 等待 30 秒
3. 重新启动（先启动后端，再启动前端）

### Q2: 如何查看 ngrok 地址？

**A**: 
- 在终端窗口中查看 "Forwarding" 行
- 访问 ngrok Web 界面：`http://127.0.0.1:4040` 或 `http://127.0.0.1:4041`
- 使用 API：`curl http://127.0.0.1:4040/api/tunnels`

### Q3: ngrok 地址会变化吗？

**A**: 是的，每次重启 ngrok，地址可能会变化。需要重新更新 `settings.py`。

### Q4: 如何停止 ngrok？

**A**: 在运行 ngrok 的终端窗口按 `Ctrl+C`。

### Q5: 可以固定 ngrok 地址吗？

**A**: 免费版不支持固定地址。需要付费版才能使用固定域名。

## 快速命令参考

```powershell
# 配置 authtoken（首次使用）
ngrok config add-authtoken YOUR_AUTHTOKEN

# 启动后端 ngrok（配置文件方式）
ngrok start --config ngrok-backend.yml backend

# 启动前端 ngrok（配置文件方式）
ngrok start --config ngrok-frontend.yml frontend

# 启动后端 ngrok（直接方式）
ngrok http 8000

# 启动前端 ngrok（直接方式）
ngrok http 5173

# 查看 ngrok 配置
ngrok config check

# 查看所有隧道
curl http://127.0.0.1:4040/api/tunnels
```

## 下一步

启动完成后：
1. ✅ 更新 `settings.py` 中的 `FRONTEND_URL` 和 `BACKEND_URL`
2. ✅ 重启 Django 服务（如果需要）
3. ✅ 测试支付流程，确认支付后能正常跳转


