# 自动添加 ngrok 到系统 PATH 的脚本
# 需要管理员权限运行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ngrok PATH 配置工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "✗ 需要管理员权限" -ForegroundColor Red
    Write-Host ""
    Write-Host "请右键点击 PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    Write-Host "然后重新运行此脚本" -ForegroundColor Yellow
    exit
}

Write-Host "✓ 已获得管理员权限" -ForegroundColor Green
Write-Host ""

# 查找 ngrok.exe
Write-Host "正在查找 ngrok.exe..." -ForegroundColor Cyan

$possiblePaths = @(
    "$env:USERPROFILE\Downloads\ngrok",
    "$env:USERPROFILE\Desktop\ngrok",
    "C:\ngrok",
    "D:\ngrok",
    "C:\Tools\ngrok",
    "D:\Tools\ngrok"
)

$ngrokPath = $null

# 检查常见位置
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\ngrok.exe") {
        $ngrokPath = $path
        Write-Host "✓ 找到 ngrok.exe 在: $path" -ForegroundColor Green
        break
    }
}

# 如果没找到，让用户输入
if (-not $ngrokPath) {
    Write-Host "未在常见位置找到 ngrok.exe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请提供 ngrok.exe 所在的完整目录路径" -ForegroundColor Cyan
    Write-Host "例如: C:\ngrok 或 D:\Tools\ngrok" -ForegroundColor Gray
    Write-Host ""
    
    $userPath = Read-Host "请输入路径"
    
    if ([string]::IsNullOrWhiteSpace($userPath)) {
        Write-Host "✗ 路径不能为空" -ForegroundColor Red
        exit
    }
    
    # 移除末尾的反斜杠
    $userPath = $userPath.TrimEnd('\')
    
    if (Test-Path "$userPath\ngrok.exe") {
        $ngrokPath = $userPath
        Write-Host "✓ 确认找到 ngrok.exe" -ForegroundColor Green
    } else {
        Write-Host "✗ 在指定路径未找到 ngrok.exe" -ForegroundColor Red
        Write-Host "  路径: $userPath\ngrok.exe" -ForegroundColor Gray
        exit
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "添加到系统 PATH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取当前系统 PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

# 检查是否已存在
if ($currentPath -like "*$ngrokPath*") {
    Write-Host "✓ ngrok 路径已在系统 PATH 中" -ForegroundColor Green
    Write-Host "  路径: $ngrokPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "测试运行 ngrok..." -ForegroundColor Cyan
    
    # 刷新当前会话的 PATH
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    
    try {
        $version = ngrok version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ ngrok 可以正常运行" -ForegroundColor Green
            Write-Host "  版本: $version" -ForegroundColor Gray
        } else {
            Write-Host "⚠ ngrok 可能无法运行，请重新打开终端窗口" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ 请重新打开终端窗口后测试" -ForegroundColor Yellow
    }
} else {
    # 添加到系统 PATH
    $newPath = $currentPath + ";$ngrokPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
    
    Write-Host "✓ 已添加 ngrok 到系统 PATH" -ForegroundColor Green
    Write-Host "  路径: $ngrokPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "重要提示" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "1. 请关闭所有已打开的 PowerShell/CMD 窗口" -ForegroundColor Yellow
    Write-Host "2. 重新打开新的终端窗口" -ForegroundColor Yellow
    Write-Host "3. 运行 'ngrok version' 验证配置" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "配置完成！" -ForegroundColor Green



