@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install -q tweepy
    py bot.py --loop
) else (
    python -m pip install -q tweepy
    python bot.py --loop
)
pause
