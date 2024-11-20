@echo off
:: ------------------------------
:: Script to close and restart ExpertSmartTelemed.exe
:: ------------------------------

:: Step 1: Find and close any running instances of ExpertSmartTelemed.exe
echo Closing any running instances of ExpertSmartTelemed.exe...
taskkill /f /im ExpertSmartTelemed.exe >nul 2>&1

:: Step 2: Wait for a moment to ensure the app is closed (optional)
timeout /t 2 /nobreak >nul

:: Step 3: Restart ExpertSmartTelemed.exe
echo Restarting ExpertSmartTelemed.exe...
start "" "C:\telemed\ExpertSmartTelemed\ExpertSmartTelemed net8.0\ExpertSmartTelemed.exe"

:: Done
echo ExpertSmartTelemed.exe has been restarted.
exit
