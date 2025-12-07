# 设置 ngrok 配置文件脚本
# 自动检测或提示输入 authtoken，然后创建配置文件

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "设置 Ngrok 配置文件" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 尝试从 ngrok 默认配置读取 authtoken
$authtoken = $null
$ngrokConfigPaths = @(
    "$env:USERPROFILE\.ngrok2\ngrok.yml",
    "$env:APPDATA\ngrok\ngrok.yml",
    "$env:LOCALAPPDATA\ngrok\ngrok.yml"
)

foreach ($path in $ngrokConfigPaths) {
    if (Test-Path $path) {
        Write-Host "找到 ngrok 配置文件: $path" -ForegroundColor Gray
        $content = Get-Content $path -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match "authtoken:\s*(.+)") {
            $authtoken = $matches[1].Trim()
            Write-Host "✓ 已从配置文件读取 authtoken" -ForegroundColor Green
            break
        }
    }
}

# 如果没找到，尝试从 ngrok 命令获取
if (-not $authtoken) {
    Write-Host "尝试从 ngrok 命令获取 authtoken..." -ForegroundColor Gray
    try {
        $ngrokConfig = ngrok config check 2>&1
        if ($ngrokConfig -match "authtoken:\s*(.+)") {
            $authtoken = $matches[1].Trim()
            Write-Host "✓ 已从 ngrok 命令读取 authtoken" -ForegroundColor Green
        }
    } catch {
        Write-Host "无法从 ngrok 命令获取 authtoken" -ForegroundColor Yellow
    }
}

# 如果还是没找到，提示用户输入
if (-not $authtoken) {
    Write-Host ""
    Write-Host "未找到 ngrok authtoken，请手动输入" -ForegroundColor Yellow
    Write-Host "获取地址: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Gray
    Write-Host ""
    $authtoken = Read-Host "请输入您的 ngrok authtoken"
    
    if ([string]::IsNullOrWhiteSpace($authtoken)) {
        Write-Host "错误: authtoken 不能为空" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "正在创建配置文件..." -ForegroundColor Yellow

# 创建后端配置文件
$backendConfig = @"
version: "2"
authtoken: $authtoken
tunnels:
  backend:
    addr: 8000
    proto: http
"@

$backendConfig | Out-File -FilePath "ngrok-backend.yml" -Encoding UTF8 -NoNewline
Write-Host "✓ 已创建: ngrok-backend.yml" -ForegroundColor Green

# 创建前端配置文件
$frontendConfig = @"
version: "2"
authtoken: $authtoken
tunnels:
  frontend:
    addr: 5173
    proto: http
"@

$frontendConfig | Out-File -FilePath "ngrok-frontend.yml" -Encoding UTF8 -NoNewline
Write-Host "✓ 已创建: ngrok-frontend.yml" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置文件创建完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "使用方法：" -ForegroundColor Yellow
Write-Host "  终端 1（后端）: ngrok start --config ngrok-backend.yml backend" -ForegroundColor White
Write-Host "  终端 2（前端）: ngrok start --config ngrok-frontend.yml frontend" -ForegroundColor White
Write-Host ""




