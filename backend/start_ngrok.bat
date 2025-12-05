@echo off
chcp 65001 >nul
echo ============================================
echo 启动 Ngrok 内网穿透
echo ============================================
echo.

REM 检查 ngrok 是否安装
where ngrok >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 ngrok
    echo.
    echo 请先安装 ngrok：
    echo 1. 访问 https://ngrok.com/ 注册账号
    echo 2. 下载 ngrok.exe
    echo 3. 将 ngrok.exe 放到系统 PATH 或当前目录
    echo 4. 运行: ngrok config add-authtoken 你的authtoken
    echo.
    pause
    exit /b 1
)

echo 正在启动 ngrok，映射本地 8000 端口...
echo.
echo 提示：
echo - ngrok 会提供一个公网地址（如 https://xxxx.ngrok-free.app）
echo - 将该地址配置到前端的 API 地址
echo - 按 Ctrl+C 停止 ngrok
echo.

REM 启动 ngrok
ngrok http 8000

pause




