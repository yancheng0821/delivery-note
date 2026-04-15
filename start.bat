@echo off
chcp 65001 >nul
title 送货单生成系统

echo =========================================
echo   送货单生成系统
echo =========================================
echo.

:: 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 python，请先安装 Python 3
    pause
    exit /b 1
)

:: 检查并安装后端依赖
echo [检查] 后端 Python 依赖...
cd /d "%~dp0backend"
python -c "import fastapi, uvicorn, openpyxl, multipart, webview" 2>nul
if %errorlevel% neq 0 (
    echo [安装] 正在安装后端依赖...
    pip install -r requirements.txt -q
    if %errorlevel% neq 0 (
        echo [错误] 后端依赖安装失败
        pause
        exit /b 1
    )
    echo [完成] 后端依赖安装成功
) else (
    echo [完成] 后端依赖已就绪
)

:: 检查并安装前端依赖 + 构建
cd /d "%~dp0frontend"
if not exist "node_modules" (
    where npm >nul 2>nul
    if %errorlevel% neq 0 (
        echo [错误] 未找到 npm，请先安装 Node.js
        pause
        exit /b 1
    )
    echo [安装] 正在安装前端依赖...
    call npm install -q
)

if not exist "dist" (
    echo [构建] 正在构建前端...
    call npm run build
    if %errorlevel% neq 0 (
        echo [错误] 前端构建失败
        pause
        exit /b 1
    )
    echo [完成] 前端构建成功
) else (
    echo [完成] 前端已构建
)

:: 启动桌面应用
echo.
echo [启动] 正在打开送货单生成系统...
echo   关闭窗口即可退出程序
echo.

cd /d "%~dp0backend"
python desktop.py
