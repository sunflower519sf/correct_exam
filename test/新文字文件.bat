@echo off
setlocal

:: 設定 Python 安裝文件名稱（假設安裝文件是 python-installer.exe）
set INSTALLER=python-installer.exe

:: 檢查 Python 是否已安裝並檢查版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 未安裝，請安裝 Python。
    call :ask_user_to_install
    goto end
)

:: 取得當前的 Python 版本
for /f "delims=" %%i in ('python --version 2^>nul') do set PYTHON_VERSION=%%i

:: 提取版本號 (假設格式為 Python 3.11.0)
for /f "tokens=2 delims= " %%i in ("%PYTHON_VERSION%") do set VERSION=%%i
for /f "tokens=1,2,3 delims=." %%i in ("%VERSION%") do (
    set MAJOR=%%i
    set MINOR=%%j
    set PATCH=%%k
)

:: 檢查版本是否大於等於 3.11.7
if %MAJOR% LSS 3 (
    echo 當前版本為 %VERSION%，低於要求的 3.11.7，正在安裝符合要求的版本...
    call :ask_user_to_install
    goto end
)

if %MAJOR% LSS 3 (
    echo 當前版本為 %VERSION%，但仍未滿足要求，正在安裝符合要求的版本...
    call :ask_user_to_install
    goto end
)

if %MAJOR% LSS 3 (
    echo 當前版本為 %VERSION%，但仍未滿足要求，正在安裝符合要求的版本..
 
