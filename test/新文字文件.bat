@echo off
setlocal

:: �]�w Python �w�ˤ��W�١]���]�w�ˤ��O python-installer.exe�^
set INSTALLER=python-installer.exe

:: �ˬd Python �O�_�w�w�˨��ˬd����
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python ���w�ˡA�Цw�� Python�C
    call :ask_user_to_install
    goto end
)

:: ���o��e�� Python ����
for /f "delims=" %%i in ('python --version 2^>nul') do set PYTHON_VERSION=%%i

:: ���������� (���]�榡�� Python 3.11.0)
for /f "tokens=2 delims= " %%i in ("%PYTHON_VERSION%") do set VERSION=%%i
for /f "tokens=1,2,3 delims=." %%i in ("%VERSION%") do (
    set MAJOR=%%i
    set MINOR=%%j
    set PATCH=%%k
)

:: �ˬd�����O�_�j�󵥩� 3.11.7
if %MAJOR% LSS 3 (
    echo ��e������ %VERSION%�A�C��n�D�� 3.11.7�A���b�w�˲ŦX�n�D������...
    call :ask_user_to_install
    goto end
)

if %MAJOR% LSS 3 (
    echo ��e������ %VERSION%�A�����������n�D�A���b�w�˲ŦX�n�D������...
    call :ask_user_to_install
    goto end
)

if %MAJOR% LSS 3 (
    echo ��e������ %VERSION%�A�����������n�D�A���b�w�˲ŦX�n�D������..
 
