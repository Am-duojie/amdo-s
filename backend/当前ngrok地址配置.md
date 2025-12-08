# 当前 Ngrok 地址配置

## 已配置的地址1

### 后端地址
```
https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev -> http://localhost:8000
```

### 前端地址
```
https://georgianna-presanitary-clair.ngrok-free.dev -> http://localhost:5173
```

## 已更新的配置

### 1. 后端配置 (`backend/core/settings.py`)

```python
# 前端地址配置
FRONTEND_URL = 'https://georgianna-presanitary-clair.ngrok-free.dev'  # 前端 ngrok 地址

# 后端地址（使用 ngrok 内网穿透地址）
BACKEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'  # 后端 ngrok 地址
```

### 2. 前端配置（需要手动配置）

#### 方法 A：创建 `.env` 文件（推荐）

在 `frontend` 目录下创建 `.env` 文件：

```env
VITE_BACKEND_NGROK_URL=https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev
```

然后重启前端服务。

#### 方法 B：浏览器控制台（临时）

访问前端地址后，在浏览器控制台运行：

```javascript
localStorage.setItem('BACKEND_NGROK_URL', 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev')
location.reload()
```

## 验证配置

### 1. 验证后端

访问：`https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev/api/`

应该看到 API 根目录的 JSON 响应。

### 2. 验证前端

访问：`https://georgianna-presanitary-clair.ngrok-free.dev`

应该能看到前端页面，并且能正常加载数据。

### 3. 验证 API 连接

在浏览器控制台（访问前端地址后）检查：

```javascript
// 应该显示后端地址
console.log(localStorage.getItem('BACKEND_NGROK_URL'))
```

## 重启服务

配置更新后，建议重启：

1. **Django 后端**（如果需要）：
   ```powershell
   # 在运行 Django 的终端按 Ctrl+C，然后重新启动
   python manage.py runserver
   ```

2. **前端服务**（如果使用 .env 文件）：
   ```powershell
   # 在运行前端的终端按 Ctrl+C，然后重新启动
   npm run dev
   ```

## 注意事项

1. **地址变化**：每次重启 ngrok，地址可能变化，需要重新更新配置
2. **CORS**：确保后端 `CORS_ALLOW_ALL_ORIGINS = True`
3. **HTTPS**：ngrok 使用 HTTPS，确保所有配置使用 `https://`

## 当前状态

- ✅ 后端 `settings.py` 已更新
- ⚠️ 前端需要手动配置（创建 `.env` 或在浏览器控制台设置）







