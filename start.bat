@echo off
chcp 65001 >nul
title 智能传媒内容分析与推荐系统

echo ========================================
echo   智能传媒内容分析与推荐系统
echo ========================================
echo.

:: Kill old
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
timeout /t 1 >nul

:: Init DB
if not exist "%~dp0backend\smart_media.db" (
    echo [初始化] 创建数据库...
    cd /d %~dp0backend
    python -c "from app.db.session import _get_engine; _get_engine(); print('OK')" >nul
    python scripts/seed_data.py
    cd /d %~dp0
)

:: Start backend (hidden window)
echo [1/2] 后端启动中...
start "" /min cmd /c "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 4 >nul

:: Start frontend (hidden window)
echo [2/2] 前端启动中...
start "" /min cmd /c "cd /d %~dp0frontend && npm run dev"
timeout /t 3 >nul

echo.
echo ========================================
echo   启动完成! 浏览器访问:
echo   http://localhost:5173
echo ========================================
echo.
echo 关闭此窗口不影响服务运行
pause
exit
