#!/bin/bash

# 送货单生成系统 - 一键启动
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================="
echo "  送货单生成系统"
echo "========================================="
echo ""

# ---- 检查 Python ----
if ! command -v python3 &>/dev/null; then
    echo "[错误] 未找到 python3，请先安装 Python 3"
    exit 1
fi

# ---- 检查并安装后端依赖 ----
echo "[检查] 后端 Python 依赖..."
cd "$DIR/backend"
MISSING=0
for pkg in fastapi uvicorn openpyxl multipart pywebview; do
    python3 -c "import $pkg" 2>/dev/null || MISSING=1
done

if [ $MISSING -eq 1 ]; then
    echo "[安装] 正在安装后端依赖..."
    pip3 install -r requirements.txt -q
    if [ $? -ne 0 ]; then
        echo "[错误] 后端依赖安装失败"
        exit 1
    fi
    echo "[完成] 后端依赖安装成功"
else
    echo "[完成] 后端依赖已就绪"
fi

# ---- 检查并安装前端依赖 + 构建 ----
cd "$DIR/frontend"
if [ ! -d "node_modules" ]; then
    if ! command -v npm &>/dev/null; then
        echo "[错误] 未找到 npm，请先安装 Node.js"
        exit 1
    fi
    echo "[安装] 正在安装前端依赖..."
    npm install -q
fi

if [ ! -d "dist" ]; then
    echo "[构建] 正在构建前端..."
    npm run build -q
    if [ $? -ne 0 ]; then
        echo "[错误] 前端构建失败"
        exit 1
    fi
    echo "[完成] 前端构建成功"
else
    echo "[完成] 前端已构建"
fi

# ---- 启动桌面应用 ----
echo ""
echo "[启动] 正在打开送货单生成系统..."
echo "  关闭窗口即可退出程序"
echo ""

cd "$DIR/backend"
python3 desktop.py
