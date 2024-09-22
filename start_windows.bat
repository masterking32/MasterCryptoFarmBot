:loop
git pull origin main
py main.py
timeout /t 5
goto loop
