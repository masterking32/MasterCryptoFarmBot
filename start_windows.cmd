@echo off
setlocal enabledelayedexpansion

:: check if git exists
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git is not installed or not in PATH. Please install Git and try again.
    exit /b 1
)

:: check if python exists
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install python and try again.
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

:: updating requirements
echo ==========================================
echo Updating requirements...
echo ==========================================
py -m pip install -r requirements.txt >nul 2>nul
if %errorlevel% neq 0 (
    echo Failed to install requirements. Retrying in 5 seconds...
    timeout /t 5
)
echo Requirements updated successfully
timeout /t 2

:: Start the bot
echo ==========================================
echo Starting bot...
echo ==========================================
py main.py
if %errorlevel% neq 0 (
    echo Bot encountered an error. Restarting in 5 seconds...
) else (
    echo Bot stopped. Restarting in 5 seconds...
)
timeout /t 5
goto loop

:ctrlc
echo ==========================================
echo CTRL+C pressed. Exiting...
echo ==========================================
exit /b
