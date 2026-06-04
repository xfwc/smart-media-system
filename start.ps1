Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  智能传媒内容分析与推荐系统" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill old processes on port 8000
Write-Host "[1/3] 清理旧进程..." -ForegroundColor Yellow
netstat -ano | Select-String ":8000" | Select-String "LISTENING" | ForEach-Object {
    $pid = ($_ -split "\s+")[-1]
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
}
Start-Sleep 1

# Start backend
Write-Host "[2/3] 启动后端 (http://127.0.0.1:8000)..." -ForegroundColor Yellow
$backendDir = Join-Path $PSScriptRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Sleep 4

# Start frontend
Write-Host "[3/3] 启动前端 (http://localhost:5173)..." -ForegroundColor Yellow
$frontendDir = Join-Path $PSScriptRoot "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm run dev"
Start-Sleep 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  启动完成！" -ForegroundColor Green
Write-Host "  前端: http://localhost:5173" -ForegroundColor Green
Write-Host "  后端: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  API文档: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Read-Host "按 Enter 关闭..."
