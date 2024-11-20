@echo off
:: ------------------------------
:: Script to install a Windows service to run the batch script at startup
:: ------------------------------

set SERVICE_NAME=MyTelemedService
set DISPLAY_NAME="Telemed Service"
set DESCRIPTION="Service to start ExpertSmartTelemed.exe and smarttelemed.exe"
set BATCH_SCRIPT_PATH="C:\telemed\start_programs.bat"
set LOG_FILE="C:\telemed\service_install.log"

:: Step 1: Install the service
echo Installing service "%SERVICE_NAME%"... >> %LOG_FILE%
sc create "%SERVICE_NAME%" binPath= "cmd /c start %BATCH_SCRIPT_PATH%" start= auto >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo Failed to install the service. Check log: %LOG_FILE%
    exit /b 1
)

:: Step 2: Start the service
echo Starting the service "%SERVICE_NAME%"... >> %LOG_FILE%
sc start "%SERVICE_NAME%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo Failed to start the service. Check log: %LOG_FILE%
    exit /b 1
)

echo Service "%SERVICE_NAME%" installed and started successfully. >> %LOG_FILE%
echo Done.
exit /b 0
