@echo off
title Cyber Security Lab - Mode Lokal
cd /d "%~dp0"
echo ======================================================================
echo    MEMULAI LAB CYBER SECURITY (MODE LOKAL OFFLINE)
echo ======================================================================
echo.
echo [*] Memastikan database siap...
python init_db.py
echo [*] Membuka web browser di http://127.0.0.1:5050 ...
timeout /t 1 >nul
start http://127.0.0.1:5050
python app.py
pause
