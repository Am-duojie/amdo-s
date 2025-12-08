# 停止所有 ngrok 进程脚本
# 使用方法：在 backend 目录下运行 .\stop_ngrok.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "停止所有 Ngrok 进程" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 查找所有 ngrok 进程
$processes = Get-Process ngrok -ErrorAction SilentlyContinue

if ($processes) {
    Write-Host "找到 $($processes.Count) 个 ngrok 进程：" -ForegroundColor Yellow
    $processes | Format-Table Id, ProcessName, StartTime -AutoSize
    
    Write-Host ""
    $confirm = Read-Host "是否停止所有 ngrok 进程？(y/n)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        $processes | Stop-Process -Force
        Write-Host ""
        Write-Host "✓ 已停止所有 ngrok 进程" -ForegroundColor Green
        Write-Host ""
        Write-Host "提示：等待 30 秒后再重新启动 ngrok，让服务器释放资源" -ForegroundColor Yellow
    } else {
        Write-Host "已取消操作" -ForegroundColor Gray
    }
} else {
    Write-Host "✓ 没有找到运行中的 ngrok 进程" -ForegroundColor Green
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")







