@echo off
setlocal enabledelayedexpansion

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

:: Start the bot
echo Starting bot...
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

