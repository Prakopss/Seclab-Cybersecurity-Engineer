#!/bin/sh
set -e

mkdir -p /etc/nginx/ssl

# Generate Self-Signed SSL Certificate if not already present
if [ ! -f /etc/nginx/ssl/server.crt ] || [ ! -f /etc/nginx/ssl/server.key ]; then
    echo "[*] Generating Self-Signed SSL Certificate for CyberLab HTTPS (Port 443)..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/server.key \
        -out /etc/nginx/ssl/server.crt \
        -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FastTrack Cyber Mentoring/OU=Security Lab/CN=localhost"
    echo "[+] SSL Certificate successfully created!"
fi

echo "[+] Starting Nginx Reverse Proxy (HTTP on Port 80 & HTTPS on Port 443)..."
exec nginx -g "daemon off;"
