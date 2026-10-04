@echo off
title Cyber Security Lab - Server Publik Ngrok (Bebas Blokir)
cd /d "%~dp0"
python launcher_ngrok.py
if %errorlevel% neq 0 (
    echo.
    echo [!] Terjadi kendala saat menjalankan launcher Ngrok.
    pause
)
