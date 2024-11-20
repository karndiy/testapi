@echo off
:: ------------------------------
:: Script to restart restart.bat with Administrator privileges
:: ------------------------------

:: Step 1: Check if the script is running with admin privileges
:: If not, relaunch the script as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script needs to be run as Administrator.
    echo Restarting with administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c, \"%~dp0%restart_restart_bat.bat\"' -Verb RunAs"
    exit /b
)

:: Step 2: Optionally, close any running processes related to the restart.bat script
echo Closing any running instances of restart.bat...
taskkill /f /im restart.bat >nul 2>&1

:: Step 3: Wait for a moment to ensure it is closed
timeout /t 2 /nobreak >nul

:: Step 4: Restart the restart.bat script
echo Restarting restart.bat...
call "C:\telemed\secureagent-1.1.1\restart.bat"

:: Done
echo restart.bat has been restarted.
exit