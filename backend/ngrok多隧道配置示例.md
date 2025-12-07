# Ngrok 多隧道配置文件示例

## 基本格式

在 YAML 配置文件中，可以在 `tunnels` 部分定义多个隧道：

```yaml
version: 3
agent:
  authtoken: YOUR_AUTHTOKEN
tunnels:
  tunnel1:
    addr: 8000
    proto: http
  tunnel2:
    addr: 5173
    proto: http
  tunnel3:
    addr: 3000
    proto: http
```

## 当前项目的配置

### 单个配置文件（推荐）

**`ngrok.yml`** - 包含前后端两个隧道：

```yaml
version: 3
agent:
  authtoken: 36TUDwWpJTqmuqX6TwUidfFZ8aL_3hNcLMa3t4T4dJgbrtcDq
tunnels:
  backend:
    addr: 8000
    proto: http
  frontend:
    addr: 5173
    proto: http
```

### 启动所有隧道

```powershell
ngrok start --all --config ngrok.yml
```

### 启动指定的隧道

```powershell
# 只启动后端
ngrok start backend --config ngrok.yml

# 只启动前端
ngrok start frontend --config ngrok.yml

# 启动多个指定隧道
ngrok start backend frontend --config ngrok.yml
```

## 更多隧道配置示例

### 示例 1：多个 HTTP 隧道

```yaml
version: 3
agent:
  authtoken: YOUR_AUTHTOKEN
tunnels:
  api:
    addr: 8000
    proto: http
  web:
    addr: 5173
    proto: http
  admin:
    addr: 3000
    proto: http
```

### 示例 2：HTTP 和 TCP 隧道混合

```yaml
version: 3
agent:
  authtoken: YOUR_AUTHTOKEN
tunnels:
  web:
    addr: 8080
    proto: http
  ssh:
    addr: 22
    proto: tcp
  database:
    addr: 3306
    proto: tcp
```

### 示例 3：带标签的隧道

```yaml
version: 3
agent:
  authtoken: YOUR_AUTHTOKEN
tunnels:
  backend:
    addr: 8000
    proto: http
    metadata: "env=production"
  frontend:
    addr: 5173
    proto: http
    metadata: "env=production"
```

### 示例 4：HTTPS 上游

```yaml
version: 3
agent:
  authtoken: YOUR_AUTHTOKEN
tunnels:
  secure-api:
    addr: https://localhost:8443
    proto: http
```

### 示例 5：IPv6 地址

```yaml
version: 3
agent:
  authtoken: YOUR_AUTHTOKEN
tunnels:
  ipv6-web:
    addr: '[::1]:80'
    proto: http
```

## 配置选项说明

### 基本选项

- `version`: 配置文件版本（当前为 `3`）
- `agent.authtoken`: ngrok 身份验证令牌
- `tunnels`: 隧道定义字典

### 每个隧道的选项

- `addr`: 本地地址和端口（例如：`8000`、`localhost:8000`、`https://localhost:8443`）
- `proto`: 协议类型（`http`、`tcp`、`tls`）

### 高级选项（可选）

- `metadata`: 元数据标签
- `schemes`: 允许的方案（`http`、`https`）
- `hostname`: 自定义域名（需要付费版）
- `subdomain`: 子域名（需要付费版）

## 启动命令

### 启动所有隧道

```powershell
ngrok start --all --config ngrok.yml
```

### 启动指定隧道

```powershell
# 启动单个隧道
ngrok start backend --config ngrok.yml

# 启动多个隧道
ngrok start backend frontend --config ngrok.yml
```

### 验证配置

```powershell
ngrok config check --config ngrok.yml
```

## 当前项目使用

### 配置文件位置

- `backend/ngrok.yml` - 主配置文件（包含前后端隧道）

### 启动脚本

- `backend/启动ngrok所有隧道.ps1` - PowerShell 启动脚本

### 使用步骤

1. **编辑配置文件**（如果需要）：
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

2. **启动所有隧道**：
   ```powershell
   cd D:\AAA\毕业设计\backend
   ngrok start --all --config ngrok.yml
   ```

3. **查看输出**，复制显示的地址：
   ```
   Forwarding  https://xxxx-backend.ngrok-free.dev -> http://localhost:8000
   Forwarding  https://yyyy-frontend.ngrok-free.dev -> http://localhost:5173
   ```

4. **更新配置**：
   - `backend/core/settings.py` 中的 `FRONTEND_URL` 和 `BACKEND_URL`
   - 前端 `localStorage` 中的 `BACKEND_NGROK_URL`

## 注意事项

1. **隧道名称**：每个隧道必须有唯一的名称
2. **地址冲突**：确保本地端口不冲突
3. **免费版限制**：免费版可能无法为多个隧道分配不同的地址
4. **地址变化**：每次重启 ngrok，地址可能变化

## 故障排除

### 如果地址相同

如果使用 `--all` 后地址仍然相同：

1. 使用分别的配置文件分别启动
2. 或者只使用后端 ngrok

### 如果配置错误

运行验证命令：
```powershell
ngrok config check --config ngrok.yml
```

### 如果无法启动

检查：
- authtoken 是否正确
- 本地端口是否被占用
- 配置文件格式是否正确


