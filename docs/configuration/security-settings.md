# 🔒 إعدادات الأمان

## تشفير البيانات

### إعداد HTTPS
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### حماية قاعدة البيانات
```bash
# PostgreSQL Security
# في pg_hba.conf
local   wifi_manager    wifi_manager                     md5
host    wifi_manager    wifi_manager    127.0.0.1/32      md5

# تشفير كلمات المرور
ALTER USER wifi_manager WITH ENCRYPTED PASSWORD 'secure_password';

# إعداد SSL
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

## جدار الحماية

### UFW Configuration
```bash
# السماح بالمنافذ الأساسية فقط
ufw default deny incoming
ufw default allow outgoing

ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5432/tcp  # PostgreSQL (محلي فقط)

ufw enable
```

### iptables Rules
```bash
# حماية من DDoS
iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT

# حماية من Port Scanning
iptables -A INPUT -m state --state NEW -p tcp --tcp-flags ALL ALL -j DROP
iptables -A INPUT -m state --state NEW -p tcp --tcp-flags ALL NONE -j DROP
```

## مراقبة الأمان

### تسجيل الأحداث الأمنية
```python
import logging
from datetime import datetime

security_logger = logging.getLogger('security')
security_handler = logging.FileHandler('/var/log/wifi-manager/security.log')
security_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
security_logger.addHandler(security_handler)

def log_security_event(event_type, user_id, ip_address, details):
    security_logger.warning(f"{event_type} - User: {user_id}, IP: {ip_address}, Details: {details}")
```

### كشف التسلل
```bash
# تثبيت fail2ban
sudo apt install fail2ban

# إعداد jail لـ WiFi Manager
cat > /etc/fail2ban/jail.d/wifi-manager.conf << EOF
[wifi-manager]
enabled = true
port = 80,443
filter = wifi-manager
logpath = /var/log/wifi-manager/access.log
maxretry = 5
bantime = 3600
EOF
```