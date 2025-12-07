# 启动后端 ngrok 隧道（端口 8000）
# 使用方法：在 backend 目录下运行 .\start_ngrok_backend.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动后端 Ngrok 隧道（端口 8000）" -ForegroundColor Cyan
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
$configFile = "ngrok-backend.yml"
if (-not (Test-Path $configFile)) {
    Write-Host "配置文件不存在，正在创建..." -ForegroundColor Yellow
    
    # 获取 authtoken
    Write-Host ""
    Write-Host "请输入您的 ngrok authtoken：" -ForegroundColor Yellow
    Write-Host "（如果还没有，请访问: https://dashboard.ngrok.com/get-started/your-authtoken）" -ForegroundColor Gray
    $authtoken = Read-Host "Authtoken"
    
    if ([string]::IsNullOrWhiteSpace($authtoken)) {
        Write-Host "错误: authtoken 不能为空" -ForegroundColor Red
        exit 1
    }
    
    # 创建配置文件
    $configContent = @"
version: "2"
authtoken: $authtoken
tunnels:
  backend:
    addr: 8000
    proto: http
"@
    
    $configContent | Out-File -FilePath $configFile -Encoding UTF8
    Write-Host "配置文件已创建: $configFile" -ForegroundColor Green
    Write-Host ""
}

# 检查端口 8000 是否被占用
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $port8000) {
    Write-Host "警告: 端口 8000 似乎没有被占用" -ForegroundColor Yellow
    Write-Host "请确保 Django 服务正在运行 (python manage.py runserver)" -ForegroundColor Yellow
    Write-Host ""
}

# 启动 ngrok
Write-Host "正在启动后端 ngrok 隧道..." -ForegroundColor Green
Write-Host ""
Write-Host "提示：" -ForegroundColor Cyan
Write-Host "1. 启动后，请复制显示的 Forwarding 地址" -ForegroundColor White
Write-Host "2. 更新 settings.py 中的 BACKEND_URL" -ForegroundColor White
Write-Host "3. 按 Ctrl+C 停止 ngrok" -ForegroundColor White
Write-Host ""

# 使用配置文件启动，指定亚太区域（适合中国用户）
ngrok start --config $configFile --region ap backend

