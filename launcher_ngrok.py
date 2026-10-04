import os
import sys
import re
import time
import json
import urllib.request
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_FILE = os.path.join(BASE_DIR, 'app.py')

def find_ngrok():
    # 1. Cek di PATH
    try:
        res = subprocess.run(['where.exe', 'ngrok'], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return 'ngrok'
    except Exception:
        pass

    # 2. Cek di path winget
    winget_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\ngrok\ngrok.exe"),
        r"C:\Program Files\ngrok\ngrok.exe",
    ]
    for p in winget_paths:
        if os.path.exists(p):
            return p
    return 'ngrok'

def is_ngrok_authenticated():
    config_file = os.path.expandvars(r"%LOCALAPPDATA%\ngrok\ngrok.yml")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'authtoken:' in content:
                    return True
        except Exception:
            pass
    return False

def copy_to_clipboard(text):
    try:
        subprocess.run('clip', input=text, text=True, check=True)
        return True
    except Exception:
        return False

def setup_authtoken(ngrok_bin):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("        SETUP AUTHTOKEN NGROK (HANYA PERLU DILAKUKAN 1 KALI)       ")
    print("=" * 70)
    print("\n  Ngrok membutuhkan akun gratis agar link publik Anda bebas dari")
    print("  blokir DNS provider internet Indonesia.")
    print("\n  Langkah Mudah (Gratis - 30 detik):")
    print("  1. Daftar / Login via Google di: https://dashboard.ngrok.com/signup")
    print("  2. Ambil token Anda di:          https://dashboard.ngrok.com/get-started/your-authtoken")
    print("-" * 70)
    
    token = input("\n  Tempel (Paste) Authtoken Ngrok Anda di sini lalu tekan Enter:\n  > ").strip()
    if not token:
        print("[!] Token kosong. Dibatalkan.")
        sys.exit(1)
        
    res = subprocess.run([ngrok_bin, 'config', 'add-authtoken', token], capture_output=True, text=True)
    if res.returncode == 0:
        print("\n  [OK] Authtoken berhasil disimpan! Melanjutkan peluncuran...")
        time.sleep(2)
    else:
        print(f"\n  [!] Gagal menyimpan token: {res.stderr}")
        input("Tekan Enter untuk keluar...")
        sys.exit(1)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("     JUNIOR CYBERSECURITY ENGINEER LAB - NGROK SERVER LAUNCHER     ")
    print("=" * 70)

    ngrok_bin = find_ngrok()

    # Cek apakah sudah ada token
    if not is_ngrok_authenticated():
        setup_authtoken(ngrok_bin)

    print("\n[*] Menyiapkan database lab...")
    try:
        from init_db import init_db
        init_db()
    except Exception as e:
        print(f"[!] Info DB: {e}")

    print("[*] Menjalankan server backend Flask (port 5050)...")
    flask_env = os.environ.copy()
    flask_env['PORT'] = '5050'
    flask_proc = subprocess.Popen(
        [sys.executable, APP_FILE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=BASE_DIR,
        env=flask_env
    )

    time.sleep(1.5)

    print("[*] Menghubungkan ke Ngrok Tunnel (Port 5050)...")
    ngrok_proc = subprocess.Popen(
        [ngrok_bin, 'http', '5050', '--log=stdout'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Ambil URL publik dari Ngrok Local API (http://127.0.0.1:4040/api/tunnels)
    public_url = None
    start_time = time.time()
    while time.time() - start_time < 15:
        time.sleep(1)
        try:
            req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels")
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                tunnels = data.get('tunnels', [])
                for t in tunnels:
                    if t.get('proto') == 'https':
                        public_url = t.get('public_url')
                        break
                if public_url:
                    break
        except Exception:
            continue

    if not public_url:
        print("\n[!] Gagal mendapatkan link Ngrok dalam 15 detik.")
        flask_proc.terminate()
        ngrok_proc.terminate()
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    copied = copy_to_clipboard(public_url)

    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("      LAB CYBERSECURITY - SERVER PUBLIK NGROK AKTIF (BEBAS BLOKIR) ")
    print("=" * 70)
    print("\n  >> LINK PUBLIK UNTUK MAHASISWA:")
    print(f"     \033[1;32m{public_url}\033[0m")
    print("-" * 70)
    if copied:
        print("  [OK] LINK TELAH OTOMATIS DISALIN KE CLIPBOARD!")
        print("  -> Tinggal buka WhatsApp / Discord dan tekan [Ctrl + V] untuk kirim.")
    else:
        print("  -> Silakan salin link di atas untuk dibagikan ke mahasiswa.")
    print("-" * 70)
    print("  Akses Lokal Anda (Mentor):  http://127.0.0.1:5050")
    print("=" * 70)
    print("\n  [KELEBIHAN NGROK]")
    print("  - Domain *.ngrok-free.app 100% bebas dari blokir DNS provider Indonesia.")
    print("  - Mahasiswa bisa langsung klik link tanpa perlu ganti DNS/VPN.")
    print("  - Biarkan jendela ini tetap terbuka selama kelas mentoring.")
    print("  - Tekan [Ctrl + C] untuk mematikan server.")
    print("=" * 70)

    try:
        while True:
            time.sleep(1)
            if flask_proc.poll() is not None or ngrok_proc.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n\n[*] Menghentikan server dan menutup tunnel Ngrok...")
    finally:
        flask_proc.terminate()
        ngrok_proc.terminate()
        flask_proc.wait()
        ngrok_proc.wait()
        print("[+] Server berhasil dimatikan dengan aman.")
        time.sleep(1)

if __name__ == '__main__':
    main()
