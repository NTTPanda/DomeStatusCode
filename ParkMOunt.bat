@echo off
setlocal EnableDelayedExpansion

:: ===================== ADMIN CHECK =====================
net session >nul 2>&1 || (
    echo Please run this script as Administrator
    pause
    exit /b
)

:: ===================== CONFIG ==========================
set LOG_DIR=C:\Users\ROHIT\OCS_Logs
set LOG_FILE="%LOG_DIR%\park_status.log"

:: ===================== CREATE LOG DIR ===================
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

:: ===================== START LOG ========================
echo ===================================================== >> %LOG_FILE%
echo OCS Upgrade Script Started >> %LOG_FILE%
echo Date: %date% Time: %time% >> %LOG_FILE%
echo ===================================================== >> %LOG_FILE%

:: ===================== PARK MOUNT =======================
echo Running: curl -X POST http://localhost:3001/rpc/mount_park -d '{}' | jq >> %LOG_FILE%
curl -X POST http://localhost:3001/rpc/mount_park -d "{}" | jq >> %LOG_FILE% 2>&1

:: ===================== WAIT =============================
echo Waiting 100 seconds... >> %LOG_FILE%
timeout /t 100 /nobreak >> %LOG_FILE% 2>&1

:: ===================== UPGRADE COMMAND ==================
echo Running: uvx oscctl upgrade >> %LOG_FILE%
uvx oscctl upgrade >> %LOG_FILE% 2>&1

:: ===================== END LOG ==========================
echo ===================================================== >> %LOG_FILE%
echo Script finished at %date% %time% >> %LOG_FILE%
echo ===================================================== >> %LOG_FILE%

endlocal
