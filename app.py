import os
import re
import sqlite3
import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, send_from_directory
import datetime

app = Flask(__name__)
app.secret_key = "cyberlab_insecure_mentoring_session_key_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "vulnerable_lab.db")
SENSITIVE_DIR = os.path.join(BASE_DIR, "sensitive_files")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure DB exists on app startup
if not os.path.exists(DB_FILE):
    import init_db
    init_db.init_db()

# -------------------------------------------------------------
# 0. DASHBOARD & UTILITY ROUTES
# -------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/reset-db')
def reset_db_route():
    import init_db
    init_db.init_db()
    flash('Database berhasil di-reset kembali ke status awal dengan dummy data & flags!', 'success')
    return redirect(url_for('index'))

# -------------------------------------------------------------
# 1. MODULE 1: SQL INJECTION (SQLi)
# -------------------------------------------------------------
@app.route('/sqli')
def sqli_home():
    tab = request.args.get('tab', 'login')
    return render_template('sqli.html', active_page='sqli', active_tab=tab)

@app.route('/sqli/login', methods=['POST'])
def sqli_login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    waf_enabled = request.form.get('waf_enabled') == 'on'

    executed_query = ""
    error_msg = None
    user_data = None

    # Optional naive WAF: only checks uppercase 'OR' and 'AND'
    if waf_enabled:
        if " OR " in username or " AND " in username:
            error_msg = "[WAF BLOCKED]: Query mengandung kata kunci SQL terlarang (OR / AND dalam huruf kapital)!"
            return render_template(
                'sqli.html',
                active_page='sqli',
                active_tab='login',
                username_val=username,
                password_val=password,
                waf_enabled=waf_enabled,
                error_msg=error_msg
            )

    # Intentionally vulnerable raw string interpolation
    executed_query = f"SELECT id, username, password, email, role, api_token FROM users WHERE username = '{username}' AND password = '{password}'"
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(executed_query)
        row = cursor.fetchone()
        conn.close()

        if row:
            user_data = {
                'id': row['id'],
                'username': row['username'],
                'role': row['role'],
                'email': row['email'],
                'api_token': row['api_token']
            }
            flash(f"Otentikasi Berhasil! Selamat datang, {user_data['username']}.", "success")
        else:
            flash("Login Gagal: Kredensial tidak valid.", "error")
    except Exception as e:
        error_msg = str(e)

    return render_template(
        'sqli.html',
        active_page='sqli',
        active_tab='login',
        username_val=username,
        password_val=password,
        waf_enabled=waf_enabled,
        executed_query=executed_query,
        error_msg=error_msg,
        user_data=user_data
    )

@app.route('/sqli/search', methods=['GET'])
def sqli_search():
    q = request.args.get('q', '')
    search_sql = f"SELECT id, name, category, price, description FROM products WHERE name LIKE '%{q}%'"
    search_results = []
    search_error = None

    if q:
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(search_sql)
            search_results = cursor.fetchall()
            conn.close()
        except Exception as e:
            search_error = str(e)

    return render_template(
        'sqli.html',
        active_page='sqli',
        active_tab='union',
        search_query=q,
        search_sql=search_sql,
        search_results=search_results,
        search_error=search_error
    )

# -------------------------------------------------------------
# 2. MODULE 2: CROSS-SITE SCRIPTING (XSS)
# -------------------------------------------------------------
@app.route('/xss')
def xss_home():
    tab = request.args.get('tab', 'reflected')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, author, comment, created_at FROM comments ORDER BY id DESC")
    comments = cursor.fetchall()
    conn.close()
    return render_template('xss.html', active_page='xss', active_tab=tab, comments=comments)

@app.route('/xss/reflected', methods=['GET'])
def xss_reflected():
    query = request.args.get('q')
    filter_enabled = request.args.get('filter_enabled') == 'on'
    blocked_by_filter = False

    if query is not None and filter_enabled:
        # Naive WAF: only checks lowercase 'script', easily bypassed with <sCrIpt> or <img>
        if "script" in query:
            blocked_by_filter = True

    return render_template(
        'xss.html',
        active_page='xss',
        active_tab='reflected',
        query=query,
        filter_enabled=filter_enabled,
        blocked_by_filter=blocked_by_filter
    )

@app.route('/xss/stored', methods=['POST'])
def xss_stored():
    author = request.form.get('author', 'Anonymous')
    comment = request.form.get('comment', '')

    if comment:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (author, comment) VALUES (?, ?)", (author, comment))
        conn.commit()
        conn.close()
        flash("Catatan insiden berhasil dipublikasikan ke papan pesan!", "success")

    return redirect(url_for('xss_home', tab='stored'))

@app.route('/xss/clear', methods=['GET'])
def xss_clear():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comments")
    conn.commit()
    conn.close()
    flash("Semua catatan dan riwayat komentar telah dikosongkan.", "info")
    return redirect(url_for('xss_home', tab='stored'))

# -------------------------------------------------------------
# 3. MODULE 3: LOCAL FILE INCLUSION (LFI)
# -------------------------------------------------------------
@app.route('/lfi', methods=['GET'])
def lfi_view():
    filename = request.args.get('file', 'about_portal.txt')
    file_content = ""
    error_msg = None

    # Intentionally vulnerable path concatenation
    resolved_path = os.path.abspath(os.path.join(SENSITIVE_DIR, filename))

    try:
        if os.path.exists(resolved_path):
            if os.path.isdir(resolved_path):
                error_msg = f"Path '{resolved_path}' adalah direktori, bukan file reguler."
            else:
                with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
        else:
            error_msg = f"File tidak ditemukan di path: {resolved_path}"
    except Exception as e:
        error_msg = f"Gagal membaca file: {str(e)}"

    return render_template(
        'lfi.html',
        active_page='lfi',
        filename=filename,
        base_dir=SENSITIVE_DIR,
        resolved_path=resolved_path,
        file_content=file_content,
        error_msg=error_msg
    )

# -------------------------------------------------------------
# 4. MODULE 4: OS COMMAND INJECTION (RCE)
# -------------------------------------------------------------
@app.route('/rce', methods=['GET', 'POST'])
def rce_view():
    target = ""
    cmd_output = ""
    executed_command = ""
    error_msg = None
    waf_enabled = False
    waf_blocked = False

    if request.method == 'POST':
        target = request.form.get('target', '').strip()
        waf_enabled = request.form.get('waf_enabled') == 'on'

        if waf_enabled:
            # Naive filter: only blocks semicolon and double ampersand
            if ";" in target or "&&" in target:
                waf_blocked = True
                return render_template(
                    'rce.html',
                    active_page='rce',
                    target=target,
                    waf_enabled=waf_enabled,
                    waf_blocked=True
                )

        if target:
            # Determine OS ping flag
            ping_flag = "-n 2" if os.name == 'nt' else "-c 2"
            executed_command = f"ping {ping_flag} {target}"

            try:
                # Intentionally vulnerable shell execution
                cmd_output = subprocess.check_output(
                    executed_command,
                    shell=True,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=8
                )
            except subprocess.TimeoutExpired:
                error_msg = "Command timed out (lebih dari 8 detik)."
            except subprocess.CalledProcessError as e:
                cmd_output = e.output if e.output else str(e)
            except Exception as e:
                error_msg = str(e)

    return render_template(
        'rce.html',
        active_page='rce',
        target=target,
        executed_command=executed_command,
        cmd_output=cmd_output,
        error_msg=error_msg,
        waf_enabled=waf_enabled,
        waf_blocked=waf_blocked
    )

# -------------------------------------------------------------
# 5. MODULE 5: FILTER & WAF BYPASS PLAYGROUND
# -------------------------------------------------------------
@app.route('/waf-bypass')
def waf_bypass_home():
    return render_template('filter_bypass.html', active_page='waf')

@app.route('/waf-bypass/case', methods=['POST'])
def waf_case():
    payload = request.form.get('input_payload', '')
    # Flaw: Only checks lowercase "script"
    is_blocked = "script" in payload
    return render_template(
        'filter_bypass.html',
        active_page='waf',
        case_input=payload,
        case_blocked=is_blocked,
        case_result="BLOCKED" if is_blocked else "ALLOWED"
    )

@app.route('/waf-bypass/recursive', methods=['POST'])
def waf_recursive():
    payload = request.form.get('input_payload', '')
    # Flaw: Non-recursive single replace
    sanitized = payload.replace("<script>", "").replace("</script>", "")
    return render_template(
        'filter_bypass.html',
        active_page='waf',
        rec_input=payload,
        rec_result=sanitized
    )

@app.route('/waf-bypass/tag', methods=['POST'])
def waf_tag():
    payload = request.form.get('input_payload', '')
    # Flaw: Blacklists <script>, but ignores <img>, <svg>, <body>
    is_blocked = bool(re.search(r'<\s*script', payload, re.IGNORECASE))
    return render_template(
        'filter_bypass.html',
        active_page='waf',
        tag_input=payload,
        tag_blocked=is_blocked,
        tag_result="BLOCKED" if is_blocked else "ALLOWED"
    )

@app.route('/waf-bypass/cmd', methods=['POST'])
def waf_cmd():
    cmd = request.form.get('input_payload', '')
    # Flaw: Blacklists ; and &&, forgets | and ||
    is_blocked = (";" in cmd) or ("&&" in cmd)
    output = ""
    if not is_blocked and cmd:
        try:
            output = subprocess.check_output(
                cmd,
                shell=True,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=5
            )
        except Exception as e:
            output = str(e)

    return render_template(
        'filter_bypass.html',
        active_page='waf',
        cmd_input=cmd,
        cmd_blocked=is_blocked,
        cmd_result=output if not is_blocked else None
    )

# -------------------------------------------------------------
# 6. MODULE 6: NETWORK SNIFFING & SSL HELPER
# -------------------------------------------------------------
@app.route('/network-lab')
def network_lab():
    return render_template('network_lab.html', active_page='network')

@app.route('/network-lab/login-test', methods=['POST'])
def network_login_test():
    username = request.form.get('sniff_user', '')
    password = request.form.get('sniff_pass', '')
    flash(f"[Simulasi Berhasil] Data POST terkirim: Username '{username}' & Password '{password}'. Paket ini sekarang tercatat secara plaintext di Wireshark!", "info")
    return redirect(url_for('network_lab'))

# -------------------------------------------------------------
# 7. MODULE 7: UNRESTRICTED FILE UPLOAD
# -------------------------------------------------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    filter_enabled = False
    if request.method == 'POST':
        filter_enabled = request.form.get('filter_enabled') == 'on'
        
        if 'file' not in request.files:
            flash("Tidak ada file yang dipilih!", "error")
            return redirect(url_for('upload_file'))
            
        file = request.files['file']
        if file.filename == '':
            flash("Nama file kosong!", "error")
            return redirect(url_for('upload_file'))
            
        filename = file.filename
        
        # Naive Blacklist Filter (Hanya melarang .php)
        if filter_enabled:
            if filename.lower().endswith('.php'):
                flash(f"[WAF Blocked] File '{filename}' ditolak! Ekstensi .php dilarang oleh filter.", "error")
                return redirect(url_for('upload_file'))
        
        # VULNERABILITY: Raw filename saved without secure_filename() whitelisting
        save_path = os.path.join(UPLOAD_DIR, filename)
        file.save(save_path)
        
        direct_url = url_for('static', filename='uploads/' + filename)
        flash(f"File '{filename}' berhasil diunggah! Akses langsung di: <a href='{direct_url}' target='_blank' class='alert-link'>{direct_url}</a>", "success")
        return redirect(url_for('upload_file'))
        
    # Ambil daftar file di direktori uploads
    uploaded_files = []
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            p = os.path.join(UPLOAD_DIR, f)
            if os.path.isfile(p):
                stat = os.stat(p)
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                uploaded_files.append({
                    'name': f,
                    'size': stat.st_size,
                    'time': mtime
                })
                
    return render_template('upload.html', active_page='upload', uploaded_files=uploaded_files, filter_enabled=filter_enabled)

@app.route('/upload/clear', methods=['POST'])
def upload_clear():
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            p = os.path.join(UPLOAD_DIR, f)
            if os.path.isfile(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
    flash("Seluruh file upload berhasil dibersihkan!", "info")
    return redirect(url_for('upload_file'))

# -------------------------------------------------------------
# 8. MODULE 8: ROBOTS.TXT (RECONNAISSANCE & INFO DISCLOSURE)
# -------------------------------------------------------------
@app.route('/robots.txt')
def robots_txt():
    robots_content = """# robots.txt for CyberLab Security Training Portal
# Crawlers: Please respect disallowed paths for internal security.

User-agent: *
Disallow: /admin-secret-vault/
Disallow: /backup/
Disallow: /sensitive_files/
Disallow: /static/uploads/

# Reconnaissance Flag:
# FLAG{ROBOTS_TXT_RECON_DISCOVERY_2026}
"""
    return Response(robots_content, mimetype='text/plain')

@app.route('/admin-secret-vault/')
def admin_secret_vault():
    vault_html = """
    <div style='background-color:#0d1117; color:#39ff14; font-family:monospace; padding:30px; border-radius:8px; margin:40px;'>
        <h2><i class='fa-solid fa-lock'></i> [CONFIDENTIAL] ADMIN SECRET VAULT</h2>
        <hr style='border-color:#30363d;'>
        <p>Selamat! Anda berhasil menemukan direktori rahasia melalui analisis <code>/robots.txt</code>.</p>
        <p><strong>RECON MASTER FLAG:</strong> <span style='background:#161b22; padding:6px 12px; border:1px solid #39ff14; color:#fff;'>FLAG{ADMIN_VAULT_ROBOTS_DISCOVERY_8892}</span></p>
        <br>
        <a href='/' style='color:#58a6ff; text-decoration:none;'>&larr; Kembali ke Dashboard</a>
    </div>
    """
    return vault_html

# -------------------------------------------------------------
# 9. MODULE 9: DIREKTORI TERBUKA (OPEN DIRECTORY / DIRECTORY LISTING)
# -------------------------------------------------------------
@app.route('/backup/')
@app.route('/backup')
def open_directory_backup():
    is_patched = session.get('backup_patched', False)
    
    # Cek query param jika ingin switch cepat via URL (?patch=1 atau ?patch=0)
    if 'patch' in request.args:
        is_patched = request.args.get('patch') == '1'
        session['backup_patched'] = is_patched

    files_list = []
    if not is_patched and os.path.exists(BACKUP_DIR):
        for f in os.listdir(BACKUP_DIR):
            p = os.path.join(BACKUP_DIR, f)
            if os.path.isfile(p):
                stat = os.stat(p)
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                size_str = f"{stat.st_size} B"
                if stat.st_size > 1024:
                    size_str = f"{stat.st_size / 1024:.1f} KB"
                files_list.append({
                    'name': f,
                    'size': size_str,
                    'modified': mtime
                })
                
    status_code = 403 if is_patched else 200
    return render_template('open_directory.html', active_page='open_dir', files=files_list, is_patched=is_patched), status_code

@app.route('/backup/toggle-patch', methods=['POST'])
def toggle_backup_patch():
    current = session.get('backup_patched', False)
    session['backup_patched'] = not current
    status_msg = "[PATCH AKTIF] Direktori /backup/ sekarang terkunci rapat dengan HTTP 403 Forbidden (autoindex off)!" if session['backup_patched'] else "[MODE RENTAN] Direktori /backup/ kembali dibuka untuk simulasi mahasiswa."
    flash(status_msg, "success" if session['backup_patched'] else "warning")
    return redirect(url_for('open_directory_backup'))

@app.route('/backup/<path:filename>')
def download_backup_file(filename):
    if session.get('backup_patched', False):
        return Response("<div style='background:#0d1117; color:#ff4d4d; font-family:monospace; padding:30px;'><h1>403 Forbidden</h1><p>Akses ke file cadangan diblokir oleh kebijakan keamanan server (Direct File Access Denied).</p></div>", status=403, mimetype='text/html')
    return send_from_directory(BACKUP_DIR, filename, as_attachment=False)

if __name__ == '__main__':
    # Default local dev server di port 5050 agar tidak bentrok dengan live server lain
    port = int(os.environ.get('PORT', 5050))
    print(f"[*] Memulai CyberLab Web Application pada http://0.0.0.0:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)
