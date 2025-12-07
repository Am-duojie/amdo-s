# 实时监控日志文件的 PowerShell 脚本
$logFile = "debug.log"
$lastSize = 0

Write-Host "开始监控日志文件: $logFile" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止监控" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    if (Test-Path $logFile) {
        $currentSize = (Get-Item $logFile).Length
        if ($currentSize -gt $lastSize) {
            $newContent = Get-Content $logFile -Tail 50 -Encoding UTF8
            Write-Host "========== 新日志内容 ==========" -ForegroundColor Cyan
            $newContent | ForEach-Object { Write-Host $_ }
            Write-Host ""
            $lastSize = $currentSize
        }
    }
    Start-Sleep -Seconds 1
}









