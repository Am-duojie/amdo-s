# 启动所有 ngrok 隧道脚本（前后端）
# 使用方法：在 backend 目录下运行 .\启动ngrok所有隧道.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动所有 Ngrok 隧道（前后端）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 ngrok 是否已安装
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Host "错误: 未找到 ngrok 命令" -ForegroundColor Red
    Write-Host "请先安装 ngrok: https://ngrok.com/download" -ForegroundColor Yellow
    exit 1
}

# 检查配置文件是否存在
$configFile = "ngrok.yml"
if (-not (Test-Path $configFile)) {
    Write-Host "错误: 配置文件 $configFile 不存在" -ForegroundColor Red
    Write-Host "请先创建配置文件" -ForegroundColor Yellow
    exit 1
}

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

# 检查端口是否被占用
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue

if (-not $port8000) {
    Write-Host "警告: 端口 8000 似乎没有被占用" -ForegroundColor Yellow
    Write-Host "请确保 Django 服务正在运行 (python manage.py runserver)" -ForegroundColor Yellow
}

if (-not $port5173) {
    Write-Host "警告: 端口 5173 似乎没有被占用" -ForegroundColor Yellow
    Write-Host "请确保前端服务正在运行 (npm run dev)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "正在启动所有 ngrok 隧道..." -ForegroundColor Green
Write-Host ""
Write-Host "提示：" -ForegroundColor Cyan
Write-Host "1. 启动后，会显示两个不同的 Forwarding 地址" -ForegroundColor White
Write-Host "2. 后端地址：https://xxxx-backend.ngrok-free.dev -> http://localhost:8000" -ForegroundColor Gray
Write-Host "3. 前端地址：https://yyyy-frontend.ngrok-free.dev -> http://localhost:5173" -ForegroundColor Gray
Write-Host "4. 请复制这两个地址并更新 settings.py 和前端配置" -ForegroundColor White
Write-Host "5. 按 Ctrl+C 停止所有隧道" -ForegroundColor White
Write-Host ""

# 使用配置文件启动所有隧道
ngrok start --all --config $configFile



