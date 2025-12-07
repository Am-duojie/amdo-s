# 重启 ngrok 脚本
# 停止所有 ngrok 进程，等待后重新启动

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "重启 Ngrok 隧道" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 停止所有 ngrok 进程
Write-Host "步骤 1: 停止所有 ngrok 进程..." -ForegroundColor Yellow
$processes = Get-Process ngrok -ErrorAction SilentlyContinue

if ($processes) {
    $processes | Stop-Process -Force
    Write-Host "✓ 已停止 $($processes.Count) 个 ngrok 进程" -ForegroundColor Green
} else {
    Write-Host "✓ 没有运行中的 ngrok 进程" -ForegroundColor Green
}

Write-Host ""
Write-Host "步骤 2: 等待 30 秒让 ngrok 服务器释放资源..." -ForegroundColor Yellow
Write-Host "（这是必要的，否则可能仍然会冲突）" -ForegroundColor Gray
Write-Host ""

$seconds = 30
for ($i = $seconds; $i -gt 0; $i--) {
    Write-Host "`r等待 $i 秒... " -NoNewline -ForegroundColor Gray
    Start-Sleep -Seconds 1
}
Write-Host "`r等待完成！                          " -ForegroundColor Green
Write-Host ""

Write-Host "步骤 3: 验证所有进程已停止..." -ForegroundColor Yellow
$remaining = Get-Process ngrok -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "警告: 仍有 ngrok 进程在运行" -ForegroundColor Red
    $remaining | Format-Table Id, ProcessName -AutoSize
    Write-Host "请手动停止这些进程" -ForegroundColor Yellow
} else {
    Write-Host "✓ 所有 ngrok 进程已停止" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "现在可以重新启动 ngrok 了" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "在终端 1 运行（后端）：" -ForegroundColor White
Write-Host "  cd D:\AAA\毕业设计\backend" -ForegroundColor Gray
Write-Host "  ngrok start --config ngrok-backend.yml backend" -ForegroundColor Gray
Write-Host ""
Write-Host "在终端 2 运行（前端）：" -ForegroundColor White
Write-Host "  cd D:\AAA\毕业设计\backend" -ForegroundColor Gray
Write-Host "  ngrok start --config ngrok-frontend.yml frontend" -ForegroundColor Gray
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


