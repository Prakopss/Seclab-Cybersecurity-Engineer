@echo off
title Cyber Security Lab - Server Publik (Cloudflare Tunnel)
cd /d "%~dp0"
python launcher_public.py
if %errorlevel% neq 0 (
    echo.
    echo [!] Terjadi kendala saat menjalankan launcher.
    pause
)
