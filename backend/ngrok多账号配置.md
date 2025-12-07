# Ngrok 多账号配置指南

## 问题

本地 ngrok 可以连接两个不同的账号做两条隧道吗？

**答案：可以！** ngrok 支持为不同的隧道使用不同的 authtoken（不同的账号）。

## 配置方法

### 方法 1：在单个配置文件中使用不同的 authtoken（推荐）

在 `ngrok.yml` 中，可以为每个隧道指定不同的 authtoken：

```yaml
version: 3
agent:
  authtoken: DEFAULT_AUTHTOKEN  # 默认 authtoken（如果隧道未指定则使用此）
tunnels:
  backend:
    addr: 8000
    proto: http
    authtoken: BACKEND_ACCOUNT_AUTHTOKEN  # 后端账号的 authtoken
  frontend:
    addr: 5173
    proto: http
    authtoken: FRONTEND_ACCOUNT_AUTHTOKEN  # 前端账号的 authtoken
```

### 方法 2：使用不同的配置文件（更清晰）

为每个账号创建独立的配置文件：

**ngrok-backend.yml**（使用账号1）:
```yaml
version: 3
agent:
  authtoken: ACCOUNT1_AUTHTOKEN
tunnels:
  backend:
    addr: 8000
    proto: http
```

**ngrok-frontend.yml**（使用账号2）:
```yaml
version: 3
agent:
  authtoken: ACCOUNT2_AUTHTOKEN
tunnels:
  frontend:
    addr: 5173
    proto: http
```

然后分别启动：

```powershell
# 终端 1 - 使用账号1
ngrok start --config ngrok-backend.yml backend

# 终端 2 - 使用账号2
ngrok start --config ngrok-frontend.yml frontend
```

## 优势

使用不同账号的优势：

1. **确保不同的地址**：不同账号会获得不同的 ngrok 地址
2. **隔离资源**：每个账号有独立的配额和限制
3. **安全性**：即使一个账号泄露，另一个账号仍然安全
4. **灵活性**：可以为不同环境使用不同的账号

## 配置示例

### 示例 1：单个配置文件，不同 authtoken

```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq  # 默认账号
tunnels:
  backend:
    addr: 8000
    proto: http
    authtoken: BACKEND_ACCOUNT_AUTHTOKEN  # 后端账号
  frontend:
    addr: 5173
    proto: http
    authtoken: FRONTEND_ACCOUNT_AUTHTOKEN  # 前端账号
```

### 示例 2：分别的配置文件

**ngrok-backend.yml**:
```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq  # 账号1
tunnels:
  backend:
    addr: 8000
    proto: http
```

**ngrok-frontend.yml**:
```yaml
version: 3
agent:
  authtoken: ANOTHER_ACCOUNT_AUTHTOKEN  # 账号2
tunnels:
  frontend:
    addr: 5173
    proto: http
```

## 获取第二个账号的 authtoken

1. **注册新账号**（如果需要）：
   - 访问 https://dashboard.ngrok.com/signup
   - 使用不同的邮箱注册

2. **获取 authtoken**：
   - 登录新账号
   - 访问 https://dashboard.ngrok.com/get-started/your-authtoken
   - 复制 authtoken

3. **配置到文件中**：
   - 更新配置文件中的 `authtoken`

## 启动方法

### 使用单个配置文件（方法1）

```powershell
cd D:\AAA\毕业设计\backend
ngrok start --all --config ngrok.yml
```

### 使用分别的配置文件（方法2）

```powershell
# 终端 1 - 账号1
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-backend.yml backend

# 终端 2 - 账号2
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-frontend.yml frontend
```

## 验证

启动后，检查输出：

```
# 账号1的隧道
Forwarding  https://xxxx-backend.ngrok-free.dev -> http://localhost:8000

# 账号2的隧道
Forwarding  https://yyyy-frontend.ngrok-free.dev -> http://localhost:5173
```

**两个地址应该不同**（因为使用了不同的账号）。

## 注意事项

1. **账号限制**：每个账号都有独立的免费配额
2. **地址稳定性**：不同账号的地址分配是独立的
3. **管理复杂度**：需要管理多个账号和 authtoken
4. **安全性**：保护好每个账号的 authtoken

## 推荐方案

### 如果只有一个账号

使用单个配置文件，让 ngrok 自动分配地址：
```yaml
version: 3
agent:
  authtoken: YOUR_AUTHTOKEN
tunnels:
  backend:
    addr: 8000
    proto: http
  frontend:
    addr: 5173
    proto: http
```

### 如果有两个账号（推荐）

使用不同的配置文件，分别启动：
- 更清晰
- 更容易管理
- 确保不同的地址

## 当前项目配置

如果您有两个账号，可以这样配置：

1. **更新 `ngrok-backend.yml`**（使用账号1）：
```yaml
version: 3
agent:
  authtoken: ACCOUNT1_AUTHTOKEN
tunnels:
  backend:
    addr: 8000
    proto: http
```

2. **更新 `ngrok-frontend.yml`**（使用账号2）：
```yaml
version: 3
agent:
  authtoken: ACCOUNT2_AUTHTOKEN
tunnels:
  frontend:
    addr: 5173
    proto: http
```

3. **分别启动**：
```powershell
# 终端 1
ngrok start --config ngrok-backend.yml backend

# 终端 2
ngrok start --config ngrok-frontend.yml frontend
```

这样就能确保前后端使用不同的账号，获得不同的地址。


