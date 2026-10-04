import os
import sys
import re
import time
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_FILE = os.path.join(BASE_DIR, 'app.py')

def find_cloudflared():
    try:
        res = subprocess.run(['where', 'cloudflared'], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return 'cloudflared'
    except Exception:
        pass

    standard_paths = [
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
        os.path.expanduser(r"~\cloudflared.exe"),
    ]
    for p in standard_paths:
        if os.path.exists(p):
            return p
    return None

def copy_to_clipboard(text):
    try:
        subprocess.run('clip', input=text, text=True, check=True)
        return True
    except Exception:
        return False

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("   JUNIOR CYBERSECURITY ENGINEER LAB - PUBLIC SERVER LAUNCHER")
    print("=" * 70)
    print("\n[*] Menyiapkan database lab...")

    try:
        from init_db import init_db
        init_db()
    except Exception as e:
        print(f"[!] Info DB: {e}")

    cloudflared_bin = find_cloudflared()
    if not cloudflared_bin:
        print("\n[!] ERROR: cloudflared.exe tidak ditemukan di komputer.")
        print("[!] Silakan unduh dari https://github.com/cloudflare/cloudflared/releases")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

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

    print("[*] Menghubungkan ke Cloudflare Public Tunnel (HTTPS)...")
    tunnel_cmd = [cloudflared_bin, 'tunnel', '--url', 'http://127.0.0.1:5050']
    tunnel_proc = subprocess.Popen(
        tunnel_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    public_url = None
    start_time = time.time()
    
    while time.time() - start_time < 20:
        line = tunnel_proc.stdout.readline()
        if not line:
            break
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if match:
            public_url = match.group(0)
            break

    if not public_url:
        print("\n[!] Gagal mendeteksi link Cloudflare dalam 20 detik.")
        flask_proc.terminate()
        tunnel_proc.terminate()
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    copied = copy_to_clipboard(public_url)

    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("   LAB JUNIOR CYBERSECURITY ENGINEER - SERVER PUBLIK SUDAH AKTIF!  ")
    print("=" * 70)
    print("\n  >> LINK PUBLIK UNTUK MAHASISWA:")
    print(f"     \033[1;32m{public_url}\033[0m")
    print("-" * 70)
    if copied:
        print("  [OK] LINK TELAH OTOMATIS DISALIN KE CLIPBOARD!")
        print("  -> Tinggal buka WhatsApp / Discord dan tekan [Ctrl + V] untuk kirim.")
    else:
        print("  -> Silakan salin (copy) link di atas untuk dibagikan ke mahasiswa.")
    print("-" * 70)
    print("  Akses Lokal Anda (Mentor):  http://127.0.0.1:5050")
    print("=" * 70)
    print("\n  [PANDUAN]")
    print("  - Mahasiswa bisa langsung membuka link di atas dari browser apa saja.")
    print("  - Tidak perlu VPN atau pengaturan port forwarding.")
    print("  - Biarkan jendela terminal ini tetap terbuka selama kelas berlangsung.")
    print("  - Tekan [Ctrl + C] untuk mematikan server jika sudah selesai.")
    print("=" * 70)

    try:
        while True:
            time.sleep(1)
            if flask_proc.poll() is not None or tunnel_proc.poll() is not None:
                print("\n[!] Salah satu proses berhenti.")
                break
    except KeyboardInterrupt:
        print("\n\n[*] Menghentikan server dan menutup tunnel...")
    finally:
        flask_proc.terminate()
        tunnel_proc.terminate()
        flask_proc.wait()
        tunnel_proc.wait()
        print("[+] Server publik berhasil dimatikan dengan aman.")
        time.sleep(1)

if __name__ == '__main__':
    main()
