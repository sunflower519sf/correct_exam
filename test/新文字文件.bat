@echo off
setlocal enabledelayedexpansion
chcp 65001

REM 確保 Python 可執行檔在 PATH 中
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python 未安裝或未加入 PATH 環境變數。
    pause
    exit /b 1
)

REM 確保 pip 可執行檔可用
python -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo pip 未正確安裝。請檢查您的 Python 安裝。
    pause
    exit /b 1
)

REM 升級 pip
echo 正在升級 pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo pip 升級失敗！
    pause
    exit /b 1
)

REM 安裝需求
if exist requirements.txt (
    echo 正在安裝需求模組...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 模組安裝失敗！
        pause
        exit /b 1
    )
) else (
    echo 未找到 requirements.txt 文件！
    pause
    exit /b 1
)

REM 執行主程式
echo 啟動主程式...
python main.py
if %errorlevel% neq 0 (
    echo 主程式執行失敗！
    pause
    exit /b 1
)

endlocal
pause
