@echo off
chcp 65001 >nul
echo ============================================
echo 一键启动所有服务（开发环境）
echo ============================================
echo.

REM 启动后端服务
echo [1/3] 启动后端服务...
start "后端服务 - Django" cmd /k "cd backend && call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

timeout /t 3 /nobreak >nul

REM 启动前端服务
echo [2/3] 启动前端服务...
start "前端服务 - Vite" cmd /k "cd frontend && npm run dev"

timeout /t 3 /nobreak >nul

REM 提示启动内网穿透
echo [3/3] 提示：如需外网访问，请手动启动内网穿透工具
echo.
echo 服务已启动：
echo - 后端: http://127.0.0.1:8000
echo - 前端: http://localhost:5173
echo.
echo 如需外网访问：
echo - 运行 start_ngrok.bat 启动内网穿透
echo - 或使用其他内网穿透工具
echo.

pause




