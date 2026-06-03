@echo off
chcp 65001 >nul
title 智能传媒系统 — 前端

cd /d %~dp0frontend
echo [启动] 前端服务 http://localhost:5173
echo.
npm run dev
