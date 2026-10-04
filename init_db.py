import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vulnerable_lab.db")

def init_db():
    print(f"[*] Initializing database at {DB_FILE}...")
    
    # Remove old database if exists to ensure clean state
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("[-] Old database removed.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Users Table (Authentication & SQLi Login Bypass target)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL,
        api_token TEXT NOT NULL
    )
    ''')

    users_data = [
        ('admin', 'P@ssw0rdAdmin2026!', 'admin@cyberlab.local', 'administrator', 'tok_adm_9948271038472910'),
        ('sec_analyst', 'CyberSec#2026', 'analyst@cyberlab.local', 'analyst', 'tok_ana_1182749201948271'),
        ('johndoe', 'password123', 'john.doe@cyberlab.local', 'employee', 'tok_emp_4492817294829104'),
        ('alice_hr', 'Sunshine2024!', 'alice@cyberlab.local', 'hr_manager', 'tok_hr_7729104829184720'),
        ('bob_finance', 'MoneyMoney123', 'bob@cyberlab.local', 'finance', 'tok_fin_8829104827194012')
    ]
    cursor.executemany('''
    INSERT INTO users (username, password, email, role, api_token)
    VALUES (?, ?, ?, ?, ?)
    ''', users_data)

    # 2. Customers Table (Sensitive data target for SQLi UNION extraction)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        credit_card TEXT NOT NULL,
        cvv TEXT NOT NULL,
        balance REAL NOT NULL
    )
    ''')

    customers_data = [
        ('Bambang Soedarmono', 'bambang.s@corporate.id', '4532-8921-3849-1029', '412', 15450000.00),
        ('Siti Nurhaliza', 'siti.n@techfirm.com', '5421-9982-1204-7743', '881', 8200000.00),
        ('Michael Tanuwidjaja', 'm.tan@capital.sg', '3782-8224-9102-4412', '120', 45000000.00),
        ('Dewi Lestari', 'dewi.lestari@finance.co.id', '4012-7721-9940-2819', '593', 3120000.00),
        ('FLAG_HOLD_VIP', 'flag@ctf.internal', 'FLAG{SQLI_DATA_LEAK_SUCCESS_2026}', '000', 99999999.00)
    ]
    cursor.executemany('''
    INSERT INTO customers (full_name, email, credit_card, cvv, balance)
    VALUES (?, ?, ?, ?, ?)
    ''', customers_data)

    # 3. Products Table (Search catalog target for SQL Injection)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT NOT NULL
    )
    ''')

    products_data = [
        ('Firewall Appliance X-100', 'Hardware', 1500.00, 'Next-gen enterprise hardware firewall for perimeter defense.'),
        ('EDR Endpoint Sensor License', 'Software', 45.00, 'Real-time endpoint behavioral detection and response agent.'),
        ('Cybersecurity Awareness Training Kit', 'Education', 299.00, 'Complete phishing and security simulation module for staff.'),
        ('Hardware Security Key (FIDO2)', 'Hardware', 55.00, 'Biometric hardware token supporting WebAuthn and passwordless login.'),
        ('SIEM Log Ingestion Connector', 'Software', 850.00, 'High-throughput Syslog and telemetry parsing utility for SOC.')
    ]
    cursor.executemany('''
    INSERT INTO products (name, category, price, description)
    VALUES (?, ?, ?, ?)
    ''', products_data)

    # 4. Comments Table (Target for Stored XSS)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    comments_data = [
        ('Auditor SOC', 'Sistem firewall telah lolos audit triwulan I. Mohon pertahankan kepatuhan.'),
        ('IT Support', 'Maintenance server dijadwalkan pada hari Sabtu pukul 22:00 WIB.'),
        ('Anonymous Guest', 'Halo admin, tampilan portal SOC ini sangat informatif!')
    ]
    cursor.executemany('''
    INSERT INTO comments (author, comment)
    VALUES (?, ?)
    ''', comments_data)

    # 5. Secret Flags / System Config Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        secret_value TEXT NOT NULL
    )
    ''')

    secrets_data = [
        ('MASTER_FLAG', 'FLAG{CYBER_FASTTRACK_MENTORING_MASTER_2026}'),
        ('JWT_SECRET_KEY', 'super_secret_signing_key_never_share_992144'),
        ('DATABASE_ROOT_BACKUP', 's3://cyberlab-backup-vault/production_2026.sql')
    ]
    cursor.executemany('''
    INSERT INTO secrets (name, secret_value)
    VALUES (?, ?)
    ''', secrets_data)

    conn.commit()
    conn.close()
    print("[+] Database successfully initialized with all mock data and CTF flags!")

if __name__ == '__main__':
    init_db()
