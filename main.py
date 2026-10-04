import os
import init_db
from app import app

# Pastikan database SQLite terinisialisasi di Replit
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vulnerable_lab.db")
if not os.path.exists(db_path):
    print("[*] Menginisialisasi database SQLite di Replit...")
    init_db.init_db()

if __name__ == "__main__":
    # Replit mengekspos web melalui host 0.0.0.0 dan port 8080
    port = int(os.environ.get("PORT", 8080))
    print(f"[*] CyberLab Web Application aktif di Replit pada port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)

