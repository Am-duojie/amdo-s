# ngrok 配置脚本
# 用于设置 ngrok 内网穿透

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ngrok 配置向导" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 ngrok 是否已安装
$ngrokInstalled = $false
try {
    $ngrokVersion = ngrok version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $ngrokInstalled = $true
        Write-Host "✓ ngrok 已安装" -ForegroundColor Green
        Write-Host "  版本信息: $ngrokVersion" -ForegroundColor Gray
    }
} catch {
    $ngrokInstalled = $false
}

if (-not $ngrokInstalled) {
    Write-Host "ngrok 未安装，请先安装 ngrok" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "安装方法：" -ForegroundColor Cyan
    Write-Host "1. 访问 https://ngrok.com/download 下载 Windows 版本" -ForegroundColor White
    Write-Host "2. 解压到任意目录（如 C:\ngrok）" -ForegroundColor White
    Write-Host "3. 将 ngrok.exe 所在目录添加到系统 PATH 环境变量" -ForegroundColor White
    Write-Host ""
    Write-Host "或者使用包管理器安装：" -ForegroundColor Cyan
    Write-Host "  choco install ngrok    # 如果安装了 Chocolatey" -ForegroundColor White
    Write-Host "  scoop install ngrok    # 如果安装了 Scoop" -ForegroundColor White
    Write-Host ""
    
    $continue = Read-Host "是否已安装 ngrok？(y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "请先安装 ngrok，然后重新运行此脚本" -ForegroundColor Yellow
        exit
    }
    
    # 再次检查
    try {
        $ngrokVersion = ngrok version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $ngrokInstalled = $true
            Write-Host "✓ ngrok 安装成功" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ ngrok 仍未安装或未添加到 PATH" -ForegroundColor Red
        Write-Host "请确保 ngrok.exe 在系统 PATH 中" -ForegroundColor Yellow
        exit
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步骤 1: 获取 ngrok authtoken" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 访问 https://dashboard.ngrok.com/signup 注册账号（如果还没有）" -ForegroundColor White
Write-Host "2. 登录后访问 https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
Write-Host "3. 复制您的 authtoken" -ForegroundColor White
Write-Host ""

$authtoken = Read-Host "请输入您的 ngrok authtoken"

if ([string]::IsNullOrWhiteSpace($authtoken)) {
    Write-Host "✗ authtoken 不能为空" -ForegroundColor Red
    exit
}

# 配置 authtoken
Write-Host ""
Write-Host "正在配置 ngrok authtoken..." -ForegroundColor Yellow
$result = ngrok config add-authtoken $authtoken 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ ngrok authtoken 配置成功" -ForegroundColor Green
} else {
    Write-Host "✗ 配置失败: $result" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步骤 2: 测试 ngrok 连接" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请确保 Django 服务正在运行（python manage.py runserver）" -ForegroundColor Yellow
Write-Host ""

$start = Read-Host "是否现在启动 ngrok？(y/n)"
if ($start -eq "y" -or $start -eq "Y") {
    Write-Host ""
    Write-Host "正在启动 ngrok（映射本地 8000 端口）..." -ForegroundColor Yellow
    Write-Host "按 Ctrl+C 停止 ngrok" -ForegroundColor Gray
    Write-Host ""
    Write-Host "注意：ngrok 启动后会显示公网地址，请复制该地址" -ForegroundColor Cyan
    Write-Host "然后在 settings.py 中更新 BACKEND_URL" -ForegroundColor Cyan
    Write-Host ""
    
    # 启动 ngrok
    ngrok http 8000
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "手动启动 ngrok" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "在命令行中运行以下命令启动 ngrok：" -ForegroundColor White
    Write-Host "  ngrok http 8000" -ForegroundColor Green
    Write-Host ""
    Write-Host "启动后，ngrok 会显示类似以下的信息：" -ForegroundColor White
    Write-Host "  Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "请复制 https://xxxx-xx-xx-xx-xx.ngrok-free.app 这个地址" -ForegroundColor Cyan
    Write-Host "然后在 settings.py 中更新 BACKEND_URL" -ForegroundColor Cyan
}











