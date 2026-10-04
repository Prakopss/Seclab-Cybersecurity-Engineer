@echo off
setlocal
title Fast Track Cyber Security Lab
color 0B

:MENU
cls
echo ======================================================================
echo           SELAMAT DATANG DI LAB PRAKTIK CYBER SECURITY
echo          Folder: C:\website junior cybersecuriy engineer
echo ======================================================================
echo.
echo  Pilih cara menjalankan lab yang Anda inginkan:
echo.
echo   [1] MODE PUBLIK NGROK (Sangat Disarankan - Bebas Blokir DNS Provider)
echo       - Menggunakan Ngrok (*.ngrok-free.app)
echo       - Mahasiswa bisa langsung klik link tanpa masalah DNS_PROBE_NXDOMAIN
echo       - Link otomatis ter-copy ke clipboard laptop Anda
echo.
echo   [2] MODE PUBLIK CLOUDFLARE TUNNEL
echo       - Menggunakan Cloudflare (*.trycloudflare.com)
echo       - Catatan: Perlu Secure DNS di browser mahasiswa jika provider memblokir
echo.
echo   [3] MODE LOKAL (Offline di Laptop Sendiri)
echo       - Berjalan offline di browser: http://127.0.0.1:5050
echo       - Browser akan terbuka secara otomatis
echo.
echo   [4] KELUAR
echo.
echo ======================================================================
set /p PILIHAN=" Masukkan angka pilihan Anda [1, 2, 3, atau 4]: "

if "%PILIHAN%"=="1" goto MODE_NGROK
if "%PILIHAN%"=="2" goto MODE_CLOUDFLARE
if "%PILIHAN%"=="3" goto MODE_LOKAL
if "%PILIHAN%"=="4" exit /b 0

echo.
echo  [!] Pilihan tidak valid. Silakan pilih 1, 2, 3, atau 4.
timeout /t 2 >nul
goto MENU

:MODE_NGROK
cls
python launcher_ngrok.py
pause
goto MENU

:MODE_CLOUDFLARE
cls
python launcher_public.py
pause
goto MENU

:MODE_LOKAL
cls
title Cyber Security Lab - Mode Lokal
echo ======================================================================
echo  MENJALANKAN LAB CYBER SECURITY DALAM MODE LOKAL...
echo ======================================================================
echo.
echo [*] Menyiapkan database...
python init_db.py
echo [*] Membuka browser: http://127.0.0.1:5050 ...
timeout /t 1 >nul
start http://127.0.0.1:5050
python app.py
pause
goto MENU
