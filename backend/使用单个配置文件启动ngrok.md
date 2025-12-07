# 使用单个配置文件启动多个 Ngrok 隧道

## 根据 ngrok 官方文档

ngrok 支持在一个配置文件中定义多个端点，然后使用一个命令启动所有端点。这样可以避免冲突问题。

## 新的配置文件

已创建 `ngrok.yml`，包含前后端两个隧道：

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

## 启动方法

### 方法 1：启动所有隧道（推荐）

```powershell
cd D:\AAA\毕业设计\backend
ngrok start --all --config ngrok.yml
```

这会同时启动 `backend` 和 `frontend` 两个隧道。

### 方法 2：启动指定的隧道

```powershell
cd D:\AAA\毕业设计\backend
ngrok start backend frontend --config ngrok.yml
```

### 方法 3：只启动一个隧道

```powershell
# 只启动后端
ngrok start backend --config ngrok.yml

# 只启动前端
ngrok start frontend --config ngrok.yml
```

## 优势

1. **避免冲突**：使用单个配置文件，ngrok 会正确管理多个隧道
2. **统一管理**：所有隧道配置在一个文件中
3. **简化启动**：一个命令启动所有隧道

## 查看隧道状态

启动后，您会看到类似以下输出：

```
Forwarding  https://xxxx-backend.ngrok-free.dev -> http://localhost:8000
Forwarding  https://yyyy-frontend.ngrok-free.dev -> http://localhost:5173
```

## 访问 Web 界面

- 后端隧道：`http://127.0.0.1:4040`
- 前端隧道：`http://127.0.0.1:4041`（如果端口冲突会自动使用下一个端口）

## 更新 settings.py

启动后，复制显示的地址并更新 `settings.py`：

```python
FRONTEND_URL = 'https://yyyy-frontend.ngrok-free.dev'  # 前端地址
BACKEND_URL = 'https://xxxx-backend.ngrok-free.dev'    # 后端地址
```

## 停止所有隧道

在运行 ngrok 的终端按 `Ctrl+C`，会停止所有隧道。

## 如果仍然遇到冲突

1. **完全停止所有 ngrok 进程**：
   ```powershell
   Get-Process ngrok | Stop-Process -Force
   ```

2. **等待 5 分钟**：
   ```powershell
   Start-Sleep -Seconds 300
   ```

3. **使用新配置文件重新启动**：
   ```powershell
   ngrok start --all --config ngrok.yml
   ```

## 验证

启动后，检查：
- [ ] 两个隧道都显示不同的地址
- [ ] 两个地址都能正常访问
- [ ] Web 界面显示两个隧道都在运行




