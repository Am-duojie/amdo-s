# URL 配置检查说明

## 当前配置问题

### 当前配置（可能有问题）

```python
FRONTEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'  # 前端地址
BACKEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'  # ngrok 公网地址
```

### 问题分析

1. **ngrok 隧道配置**：
   - 从 `start_ngrok.ps1` 看，只启动了 **8000 端口**的 ngrok 隧道（后端）
   - 前端运行在 **5173 端口**，但**没有** ngrok 隧道

2. **配置错误**：
   - `FRONTEND_URL` 设置为 ngrok 地址，但前端没有 ngrok 隧道
   - 这会导致前端无法通过 ngrok 地址访问

3. **正确的配置应该是**：
   - `BACKEND_URL` = ngrok 地址（指向 8000 端口）✅
   - `FRONTEND_URL` = `http://localhost:5173`（本地前端地址）✅

## 配置方案

### 方案一：只使用后端 ngrok（推荐用于测试）

**适用场景**：前端在本地访问，后端通过 ngrok 暴露给支付宝

```python
# 后端通过 ngrok 暴露（用于支付宝回调）
BACKEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'

# 前端在本地运行（用户直接访问）
FRONTEND_URL = 'http://localhost:5173'
```

**优点**：
- 只需要一个 ngrok 隧道
- 前端访问速度快
- 配置简单

**缺点**：
- 支付宝的 `return_url` 会跳转到 `localhost`，可能无法访问
- 需要用户手动处理支付返回

### 方案二：前后端都使用 ngrok

**适用场景**：需要支付宝能跳转回前端页面

**步骤**：
1. 启动两个 ngrok 隧道：
   ```powershell
   # 终端 1：后端隧道
   ngrok http 8000
   # 复制地址：https://xxxx-backend.ngrok-free.dev
   
   # 终端 2：前端隧道
   ngrok http 5173
   # 复制地址：https://xxxx-frontend.ngrok-free.dev
   ```

2. 配置：
   ```python
   BACKEND_URL = 'https://xxxx-backend.ngrok-free.dev'
   FRONTEND_URL = 'https://xxxx-frontend.ngrok-free.dev'
   ```

**优点**：
- 支付宝可以正确跳转回前端
- 完全公网可访问

**缺点**：
- 需要两个 ngrok 隧道
- 免费版 URL 会变化，需要频繁更新

### 方案三：使用后端重定向（当前实现）

**当前代码逻辑**：
- 检测到使用 ngrok 时，`return_url` 指向后端重定向页面
- 后端重定向页面自动跳转到前端

```python
# 如果使用 ngrok
if 'ngrok' in backend_url:
    return_url = f'{backend_url}/api/payment/redirect?order_id={order.id}&order_type=normal'
```

**优点**：
- 只需要一个 ngrok 隧道
- 支付宝可以跳转到后端
- 后端自动重定向到前端

**缺点**：
- 需要用户点击 ngrok 警告页面的 "Visit Site"
- 多一次跳转

## 推荐配置（根据当前架构）

基于当前代码实现，推荐使用**方案一 + 后端重定向**：

```python
# 后端通过 ngrok 暴露（用于支付宝回调和重定向）
BACKEND_URL = 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev'

# 前端在本地运行
FRONTEND_URL = 'http://localhost:5173'
```

**工作流程**：
1. 用户在前端（localhost:5173）创建订单
2. 跳转到支付宝支付
3. 支付完成后，支付宝跳转到后端重定向页面（ngrok 地址）
4. 后端重定向页面自动跳转回前端（localhost:5173）
5. 前端支付回调页面查询支付状态

## 检查清单

- [ ] 确认 ngrok 只启动了 8000 端口的隧道
- [ ] 确认前端运行在 localhost:5173
- [ ] 更新 `FRONTEND_URL` 为 `http://localhost:5173`
- [ ] 保持 `BACKEND_URL` 为 ngrok 地址
- [ ] 测试支付流程是否正常


