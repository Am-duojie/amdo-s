@echo off
echo ========================================
echo 添加官方验商品测试数据
echo ========================================
echo.

cd /d %~dp0..
python scripts/add_verified_test_data.py

echo.
echo ========================================
echo 按任意键退出...
pause >nul
