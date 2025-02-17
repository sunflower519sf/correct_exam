@echo off
chcp 65001

REM 檢查是否有 Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python 未安裝，正在安裝...
    REM 假設目錄中有 Python 安裝檔案，名稱為 python-installer.exe
    python-installer.exe /passive InstallAllUsers=1 PrependPath=1
    if %ERRORLEVEL% NEQ 0 (
        echo Python 安裝失敗，請檢查安裝檔案。
        pause
        exit /b
    )
)

REM 獲取 Python 版本
for /f "tokens=2 delims= " %%a in ('python --version') do set PYTHON_VERSION=%%a

REM 提取主版本、副版本和修訂號
for /f "tokens=1-3 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

REM 檢查版本是否大於 3.11.7
if %MAJOR% LSS 3 goto InstallPython
if %MAJOR%==3 if %MINOR% LSS 11 goto InstallPython
if %MAJOR%==3 if %MINOR%==11 if %PATCH% LSS 7 goto InstallPython

goto CheckPath

:InstallPython
    echo Python 版本過低，正在重新安裝...
    python-installer.exe /passive InstallAllUsers=1 PrependPath=1
    if %ERRORLEVEL% NEQ 0 (
        echo Python 安裝失敗，請檢查安裝檔案。
        pause
        exit /b
    )
    goto CheckPath

:CheckPath
REM 檢查 Python 是否在環境變量中
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python 未在環境變量中，正在嘗試修復...
    python-installer.exe /passive InstallAllUsers=1 PrependPath=1
    if %ERRORLEVEL% NEQ 0 (
        echo 修復失敗，請檢查安裝檔案。
        pause
        exit /b
    )
)

REM 升級 pip 並安裝必要的依賴
python.exe -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo pip 升級失敗，請檢查網路連線。
    pause
    exit /b
)

pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo 依賴安裝失敗，請檢查 requirements.txt 文件。
    pause
    exit /b
)

REM 執行主程式
py -3.11 main.py
if %ERRORLEVEL% NEQ 0 (
    echo 運行指定版本失敗，使用預設執行...
    python main.py
    if %ERRORLEVEL% NEQ 0 (
        echo 運行失敗，請重新執行或是回報開發者。
    )
)
