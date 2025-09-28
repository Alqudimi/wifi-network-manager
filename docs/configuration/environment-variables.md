# 🌍 متغيرات البيئة

## نظرة عامة

متغيرات البيئة تسمح بتخصيص إعدادات النظام دون تعديل الكود، وهي أساسية للنشر الآمن في بيئات الإنتاج.

## المتغيرات الأساسية

### الأمان والتشفير
```bash
# مفاتيح التشفير (مطلوبة)
SECRET_KEY=your-very-long-random-secret-key-here-32-chars-min
JWT_SECRET_KEY=your-jwt-secret-key-here-32-chars-min
WTF_CSRF_SECRET_KEY=your-csrf-secret-key-here

# طريقة توليد آمنة
openssl rand -hex 32
```

### قاعدة البيانات
```bash
# PostgreSQL (للإنتاج)
DATABASE_URL=postgresql://username:password@localhost:5432/wifi_manager

# SQLite (للتطوير)
DATABASE_URL=sqlite:///wifi_manager.db

# إعدادات Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_RECYCLE=3600
```

### خادم التطبيق
```bash
# إعدادات Flask
FLASK_ENV=production
FLASK_DEBUG=False
HOST=0.0.0.0
PORT=5000

# Workers للإنتاج
WORKERS=4
WORKER_CLASS=gevent
WORKER_CONNECTIONS=1000
```

## المتغيرات الاختيارية

### Redis والتخزين المؤقت
```bash
# Redis للجلسات والتخزين المؤقت
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300

# Celery للمهام المؤجلة
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### البريد الإلكتروني
```bash
# إعدادات SMTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@your-domain.com
```

### التسجيل والمراقبة
```bash
# مستوى التسجيل
LOG_LEVEL=INFO
LOG_FILE=/var/log/wifi-manager/app.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5

# مراقبة الأداء
ENABLE_PROFILING=False
SLOW_QUERY_THRESHOLD=0.5
```

## إعدادات الأمان المتقدمة

### JWT Configuration
```bash
# مدة صلاحية الرموز
JWT_ACCESS_TOKEN_EXPIRES=86400     # 24 ساعة
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 يوم

# إعدادات JWT متقدمة
JWT_ALGORITHM=HS256
JWT_ISSUER=wifi-manager-system
JWT_AUDIENCE=wifi-manager-users
```

### CORS والحماية
```bash
# CORS للتطوير
CORS_ORIGINS="*"

# CORS للإنتاج
CORS_ORIGINS="https://your-domain.com,https://admin.your-domain.com"

# Content Security Policy
CSP_DEFAULT_SRC="'self'"
CSP_SCRIPT_SRC="'self' 'unsafe-inline'"
CSP_STYLE_SRC="'self' 'unsafe-inline'"
```

## إعدادات أجهزة التوجيه

### المهلات الزمنية
```bash
# Router API Timeouts
ROUTER_CONNECTION_TIMEOUT=10
ROUTER_READ_TIMEOUT=5
ROUTER_MAX_RETRIES=3

# Connection Pool للراوترات
ROUTER_POOL_SIZE=5
ROUTER_POOL_TIMEOUT=30
```

### إعدادات خاصة بالأجهزة
```bash
# MikroTik
MIKROTIK_API_PORT=8728
MIKROTIK_API_SSL=False

# Ubiquiti
UBIQUITI_VERIFY_SSL=False
UBIQUITI_API_VERSION=v1

# Cisco
CISCO_SSH_PORT=22
CISCO_ENABLE_SECRET=your-enable-password
```

## ملف .env كامل

### مثال لبيئة الإنتاج
```bash
# ملف .env للإنتاج
# ===================

# الأمان (مطلوب)
SECRET_KEY=f7d8a9b2c3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0
JWT_SECRET_KEY=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
WTF_CSRF_SECRET_KEY=9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8

# قاعدة البيانات
DATABASE_URL=postgresql://wifi_mgr:SecurePass123@localhost:5432/wifi_manager_prod
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# الخادم
FLASK_ENV=production
FLASK_DEBUG=False
HOST=0.0.0.0
PORT=5000

# Redis
REDIS_URL=redis://localhost:6379/0

# البريد الإلكتروني
MAIL_SERVER=smtp.company.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=wifi-system@company.com
MAIL_PASSWORD=EmailAppPassword123

# التسجيل
LOG_LEVEL=INFO
LOG_FILE=/var/log/wifi-manager/app.log

# CORS (حدد النطاقات المسموحة)
CORS_ORIGINS=https://wifi.company.com,https://admin.company.com

# أجهزة التوجيه
ROUTER_CONNECTION_TIMEOUT=10
MIKROTIK_API_PORT=8728
```

### مثال لبيئة التطوير
```bash
# ملف .env للتطوير
# ===================

# الأمان (للتطوير فقط)
SECRET_KEY=dev-secret-key-not-for-production
JWT_SECRET_KEY=dev-jwt-key-not-for-production

# قاعدة البيانات
DATABASE_URL=sqlite:///wifi_manager_dev.db

# الخادم
FLASK_ENV=development
FLASK_DEBUG=True
HOST=127.0.0.1
PORT=5000

# التسجيل
LOG_LEVEL=DEBUG

# CORS (مفتوح للتطوير)
CORS_ORIGINS=*

# تعطيل إعدادات الإنتاج
REDIS_URL=
MAIL_SERVER=
```

## التحقق من المتغيرات

### سكريبت فحص الإعدادات
```python
#!/usr/bin/env python3
"""فحص صحة متغيرات البيئة"""

import os
import sys
from urllib.parse import urlparse

def check_environment_variables():
    """فحص المتغيرات المطلوبة"""
    
    # متغيرات مطلوبة
    required_vars = {
        'SECRET_KEY': 'مفتاح Flask السري',
        'JWT_SECRET_KEY': 'مفتاح JWT',
    }
    
    # متغيرات اختيارية مع قيم افتراضية
    optional_vars = {
        'DATABASE_URL': 'sqlite:///wifi_manager.db',
        'REDIS_URL': '',
        'LOG_LEVEL': 'INFO',
        'HOST': '127.0.0.1',
        'PORT': '5000'
    }
    
    errors = []
    warnings = []
    
    # فحص المتغيرات المطلوبة
    for var, desc in required_vars.items():
        value = os.environ.get(var)
        if not value:
            errors.append(f"❌ {var} غير موجود - {desc}")
        elif var.endswith('_KEY') and len(value) < 32:
            warnings.append(f"⚠️ {var} قصير جداً - يجب 32 حرف على الأقل")
        else:
            print(f"✅ {var} - موجود وصالح")
    
    # فحص المتغيرات الاختيارية
    for var, default in optional_vars.items():
        value = os.environ.get(var, default)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"ℹ️ {var} - سيتم استخدام القيمة الافتراضية")
    
    # فحص DATABASE_URL
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        try:
            parsed = urlparse(db_url)
            if parsed.scheme in ['postgresql', 'mysql', 'sqlite']:
                print(f"✅ DATABASE_URL - نوع قاعدة البيانات: {parsed.scheme}")
            else:
                warnings.append(f"⚠️ DATABASE_URL - نوع غير مدعوم: {parsed.scheme}")
        except Exception as e:
            errors.append(f"❌ DATABASE_URL - تنسيق خاطئ: {e}")
    
    # طباعة النتائج
    if errors:
        print("\n🚨 أخطاء يجب إصلاحها:")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print("\n⚠️ تحذيرات:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors and not warnings:
        print("\n🎉 جميع متغيرات البيئة صحيحة!")
    
    return len(errors) == 0

if __name__ == '__main__':
    success = check_environment_variables()
    sys.exit(0 if success else 1)
```

## أفضل الممارسات

### إدارة آمنة للمتغيرات
1. **لا تضع مفاتيح الإنتاج في Git**
2. **استخدم أدوات إدارة الأسرار** (HashiCorp Vault, AWS Secrets Manager)
3. **غيّر المفاتيح دورياً** (كل 90 يوم)
4. **استخدم مفاتيح مختلفة لكل بيئة**

### نصائح النشر
```bash
# استخدم systemd لتحميل المتغيرات
# /etc/systemd/system/wifi-manager.service
[Service]
EnvironmentFile=/etc/wifi-manager/.env
ExecStart=/opt/wifi-manager/venv/bin/gunicorn app:app

# أو استخدم Docker secrets
docker run -d \
  --env-file /secure/path/.env \
  --name wifi-manager \
  wifi-manager:latest
```

### مراقبة المتغيرات
```python
# فحص دوري للإعدادات
@app.route('/health/config')
@admin_required
def config_health():
    required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY', 'DATABASE_URL']
    
    status = {}
    for var in required_vars:
        status[var] = 'OK' if os.environ.get(var) else 'MISSING'
    
    return jsonify({
        'config_status': status,
        'all_required_present': all(v == 'OK' for v in status.values())
    })
```

---

**🔒 تذكر**: احتفظ بملف .env آمناً ولا تشاركه أبداً في المستودعات العامة!