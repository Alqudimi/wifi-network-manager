# دليل النشر والتشغيل

هذا الدليل يوضح كيفية نشر وتشغيل نظام إدارة شبكات Wi-Fi في بيئة الإنتاج.

## متطلبات الخادم

### الحد الأدنى للمتطلبات
- **نظام التشغيل**: Ubuntu 20.04+ أو CentOS 8+
- **المعالج**: 2 CPU cores
- **الذاكرة**: 4GB RAM
- **التخزين**: 20GB مساحة فارغة
- **الشبكة**: اتصال إنترنت مستقر

### المتطلبات الموصى بها
- **نظام التشغيل**: Ubuntu 22.04 LTS
- **المعالج**: 4+ CPU cores
- **الذاكرة**: 8GB+ RAM
- **التخزين**: 50GB+ SSD
- **الشبكة**: اتصال إنترنت عالي السرعة

## إعداد الخادم

### 1. تحديث النظام
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. تثبيت Docker و Docker Compose
```bash
# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# إضافة المستخدم لمجموعة docker
sudo usermod -aG docker $USER

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# إعادة تسجيل الدخول لتفعيل التغييرات
logout
```

### 3. إعداد Firewall
```bash
# تفعيل UFW
sudo ufw enable

# السماح بالمنافذ المطلوبة
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 5000  # API (اختياري للتطوير)

# عرض حالة Firewall
sudo ufw status
```

## نشر التطبيق

### 1. استنساخ المشروع
```bash
cd /opt
sudo git clone <repository-url> wifi-network-manager
sudo chown -R $USER:$USER wifi-network-manager
cd wifi-network-manager
```

### 2. إعداد متغيرات البيئة

#### إعداد الواجهة الخلفية
```bash
cd backend
cp .env.example .env
```

قم بتحرير ملف `.env`:
```env
# إعدادات الأمان
SECRET_KEY=your-super-secret-key-change-in-production-$(openssl rand -hex 32)
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production-$(openssl rand -hex 32)

# إعدادات قاعدة البيانات
DATABASE_URL=postgresql://wifi_user:secure_password_2024@postgres:5432/wifi_network_db

# إعدادات Redis
REDIS_URL=redis://redis:6379/0

# إعدادات البيئة
FLASK_ENV=production
PORT=5000
```

#### إعداد الواجهة الأمامية
```bash
cd ../frontend
cp .env.example .env
```

قم بتحرير ملف `.env`:
```env
VITE_API_BASE_URL=https://yourdomain.com/api
```

### 3. إعداد Docker Compose للإنتاج
```bash
cd ..
cp docker-compose.yml docker-compose.prod.yml
```

قم بتحرير `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: wifi-postgres
    environment:
      POSTGRES_DB: wifi_network_db
      POSTGRES_USER: wifi_user
      POSTGRES_PASSWORD: secure_password_2024
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - wifi-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: wifi-redis
    volumes:
      - redis_data:/data
    networks:
      - wifi-network
    restart: unless-stopped
    command: redis-server --appendonly yes

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: wifi-backend
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=postgresql://wifi_user:secure_password_2024@postgres:5432/wifi_network_db
      - REDIS_URL=redis://redis:6379/0
      - FLASK_ENV=production
      - PORT=5000
    depends_on:
      - postgres
      - redis
    networks:
      - wifi-network
    restart: unless-stopped
    volumes:
      - ./backend/uploads:/app/uploads

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: wifi-frontend
    depends_on:
      - backend
    networks:
      - wifi-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: wifi-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - frontend
      - backend
    networks:
      - wifi-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  wifi-network:
    driver: bridge
```

### 4. إعداد Nginx
```bash
mkdir -p nginx/ssl nginx/logs
```

إنشاء ملف `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }

    upstream frontend {
        server frontend:80;
    }

    # إعادة توجيه HTTP إلى HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # إعدادات HTTPS
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # إعدادات SSL
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # إعدادات الأمان
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # API routes
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # إعدادات التخزين المؤقت
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 5. الحصول على شهادة SSL
```bash
# تثبيت Certbot
sudo apt install certbot

# الحصول على شهادة SSL
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# نسخ الشهادات
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*
```

### 6. تشغيل التطبيق
```bash
# بناء وتشغيل الحاويات
docker-compose -f docker-compose.prod.yml up -d --build

# التحقق من حالة الحاويات
docker-compose -f docker-compose.prod.yml ps

# عرض السجلات
docker-compose -f docker-compose.prod.yml logs -f
```

## إعداد النسخ الاحتياطي

### 1. نسخ احتياطي لقاعدة البيانات
```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/opt/backups/wifi-db"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="wifi-postgres"

mkdir -p $BACKUP_DIR

# إنشاء نسخة احتياطية
docker exec $CONTAINER_NAME pg_dump -U wifi_user wifi_network_db > $BACKUP_DIR/backup_$DATE.sql

# الاحتفاظ بآخر 30 نسخة احتياطية فقط
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete

echo "تم إنشاء النسخة الاحتياطية: backup_$DATE.sql"
```

### 2. جدولة النسخ الاحتياطي
```bash
# إضافة مهمة cron للنسخ الاحتياطي اليومي
crontab -e

# إضافة السطر التالي (نسخة احتياطية يومياً في الساعة 2:00 صباحاً)
0 2 * * * /opt/wifi-network-manager/backup-db.sh
```

## المراقبة والصيانة

### 1. مراقبة السجلات
```bash
# عرض سجلات جميع الخدمات
docker-compose -f docker-compose.prod.yml logs -f

# عرض سجلات خدمة محددة
docker-compose -f docker-compose.prod.yml logs -f backend

# عرض آخر 100 سطر من السجلات
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### 2. مراقبة الأداء
```bash
# عرض استخدام الموارد
docker stats

# عرض مساحة القرص
df -h

# عرض استخدام الذاكرة
free -h

# عرض العمليات النشطة
top
```

### 3. تحديث التطبيق
```bash
# سحب آخر التحديثات
git pull origin main

# إعادة بناء وتشغيل الحاويات
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# تنظيف الصور القديمة
docker image prune -f
```

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. فشل في الاتصال بقاعدة البيانات
```bash
# التحقق من حالة PostgreSQL
docker-compose -f docker-compose.prod.yml logs postgres

# إعادة تشغيل قاعدة البيانات
docker-compose -f docker-compose.prod.yml restart postgres
```

#### 2. مشاكل في الذاكرة
```bash
# التحقق من استخدام الذاكرة
docker stats --no-stream

# إعادة تشغيل الخدمات
docker-compose -f docker-compose.prod.yml restart
```

#### 3. مشاكل SSL
```bash
# التحقق من صحة الشهادة
openssl x509 -in nginx/ssl/cert.pem -text -noout

# تجديد شهادة SSL
sudo certbot renew
```

## الأمان

### 1. تحديث كلمات المرور الافتراضية
- قم بتغيير كلمة مرور المدير الافتراضي فور التثبيت
- استخدم كلمات مرور قوية لقاعدة البيانات
- قم بتحديث مفاتيح التشفير بانتظام

### 2. إعدادات Firewall
```bash
# السماح فقط بالمنافذ المطلوبة
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 3. مراقبة الأمان
```bash
# مراقبة محاولات تسجيل الدخول الفاشلة
sudo tail -f /var/log/auth.log

# مراقبة سجلات Nginx
sudo tail -f nginx/logs/access.log
sudo tail -f nginx/logs/error.log
```

## الصيانة الدورية

### أسبوعياً
- مراجعة السجلات للأخطاء
- التحقق من مساحة القرص المتاحة
- مراقبة أداء النظام

### شهرياً
- تحديث النظام والحزم
- مراجعة النسخ الاحتياطية
- تنظيف الملفات المؤقتة

### سنوياً
- تجديد شهادات SSL
- مراجعة إعدادات الأمان
- تحديث كلمات المرور

---

هذا الدليل يوفر الأساسيات لنشر وإدارة نظام إدارة شبكات Wi-Fi في بيئة الإنتاج. للحصول على مساعدة إضافية، يرجى مراجعة الوثائق الأخرى أو التواصل مع فريق الدعم.

