@echo off
chcp 65001 >nul
echo ============================================
echo 启动生产环境服务
echo ============================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先创建虚拟环境
    echo 运行: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/5] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 无法激活虚拟环境
    pause
    exit /b 1
)

REM 检查 Redis 是否运行（WebSocket 需要）
echo [2/5] 检查 Redis 服务...
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if errorlevel 1 (
    echo [警告] Redis 服务未运行，WebSocket 功能可能不可用
    echo 如需使用 WebSocket，请先启动 Redis
    echo.
) else (
    echo [OK] Redis 服务正在运行
)

REM 检查 MySQL 连接
echo [3/5] 检查数据库连接...
python -c "import MySQLdb" 2>nul
if errorlevel 1 (
    echo [错误] 无法导入 MySQLdb，请检查数据库配置
    pause
    exit /b 1
)

REM 设置环境变量
echo [4/5] 设置生产环境变量...
set DJANGO_SETTINGS_MODULE=core.settings_production

REM 收集静态文件
echo [5/5] 收集静态文件...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo [警告] 收集静态文件失败，继续启动...
)

echo.
echo ============================================
echo 启动后端服务...
echo ============================================
echo.
echo 使用 Daphne 启动（支持 WebSocket）
echo 服务地址: http://0.0.0.0:8000
echo.
echo 提示：
echo 1. 请在新终端启动内网穿透工具（如 ngrok）
echo 2. 将内网穿透地址配置到前端
echo 3. 按 Ctrl+C 停止服务
echo.

REM 启动 Daphne（支持 WebSocket）
daphne -b 0.0.0.0 -p 8000 core.asgi:application

pause




