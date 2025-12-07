# 配置前端使用 Ngrok 后端地址

## 问题

当通过 ngrok 访问前端时，前端无法连接到后端，因为 API 请求仍然指向 `localhost:8000`，而前端在公网上无法访问本地地址。

## 解决方案

### 方法 1：通过 localStorage 配置（推荐）

在浏览器控制台运行：

```javascript
// 设置后端的 ngrok 地址（替换为您的实际地址）
localStorage.setItem('BACKEND_NGROK_URL', 'https://xxxx-backend.ngrok-free.dev')

// 刷新页面
location.reload()
```

### 方法 2：通过环境变量配置

创建 `.env` 文件（在 `frontend` 目录下）：

```env
VITE_BACKEND_NGROK_URL=https://xxxx-backend.ngrok-free.dev
```

然后重启前端服务。

### 方法 3：修改代码自动检测

已修改 `frontend/src/utils/api.js`，现在会：
1. 自动检测是否通过 ngrok 访问
2. 如果通过 ngrok 访问，尝试从 localStorage 或环境变量获取后端地址
3. 如果未配置，会显示警告

## 快速配置步骤

### 1. 启动后端 ngrok

```powershell
cd D:\AAA\毕业设计\backend
ngrok start --all --config ngrok.yml
```

复制后端地址，例如：`https://xxxx-backend.ngrok-free.dev`

### 2. 启动前端 ngrok（如果使用）

```powershell
# 如果使用单个配置文件
ngrok start --all --config ngrok.yml
```

复制前端地址，例如：`https://yyyy-frontend.ngrok-free.dev`

### 3. 配置前端使用后端地址

**方法 A - 浏览器控制台**（最简单）：
1. 访问前端 ngrok 地址
2. 打开浏览器控制台（F12）
3. 运行：
   ```javascript
   localStorage.setItem('BACKEND_NGROK_URL', 'https://xxxx-backend.ngrok-free.dev')
   location.reload()
   ```

**方法 B - 环境变量**：
1. 在 `frontend` 目录创建 `.env` 文件
2. 添加：
   ```env
   VITE_BACKEND_NGROK_URL=https://xxxx-backend.ngrok-free.dev
   ```
3. 重启前端服务

### 4. 验证

访问前端 ngrok 地址，应该能正常加载数据。

## 代码说明

已修改的 `api.js` 会：
- 检测当前是否通过 ngrok 访问
- 如果是，尝试使用后端的 ngrok 地址
- 如果未配置，显示警告并尝试使用相对路径（可能不工作）

## 注意事项

1. **CORS 配置**：确保后端 `settings.py` 中 `CORS_ALLOW_ALL_ORIGINS = True`
2. **地址更新**：每次重启 ngrok，地址可能变化，需要重新配置
3. **HTTPS**：ngrok 使用 HTTPS，确保后端也支持 HTTPS（通常自动支持）

## 自动化方案（可选）

可以创建一个配置页面，让用户输入后端 ngrok 地址并保存到 localStorage。



