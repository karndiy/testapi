@echo off
:: ------------------------------
:: Script to close and restart smarttelemed.exe
:: ------------------------------

:: Step 1: Find and close any running instances of smarttelemed.exe
echo Closing any running instances of smarttelemed.exe...
taskkill /f /im smarttelemed.exe >nul 2>&1

:: Step 2: Wait for a moment to ensure the app is closed (optional)
timeout /t 2 /nobreak >nul

:: Step 3: Restart smarttelemed.exe
echo Restarting smarttelemed.exe...
start "" "C:\telemed\Release\smarttelemed.exe"

:: Done
echo smarttelemed.exe has been restarted.
exit
