@echo off
chcp 65001 >nul

echo =========================================
echo   构建 Windows 安装包
echo =========================================
echo.

set DIR=%~dp0
cd /d "%DIR%"

:: 0. 创建干净的构建环境
if not exist ".buildenv" (
    echo [0/4] 创建构建环境...
    python -m venv .buildenv
    .buildenv\Scripts\pip install -q fastapi uvicorn openpyxl python-multipart pywebview pyinstaller
    echo   构建环境就绪
) else (
    echo [0/4] 构建环境已存在
)

:: 1. 构建前端
echo [1/4] 构建前端...
cd /d "%DIR%frontend"
if not exist "node_modules" (
    call npm install -q
)
call npm run build
echo   前端构建完成

:: 2. 打包
echo [2/4] 打包应用...
cd /d "%DIR%backend"

"%DIR%.buildenv\Scripts\pyinstaller" ^
    --name "送货单生成系统" ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --add-data "templates;templates" ^
    --add-data "..\frontend\dist;static" ^
    desktop.py

:: 3. 压缩
echo [3/4] 压缩安装包...
cd /d "%DIR%backend\dist"
powershell -Command "Compress-Archive -Force -Path '送货单生成系统' -DestinationPath '送货单生成系统-win-x64.zip'"

:: 4. 输出
echo.
echo =========================================
echo   构建完成!
echo.
echo   安装包: backend\dist\送货单生成系统-win-x64.zip
echo =========================================
echo.
echo 分发: 将 .zip 发送给用户，解压后双击 送货单生成系统.exe 即可使用

pause
