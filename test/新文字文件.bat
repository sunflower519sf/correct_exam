@echo off

:: Keep the CMD window open for debugging
setlocal enabledelayedexpansion

:: Check if Python is installed and its version
python --version 2>nul | findstr "Python 3\.11\.[7-9]" >nul
if %errorlevel% neq 0 (
    echo Python 3.11.7 or higher is not detected. Installing Python...

    :: Install Python in windowed mode to display progress bar
    set "PYTHON_INSTALLER=python-3.11.7-amd64.exe"
    if exist "%PYTHON_INSTALLER%" (
        echo Launching Python installer...
        start /wait "" "%PYTHON_INSTALLER%" InstallAllUsers=1 PrependPath=1 Include_test=0

        if %errorlevel% neq 0 (
            echo Python installation failed.
            pause
            exit /b 1
        )
    ) else (
        echo Error: Python installer "%PYTHON_INSTALLER%" not found.
        pause
        exit /b 1
    )
)

:: Check if Python is in the PATH
set "PYTHON_PATH_CHECK=%ProgramFiles%\Python311\python.exe"
if exist "%PYTHON_PATH_CHECK%" (
    for %%I in ("%PYTHON_PATH_CHECK%") do set "PYTHON_DIR=%%~dpI"
    set "PATH=!PYTHON_DIR!;%PATH%"
    setx PATH "!PYTHON_DIR!;%PATH%" >nul
) else (
    echo Error: Python executable not found in expected path.
    pause
    exit /b 1
)

:: Confirm Python is accessible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not accessible after installation.
    pause
    exit /b 1
)

:: Install required Python packages
if exist "requirements.txt" (
    echo Installing required Python packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install required Python packages.
        pause
        exit /b 1
    )
) else (
    echo Error: requirements.txt not found.
    pause
    exit /b 1
)

echo Setup complete.
pause
exit /b 0
