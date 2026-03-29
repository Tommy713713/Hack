@echo off

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装，请先安装Python 3.7或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt

:: 启动后端服务
echo 正在启动后端服务...
start "AI Canteen Assistant Backend" python app.py

:: 等待服务启动
echo 正在启动前端页面...
ping 127.0.0.1 -n 3 >nul

:: 打开前端页面
start "AI Canteen Assistant" index.html

echo 启动完成！请在浏览器中查看AI食堂助手
pause