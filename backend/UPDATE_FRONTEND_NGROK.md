# 更新前端 ngrok 配置指南

## 您已经手动启动了前端 ngrok 隧道

现在需要更新配置以使用前端 ngrok 地址。

## 步骤 1：获取前端 ngrok 地址

### 方法一：查看 ngrok 启动信息

在启动前端 ngrok 的终端窗口中，您应该看到类似以下的信息：

```
Forwarding  https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app -> http://localhost:5173
```

**复制这个 HTTPS 地址**：`https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app`

### 方法二：访问 ngrok Web 界面

1. 打开浏览器访问：`http://127.0.0.1:4040`（前端 ngrok 的 Web 界面）
2. 如果端口冲突，ngrok 可能使用了其他端口（如 4041）
3. 在 Web 界面中查看 "Forwarding" 信息，找到映射到 5173 端口的地址

### 方法三：查看 ngrok 日志

在启动前端 ngrok 的终端窗口中，查找包含 `5173` 的行，应该能看到公网地址。

## 步骤 2：更新 settings.py 配置

打开 `backend/core/settings.py`，找到以下配置：

```python
# 前端地址（本地开发时使用 localhost，如果前端也有 ngrok 隧道则使用 ngrok 地址）
FRONTEND_URL = 'http://localhost:5173'  # 前端地址（本地）
```

**修改为**：

```python
# 前端地址（使用前端 ngrok 公网地址）
FRONTEND_URL = 'https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app'  # 替换为您的前端 ngrok 地址
```

**完整配置示例**：

```python
# 前后端URL配置（用于动态构建回调地址）
# 注意：
# 1. 如果只启动了后端 ngrok 隧道（8000端口），前端应该使用 localhost
# 2. 如果前后端都启动了 ngrok 隧道，则分别配置对应的地址
# 3. 当前代码会自动检测 ngrok，使用后端重定向页面处理支付返回

# 前端地址（使用前端 ngrok 公网地址）
FRONTEND_URL = 'https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app'  # 前端 ngrok 地址

# 后端地址（使用 ngrok 内网穿透地址，从 ngrok 启动信息中获取）
BACKEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'  # ngrok 公网地址（后端）
```

## 步骤 3：重启 Django 服务（如果需要）

如果 Django 服务正在运行，建议重启以加载新配置：

1. 停止当前 Django 服务（在运行 Django 的终端按 `Ctrl+C`）
2. 重新启动：
   ```powershell
   python manage.py runserver
   ```

## 步骤 4：验证配置

### 1. 检查前端 ngrok 是否可访问

在浏览器中访问前端 ngrok 地址：
```
https://yyyy-yyyy-yyyy-yyyy.ngrok-free.app
```

**注意**：可能会看到 ngrok 警告页面，点击 "Visit Site" 继续。

应该能看到前端页面正常加载。

### 2. 检查配置是否正确

确认 `settings.py` 中的配置：

```python
FRONTEND_URL = 'https://您的-前端-ngrok-地址.ngrok-free.dev'
BACKEND_URL = 'https://您的-后端-ngrok-地址.ngrok-free.dev'
```

### 3. 测试支付流程

1. 访问前端 ngrok 地址
2. 创建订单
3. 点击支付
4. 完成支付
5. 检查是否能自动跳转回前端

## 当前运行的服务

确保以下服务都在运行：

- ✅ **后端 Django**：`python manage.py runserver`（端口 8000）
- ✅ **后端 ngrok**：`ngrok http 8000`（映射后端）
- ✅ **前端服务**：`npm run dev`（端口 5173）
- ✅ **前端 ngrok**：`ngrok http 5173`（映射前端）

## 配置后的工作流程

1. **用户访问**：`https://前端-ngrok-地址.ngrok-free.app`
2. **创建支付**：前端调用后端 API
3. **支付完成**：支付宝跳转到前端支付回调页面（`https://前端-ngrok-地址.ngrok-free.app/payment/return`）
4. **查询状态**：前端支付回调页面查询支付状态
5. **跳转订单**：自动跳转到订单详情页

## 如果遇到问题

### 问题1：无法访问前端 ngrok 地址

**解决**：
1. 确认前端 ngrok 正在运行
2. 确认前端服务（npm run dev）正在运行
3. 点击 ngrok 警告页面的 "Visit Site"

### 问题2：支付后无法跳转

**解决**：
1. 检查 `FRONTEND_URL` 配置是否正确
2. 检查前端 ngrok 是否正常运行
3. 查看浏览器控制台和网络请求

### 问题3：前端无法调用后端 API

**解决**：
1. 检查 `vite.config.js` 中的 proxy 配置
2. 或者直接使用后端 ngrok 地址作为 API 地址

## 快速检查清单

- [ ] 前端 ngrok 正在运行（端口 5173）
- [ ] 后端 ngrok 正在运行（端口 8000）
- [ ] 前端服务正在运行（npm run dev）
- [ ] 后端服务正在运行（python manage.py runserver）
- [ ] `FRONTEND_URL` 已更新为前端 ngrok 地址
- [ ] `BACKEND_URL` 已更新为后端 ngrok 地址
- [ ] 可以访问前端 ngrok 地址
- [ ] 支付流程可以正常完成

## 下一步

配置完成后，请：
1. 测试创建订单
2. 测试支付流程
3. 确认支付完成后能自动跳转回前端

如果还有问题，请告诉我具体的错误信息。



