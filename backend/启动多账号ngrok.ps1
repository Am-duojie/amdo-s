# 启动多账号 ngrok 脚本
# 分别使用不同的账号启动前后端隧道

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动多账号 Ngrok 隧道" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查配置文件是否存在
$backendConfig = "ngrok-backend.yml"
$frontendConfig = "ngrok-frontend.yml"

if (-not (Test-Path $backendConfig)) {
    Write-Host "错误: 后端配置文件 $backendConfig 不存在" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendConfig)) {
    Write-Host "错误: 前端配置文件 $frontendConfig 不存在" -ForegroundColor Red
    exit 1
}

Write-Host "✓ 找到后端配置文件: $backendConfig" -ForegroundColor Green
Write-Host "✓ 找到前端配置文件: $frontendConfig" -ForegroundColor Green
Write-Host ""

# 检查是否有 ngrok 进程在运行
$existingProcesses = Get-Process ngrok -ErrorAction SilentlyContinue
if ($existingProcesses) {
    Write-Host "警告: 发现 $($existingProcesses.Count) 个 ngrok 进程正在运行" -ForegroundColor Yellow
    $confirm = Read-Host "是否停止现有进程并重新启动？(y/n)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        $existingProcesses | Stop-Process -Force
        Write-Host "已停止现有进程" -ForegroundColor Green
        Write-Host "等待 10 秒让服务器释放资源..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    } else {
        Write-Host "已取消操作" -ForegroundColor Gray
        exit 0
    }
}

# 检查端口
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue

if (-not $port8000) {
    Write-Host "警告: 端口 8000 似乎没有被占用" -ForegroundColor Yellow
    Write-Host "请确保 Django 服务正在运行" -ForegroundColor Yellow
}

if (-not $port5173) {
    Write-Host "警告: 端口 5173 似乎没有被占用" -ForegroundColor Yellow
    Write-Host "请确保前端服务正在运行" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动说明" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "由于需要使用不同的账号，需要在两个终端分别启动：" -ForegroundColor Yellow
Write-Host ""
Write-Host "终端 1 - 后端（账号1）：" -ForegroundColor White
Write-Host "  cd D:\AAA\毕业设计\backend" -ForegroundColor Gray
Write-Host "  ngrok start --config ngrok-backend.yml backend" -ForegroundColor Gray
Write-Host ""
Write-Host "终端 2 - 前端（账号2）：" -ForegroundColor White
Write-Host "  cd D:\AAA\毕业设计\backend" -ForegroundColor Gray
Write-Host "  ngrok start --config ngrok-frontend.yml frontend" -ForegroundColor Gray
Write-Host ""
Write-Host "提示：" -ForegroundColor Cyan
Write-Host "- 两个账号会获得不同的 ngrok 地址" -ForegroundColor White
Write-Host "- 启动后复制显示的地址并更新 settings.py" -ForegroundColor White
Write-Host "- 配置前端使用后端地址（localStorage 或 .env）" -ForegroundColor White
Write-Host ""
Write-Host "是否现在启动后端隧道？(y/n)" -ForegroundColor Yellow
$startBackend = Read-Host

if ($startBackend -eq "y" -or $startBackend -eq "Y") {
    Write-Host ""
    Write-Host "正在启动后端 ngrok（账号1）..." -ForegroundColor Green
    Write-Host "提示：启动后，请在另一个终端启动前端 ngrok" -ForegroundColor Yellow
    Write-Host ""
    ngrok start --config $backendConfig backend
} else {
    Write-Host ""
    Write-Host "请手动在两个终端分别启动前后端 ngrok" -ForegroundColor Gray
    Write-Host ""
}



