# 配置多账号 ngrok 脚本
# 帮助用户为前后端配置不同的 ngrok 账号

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置多账号 Ngrok" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "此脚本将帮助您为前后端配置不同的 ngrok 账号" -ForegroundColor Yellow
Write-Host "这样可以确保前后端获得不同的地址" -ForegroundColor Yellow
Write-Host ""

# 检查现有配置文件
$backendConfig = "ngrok-backend.yml"
$frontendConfig = "ngrok-frontend.yml"

$hasBackendConfig = Test-Path $backendConfig
$hasFrontendConfig = Test-Path $frontendConfig

if ($hasBackendConfig) {
    Write-Host "✓ 找到后端配置文件: $backendConfig" -ForegroundColor Green
} else {
    Write-Host "✗ 未找到后端配置文件: $backendConfig" -ForegroundColor Yellow
}

if ($hasFrontendConfig) {
    Write-Host "✓ 找到前端配置文件: $frontendConfig" -ForegroundColor Green
} else {
    Write-Host "✗ 未找到前端配置文件: $frontendConfig" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置后端账号" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请输入后端 ngrok 账号的 authtoken：" -ForegroundColor Yellow
Write-Host "（如果还没有，请访问: https://dashboard.ngrok.com/get-started/your-authtoken）" -ForegroundColor Gray
$backendAuthtoken = Read-Host "后端 Authtoken"

if ([string]::IsNullOrWhiteSpace($backendAuthtoken)) {
    Write-Host "错误: authtoken 不能为空" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置前端账号" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请输入前端 ngrok 账号的 authtoken：" -ForegroundColor Yellow
Write-Host "（可以使用相同的账号，或使用不同的账号）" -ForegroundColor Gray
$frontendAuthtoken = Read-Host "前端 Authtoken"

if ([string]::IsNullOrWhiteSpace($frontendAuthtoken)) {
    Write-Host "错误: authtoken 不能为空" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "正在创建/更新配置文件..." -ForegroundColor Yellow

# 创建后端配置文件
$backendConfigContent = @"
version: 3
agent:
  authtoken: $backendAuthtoken
tunnels:
  backend:
    addr: 8000
    proto: http
"@

$backendConfigContent | Out-File -FilePath $backendConfig -Encoding UTF8 -NoNewline
Write-Host "✓ 已创建/更新: $backendConfig" -ForegroundColor Green

# 创建前端配置文件
$frontendConfigContent = @"
version: 3
agent:
  authtoken: $frontendAuthtoken
tunnels:
  frontend:
    addr: 5173
    proto: http
"@

$frontendConfigContent | Out-File -FilePath $frontendConfig -Encoding UTF8 -NoNewline
Write-Host "✓ 已创建/更新: $frontendConfig" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "使用方法：" -ForegroundColor Yellow
Write-Host ""
Write-Host "终端 1（后端）：" -ForegroundColor White
Write-Host "  cd D:\AAA\毕业设计\backend" -ForegroundColor Gray
Write-Host "  ngrok start --config ngrok-backend.yml backend" -ForegroundColor Gray
Write-Host ""
Write-Host "终端 2（前端）：" -ForegroundColor White
Write-Host "  cd D:\AAA\毕业设计\backend" -ForegroundColor Gray
Write-Host "  ngrok start --config ngrok-frontend.yml frontend" -ForegroundColor Gray
Write-Host ""
Write-Host "提示：" -ForegroundColor Cyan
Write-Host "- 如果使用不同的账号，前后端会获得不同的地址" -ForegroundColor White
Write-Host "- 如果使用相同的账号，地址可能相同（免费版限制）" -ForegroundColor White
Write-Host "- 建议使用不同的账号以确保地址不同" -ForegroundColor Yellow
Write-Host ""



