# 快速启动 ngrok 脚本
# 用于启动 ngrok 内网穿透服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动 ngrok 内网穿透" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 ngrok 是否已安装
try {
    $ngrokVersion = ngrok version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "ngrok not found"
    }
} catch {
    Write-Host "✗ ngrok 未安装或未添加到 PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先运行 setup_ngrok.ps1 进行配置" -ForegroundColor Yellow
    Write-Host "或访问 https://ngrok.com/download 下载安装" -ForegroundColor Yellow
    exit
}

# 检查端口是否被占用
$port = 8000
$portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if (-not $portInUse) {
    Write-Host "⚠ 警告: 端口 $port 似乎没有被占用" -ForegroundColor Yellow
    Write-Host "请确保 Django 服务正在运行（python manage.py runserver）" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "是否继续启动 ngrok？(y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit
    }
}

Write-Host "正在启动 ngrok（映射本地 $port 端口）..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "重要提示" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. ngrok 启动后会显示公网地址（类似 https://xxxx.ngrok-free.app）" -ForegroundColor White
Write-Host "2. 请复制该地址并更新 settings.py 中的 BACKEND_URL" -ForegroundColor White
Write-Host "3. 按 Ctrl+C 停止 ngrok" -ForegroundColor White
Write-Host ""
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "启动中..." -ForegroundColor Green
Write-Host ""

# 启动 ngrok
ngrok http $port










