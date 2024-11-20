@ECHO OFF

set SERVICE_NAME=NHSOSecureSmartCardAgent
set NHSOSSMC_FILE_NAME=NHSOSecureSmartCardAgent.exe
set NHSOSSMC_LOCATION="%~dp0%NHSOSSMC_FILE_NAME%"

echo ---------------------------------------------------
echo service path %NHSOSSMC_LOCATION%
echo ---------------------------------------------------

REM  Check for permissions
IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
    >nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
    >nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

if '%errorlevel%' NEQ '0' (
    echo Does not have Administrator permission for run the service.
    echo Run As Administrator required.
    pause
    exit /B
) else (
    goto RestartService
)

:RestartService
    echo ---------------------------------------------------
    echo List all file in the directory...
    echo ---------------------------------------------------
    
    dir "%~dp0"
    
    if exist %NHSOSSMC_LOCATION% (
        echo file %NHSOSSMC_LOCATION% exists.
        echo restarting NHSO Secure SmartCard Agent service...
        echo ---------------------------------------------------

        sc query %SERVICE_NAME% > nul
        if errorlevel 1060 (
            echo no service %SERVICE_NAME% installed on this machine.
            echo Done.
        ) else (
            echo service %SERVICE_NAME% already installed on this machine.
            sc queryex NHSOSecureSmartCardAgent|Find "STATE"|Find /v "RUNNING">ืีส&&(
                echo %SERVICE_NAME% is not running 
                net start NHSOSecureSmartCardAgent>nul||(Echo NHSOSecureSmartCardAgent wont start exit /b 1)
                echo NHSOSecureSmartCardAgent started
                echo Done.
            )||(
                echo NHSOSecureSmartCardAgent is working
                echo "restarting service %SERVICE_NAME% ..."
                net stop NHSOSecureSmartCardAgent>nul||(Echo NHSOSecureSmartCardAgent wont start exit /b 1)
                net start NHSOSecureSmartCardAgent>nul||(Echo NHSOSecureSmartCardAgent wont start exit /b 1)
                echo Done.
            )
        )
        @REM services.msc
        pause
    ) else (
        echo file %NHSOSSMC_LOCATION% does not exists.
        pause
    )
