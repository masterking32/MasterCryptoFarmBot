@echo off
setlocal enabledelayedexpansion

:: check if git exists
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git is not installed or not in PATH. Please install Git and try again.
    echo to install git, visit https://git-scm.com/download/win
    exit /b 1
)

:: Check if Python 3.12 and pip are installed
where py >nul 2>nul
if %errorlevel% neq 0 (
    echo Python launcher is not installed or not in PATH. Please install Python and try again.
    echo To install Python, visit https://www.python.org/downloads/
    exit /b 1
)

py -3.12 --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Python 3.12 is not installed. Please install Python 3.12 and try again.
    exit /b 1
)

:: Set python_alias to use Python 3.12
set python_alias=py -3.12

where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo pip is not installed or not in PATH. Please install pip and try again.
    exit /b 1
)

:: Display initial messages
echo ==========================================
echo Press CTRL+C to stop the bot
echo ==========================================
timeout /t 3

:loop
:: Update the bot
echo ==========================================
echo Updating bot...
echo ==========================================
git pull origin main
if %errorlevel% neq 0 (
    echo Failed to update the bot. Retrying in 5 seconds...
    timeout /t 5
    goto loop
)
echo Project updated successfully
timeout /t 2

echo ==========================================
echo Updating dependencies...
echo ==========================================
%python_alias% -m pip install -r requirements.txt >nul 2>nul
if %errorlevel% neq 0 (
    echo Failed to update dependencies. Retrying in 5 seconds...
    timeout /t 5
    goto loop
)
echo Dependencies updated successfully

:: Start the bot
echo ==========================================
echo Starting bot...
echo ==========================================
%python_alias% main.py
if %errorlevel% neq 0 (
    echo Bot encountered an error. Restarting in 5 seconds...
    timeout /t 5
    goto loop
) 
echo Bot stopped. Restarting in 5 seconds...
timeout /t 5
goto loop

:ctrlc
echo ==========================================
echo CTRL+C pressed. Exiting...
echo ==========================================
exit /b
