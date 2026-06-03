@echo off
chcp 65001 >nul
title 智能传媒系统 — 后端

cd /d %~dp0backend
echo [启动] 后端服务 http://127.0.0.1:8000
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
