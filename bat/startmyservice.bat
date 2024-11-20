@echo off
:: ------------------------------
:: Check if the script is running as Administrator
:: ------------------------------
:: Check for administrator privileges
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Attempting to run as Administrator...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~s0' -Verb RunAs"
    exit /b
)

:: ------------------------------
:: Configuration
:: ------------------------------
set SERVICE_NAME=MyService
set DISPLAY_NAME="My Telemed Service"
set DESCRIPTION="Service for Telemed Application"
set EXECUTABLE_PATH=C:\telemed\Release\smarttelemed.exe
set LOG_FILE=C:\telemed\service_install.log
set RESTART_SCRIPT=C:\telemed\secureagent-1.1.1\restart.bat

:: ------------------------------
:: Install the Service
:: ------------------------------
echo Installing the service "%SERVICE_NAME%"... >> %LOG_FILE%
sc create "%SERVICE_NAME%" binPath= "%EXECUTABLE_PATH%" displayname= "%DISPLAY_NAME%" start= auto >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo Failed to install the service. Check log: %LOG_FILE%
    exit /b 1
)

:: ------------------------------
:: Configure Recovery Options
:: ------------------------------
echo Configuring recovery options... >> %LOG_FILE%
sc failure "%SERVICE_NAME%" reset= 86400 actions= restart/60000/restart/60000/restart/60000 >> %LOG_FILE% 2>&1

:: ------------------------------
:: Start the Service
:: ------------------------------
echo Starting the service "%SERVICE_NAME%"... >> %LOG_FILE%
sc start "%SERVICE_NAME%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo Failed to start the service. Check log: %LOG_FILE%
    exit /b 1
)

:: ------------------------------
:: Run restart.bat (optional)
:: ------------------------------
echo Running restart script from "%RESTART_SCRIPT%"... >> %LOG_FILE%
call "%RESTART_SCRIPT%" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo Failed to run restart script. Check log: %LOG_FILE%
    exit /b 1
)

:: ------------------------------
:: Finish
:: ------------------------------
echo Service "%SERVICE_NAME%" installed and started successfully. >> %LOG_FILE%
echo Done.
exit /b 0
