@echo off
setlocal

REM Check if Python is installed and in PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    goto install_python
)

REM Check Python version
for /f "tokens=2 delims= " %%i in ('python --version') do set PY_VERSION=%%i
for /f "tokens=1,2,3 delims=." %%a in ("%PY_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

if %MAJOR% lss 3 goto install_python
if %MAJOR%==3 if %MINOR% lss 11 goto install_python
if %MAJOR%==3 if %MINOR%==11 if %PATCH% lss 7 goto install_python

echo Python version %PY_VERSION% is sufficient.
goto install_requirements

:install_python
echo Installing Python...
REM Add your Python installation logic here (e.g., call an installer or guide the user).
goto end

:install_requirements
echo Installing required Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install required packages.
    goto end
)

echo All requirements installed successfully.

goto end

:end
echo Script completed.
endlocal
pause
