# 前端 ngrok 隧道配置指南

## 为什么需要前端 ngrok 隧道？

### 问题背景

当支付宝支付完成后，会通过 `return_url` 跳转回前端页面。如果前端是 `localhost:5173`：
- 支付宝从外部跳转回来时，无法访问 `localhost`
- 导致支付完成后无法自动跳转回前端

### 解决方案

使用 ngrok 为前端也创建一个公网隧道，这样：
- 支付宝可以正确跳转到前端页面
- 支付流程可以完全自动化
- 用户体验更好

## 配置步骤

### 步骤 1：启动前端服务

确保前端服务正在运行：

```powershell
# 在 frontend 目录下
cd frontend
npm run dev
```

前端应该运行在 `http://localhost:5173`

### 步骤 2：启动前端 ngrok 隧道

**方法一：使用启动脚本（推荐）**

```powershell
# 在 backend 目录下
cd backend
.\start_ngrok_frontend.ps1
```

**方法二：手动启动**

```powershell
# 新开一个终端窗口
ngrok http 5173
```

### 步骤 3：获取前端 ngrok 地址

ngrok 启动后会显示类似以下信息：

```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       50ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app -> http://localhost:5173

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**重要**：复制 `Forwarding` 中的 HTTPS 地址（如 `https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app`）

### 步骤 4：更新配置

在 `backend/core/settings.py` 中更新 `FRONTEND_URL`：

```python
# 前端地址（使用 ngrok 公网地址）
FRONTEND_URL = 'https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app'  # 前端 ngrok 地址

# 后端地址（使用 ngrok 公网地址）
BACKEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'  # 后端 ngrok 地址
```

### 步骤 5：重启服务（如果需要）

如果 Django 服务正在运行，可能需要重启以加载新配置：

```powershell
# 停止当前服务（Ctrl+C）
# 重新启动
python manage.py runserver
```

## 完整配置示例

### 前后端都使用 ngrok

```python
# backend/core/settings.py

# 前端地址（前端 ngrok 隧道）
FRONTEND_URL = 'https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app'

# 后端地址（后端 ngrok 隧道）
BACKEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'
```

### 工作流程

1. **用户访问前端**：`https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app`（前端 ngrok）
2. **创建支付**：前端调用后端 API（通过 vite proxy 或直接调用后端 ngrok 地址）
3. **支付完成**：支付宝跳转到后端重定向页面（后端 ngrok）
4. **自动重定向**：后端重定向页面跳转到前端支付回调页面（前端 ngrok）
5. **查询状态**：前端支付回调页面查询支付状态并跳转到订单详情页

## 注意事项

### 1. 需要两个 ngrok 进程

- **后端 ngrok**：映射 8000 端口
- **前端 ngrok**：映射 5173 端口

需要同时运行两个 ngrok 进程。

### 2. URL 会变化

每次重启 ngrok，URL 都会变化（免费版）：
- 需要更新 `settings.py` 中的配置
- 建议使用两个终端窗口分别运行，方便查看地址

### 3. ngrok 警告页面

免费版 ngrok 会显示警告页面：
- 用户需要点击 "Visit Site" 才能继续
- 这是 ngrok 免费版的限制
- 升级到付费版可以跳过警告

### 4. 前端 API 代理配置

如果前端使用 vite proxy，确保配置正确：

```javascript
// frontend/vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // 本地后端
        // 或者使用后端 ngrok 地址：
        // target: 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
```

## 快速启动脚本

### 方式一：分别启动（推荐）

**终端 1 - 后端 ngrok：**
```powershell
cd backend
.\start_ngrok.ps1
# 复制地址，更新 BACKEND_URL
```

**终端 2 - 前端 ngrok：**
```powershell
cd backend
.\start_ngrok_frontend.ps1
# 复制地址，更新 FRONTEND_URL
```

**终端 3 - Django 服务：**
```powershell
cd backend
python manage.py runserver
```

**终端 4 - 前端服务：**
```powershell
cd frontend
npm run dev
```

### 方式二：使用 ngrok 配置文件

创建 `ngrok.yml` 配置文件：

```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN
tunnels:
  backend:
    addr: 8000
    proto: http
  frontend:
    addr: 5173
    proto: http
```

然后启动：
```powershell
ngrok start --all
```

## 验证配置

### 1. 检查前端 ngrok 是否运行

访问 ngrok Web 界面：`http://127.0.0.1:4040`（前端 ngrok）

应该看到：
- 前端请求日志
- 前端 ngrok 地址

### 2. 检查后端 ngrok 是否运行

访问 ngrok Web 界面：`http://127.0.0.1:4040`（后端 ngrok）

应该看到：
- 后端请求日志
- 后端 ngrok 地址

### 3. 测试前端访问

在浏览器中访问前端 ngrok 地址：
```
https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app
```

应该能看到前端页面（可能需要点击 ngrok 警告页面的 "Visit Site"）

### 4. 测试支付流程

1. 创建订单
2. 点击支付
3. 完成支付
4. 检查是否能自动跳转回前端

## 故障排查

### 问题1：前端 ngrok 无法启动

**原因**：端口 5173 没有被占用

**解决**：
1. 确保前端服务正在运行：`npm run dev`
2. 检查端口是否被占用：`netstat -ano | findstr :5173`

### 问题2：前端 ngrok 地址无法访问

**原因**：ngrok 警告页面或网络问题

**解决**：
1. 点击 ngrok 警告页面的 "Visit Site"
2. 检查 ngrok 是否正常运行
3. 检查网络连接

### 问题3：前端无法调用后端 API

**原因**：前端 vite proxy 配置或 CORS 问题

**解决**：
1. 检查 `vite.config.js` 中的 proxy 配置
2. 检查后端 CORS 配置
3. 可以直接使用后端 ngrok 地址作为 API 地址

### 问题4：支付后无法跳转

**原因**：`FRONTEND_URL` 配置错误

**解决**：
1. 确认 `FRONTEND_URL` 是前端 ngrok 地址
2. 确认前端 ngrok 正在运行
3. 检查后端日志，查看重定向 URL

## 相关文件

- `backend/start_ngrok_frontend.ps1` - 前端 ngrok 启动脚本
- `backend/start_ngrok.ps1` - 后端 ngrok 启动脚本
- `backend/core/settings.py` - URL 配置
- `frontend/vite.config.js` - 前端代理配置


