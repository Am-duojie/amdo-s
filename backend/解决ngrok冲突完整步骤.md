# 解决 Ngrok 端点冲突完整步骤

## 错误信息
```
ERROR: failed to start tunnel: The endpoint 'https://hypochondriacally-nondiscretionary-kylie.ngrok-free.dev' is already online.
ERROR: ERR_NGROK_334
```

## 完整解决步骤

### 步骤 1：停止所有 ngrok 进程

**方法 A - 使用脚本（推荐）**：
```powershell
cd D:\AAA\毕业设计\backend
.\stop_ngrok.ps1
```

**方法 B - 手动停止**：
```powershell
Get-Process ngrok | Stop-Process -Force
```

**方法 C - 手动停止（逐个）**：
- 找到所有运行 ngrok 的终端窗口
- 在每个窗口按 `Ctrl+C` 停止

### 步骤 2：等待 30-60 秒

**非常重要**：必须等待足够的时间让 ngrok 服务器释放资源。

```powershell
# 等待 30 秒
Start-Sleep -Seconds 30

# 或者使用脚本自动等待
.\重启ngrok.ps1
```

### 步骤 3：验证进程已停止

```powershell
Get-Process ngrok -ErrorAction SilentlyContinue
```

如果没有输出，说明所有进程已停止。

### 步骤 4：重新启动（使用不同的配置）

**关键**：确保使用配置文件方式启动，这样前后端会使用不同的地址。

**终端 1 - 后端 ngrok**：
```powershell
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-backend.yml backend
```

**终端 2 - 前端 ngrok**（新开终端）：
```powershell
cd D:\AAA\毕业设计\backend
ngrok start --config ngrok-frontend.yml frontend
```

### 步骤 5：验证地址不同

启动后，检查两个 ngrok 显示的地址是否**不同**：

- 后端：`https://xxxx-backend.ngrok-free.dev` → `http://localhost:8000`
- 前端：`https://yyyy-frontend.ngrok-free.dev` → `http://localhost:5173`

**如果地址相同，说明配置有问题，需要重新检查。**

## 如果仍然冲突

### 方案 1：等待更长时间

有时需要等待 5-10 分钟让 ngrok 服务器完全释放资源：

```powershell
Start-Sleep -Seconds 300  # 等待 5 分钟
```

### 方案 2：检查是否有其他 ngrok 进程

```powershell
# 检查所有进程
Get-Process | Where-Object {$_.ProcessName -like "*ngrok*"}

# 检查网络连接
Get-NetTCPConnection | Where-Object {$_.LocalPort -in @(4040, 4041, 8000, 5173)}
```

### 方案 3：重启计算机

如果以上方法都不行，可能需要重启计算机来完全清理所有进程和连接。

### 方案 4：使用不同的 ngrok 账户

如果有另一个 ngrok 账户，可以使用不同的 authtoken：

1. 修改 `ngrok-backend.yml` 和 `ngrok-frontend.yml` 中的 `authtoken`
2. 重新启动

## 快速修复命令

```powershell
# 一键停止并等待
cd D:\AAA\毕业设计\backend
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 30
Write-Host "可以重新启动了" -ForegroundColor Green
```

## 预防措施

1. **使用配置文件**：始终使用 `--config` 参数指定配置文件
2. **分别启动**：前后端在不同的终端窗口启动
3. **正确关闭**：使用 `Ctrl+C` 关闭，不要直接关闭终端
4. **检查进程**：启动前先检查是否有 ngrok 进程在运行

## 验证清单

- [ ] 所有 ngrok 进程已停止
- [ ] 已等待至少 30 秒
- [ ] 使用配置文件方式启动
- [ ] 前后端地址不同
- [ ] 两个 ngrok 都能正常访问

## 如果问题持续

1. 查看 ngrok 日志：访问 `http://127.0.0.1:4040` 或 `http://127.0.0.1:4041`
2. 检查 ngrok 状态：`ngrok config check`
3. 联系 ngrok 支持：https://ngrok.com/docs/errors/err_ngrok_334




