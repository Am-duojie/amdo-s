# 快速修复 Ngrok 冲突问题

## 问题

前后端 ngrok 使用了相同的地址 `https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev`，导致错误 NGROK_6030。

## 解决方案（3 步）

### 步骤 1：停止所有 ngrok 进程

在所有运行 ngrok 的终端窗口按 `Ctrl+C` 停止。

### 步骤 2：分别启动前后端 ngrok（使用配置文件）

**终端 1 - 启动后端 ngrok**：
```powershell
cd backend
.\start_ngrok_backend.ps1
```

**终端 2 - 启动前端 ngrok**：
```powershell
cd backend
.\start_ngrok_frontend.ps1
```

脚本会自动创建配置文件，确保前后端使用不同的 ngrok 地址。

### 步骤 3：更新 settings.py

启动后，您会看到两个**不同的** ngrok 地址：

- **后端**：`https://xxxx-backend.ngrok-free.dev` → `http://localhost:8000`
- **前端**：`https://yyyy-frontend.ngrok-free.dev` → `http://localhost:5173`

更新 `backend/core/settings.py`：

```python
# 前端地址（使用前端 ngrok 公网地址）
FRONTEND_URL = 'https://yyyy-frontend.ngrok-free.dev'  # 替换为您的前端 ngrok 地址

# 后端地址（使用后端 ngrok 公网地址）
BACKEND_URL = 'https://xxxx-backend.ngrok-free.dev'  # 替换为您的后端 ngrok 地址
```

## 验证

1. 访问后端地址：`https://xxxx-backend.ngrok-free.dev/api/`（应该看到 API 根目录）
2. 访问前端地址：`https://yyyy-frontend.ngrok-free.dev`（应该看到前端页面）
3. 两个地址应该**不同**，且都能正常访问

## 如果仍然冲突

如果两个 ngrok 仍然使用相同地址，请：

1. **完全退出所有 ngrok 进程**：
   ```powershell
   Get-Process ngrok | Stop-Process -Force
   ```

2. **等待 30 秒**，让 ngrok 服务器释放资源

3. **重新启动**（先启动后端，再启动前端）

4. **如果还是相同地址**，可能需要：
   - 使用不同的 ngrok 账户
   - 或者等待一段时间后再试
   - 或者使用付费版 ngrok（支持多个隧道）

## 详细说明

查看 `backend/NGROK_多隧道解决方案.md` 获取更多信息。







