# 前端 Ngrok 地址配置说明

## 当前配置

- **后端地址**：`https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev`
- **前端地址**：`https://georgianna-presanitary-clair.ngrok-free.dev`

## 配置方法

### 方法 1：使用环境变量（推荐，持久化）

在 `frontend` 目录下创建 `.env` 文件：

```env
VITE_BACKEND_NGROK_URL=https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev
```

然后**重启前端服务**（`npm run dev`）。

### 方法 2：使用浏览器 localStorage（临时）

1. 访问前端 ngrok 地址：`https://georgianna-presanitary-clair.ngrok-free.dev`
2. 打开浏览器控制台（F12）
3. 运行以下代码：

```javascript
localStorage.setItem('BACKEND_NGROK_URL', 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev')
location.reload()
```

## 验证配置

配置后，在浏览器控制台应该能看到：

```
API基础地址: https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev/api
```

## 如果仍然无法连接

1. **检查后端 ngrok 是否运行**：访问 `https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev/api/`
2. **检查 CORS 配置**：确保后端 `settings.py` 中 `CORS_ALLOW_ALL_ORIGINS = True`
3. **查看浏览器控制台**：检查网络请求和错误信息








