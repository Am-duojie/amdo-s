# 同时启动前后端 ngrok 隧道脚本
# 注意：需要两个 ngrok 进程，建议分别启动

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动前后端 ngrok 内网穿透" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠ 注意：此脚本会尝试同时启动两个 ngrok 进程" -ForegroundColor Yellow
Write-Host "建议：分别使用 start_ngrok.ps1 和 start_ngrok_frontend.ps1" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "是否继续？(y/n)"
if ($choice -ne "y" -and $choice -ne "Y") {
    exit
}

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
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "推荐方式：分别启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "终端 1（后端）：" -ForegroundColor White
Write-Host "  cd backend" -ForegroundColor Gray
Write-Host "  .\start_ngrok.ps1" -ForegroundColor Gray
Write-Host "  复制显示的地址，更新 settings.py 中的 BACKEND_URL" -ForegroundColor Gray
Write-Host ""
Write-Host "终端 2（前端）：" -ForegroundColor White
Write-Host "  cd backend" -ForegroundColor Gray
Write-Host "  .\start_ngrok_frontend.ps1" -ForegroundColor Gray
Write-Host "  复制显示的地址，更新 settings.py 中的 FRONTEND_URL" -ForegroundColor Gray
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")








