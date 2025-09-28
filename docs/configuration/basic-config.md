# ⚙️ الإعداد الأساسي للنظام

## نظرة عامة

هذا الدليل يغطي جميع الإعدادات الأساسية المطلوبة لتشغيل نظام إدارة شبكات Wi-Fi بكفاءة وأمان.

## ملف الإعداد الرئيسي

### موقع ملف الإعداد
```
config.py              # الإعداد الأساسي
config/
├── development.py     # إعدادات التطوير
├── production.py      # إعدادات الإنتاج
└── testing.py         # إعدادات الاختبار
```

### هيكل ملف config.py
```python
import os
from datetime import timedelta

class Config:
    # إعدادات Flask الأساسية
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # إعدادات قاعدة البيانات
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///wifi_manager.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # إعدادات الأمان
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # إعدادات CORS
    CORS_ORIGINS = ['*']  # للتطوير، حدد النطاقات للإنتاج
```

## متغيرات البيئة الأساسية

### ملف .env
أنشئ ملف `.env` في الجذر الرئيسي للمشروع:

```bash
# إعدادات الأمان
SECRET_KEY=your-very-long-random-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# إعدادات قاعدة البيانات
DATABASE_URL=postgresql://username:password@localhost/wifi_manager
# أو للـ SQLite (افتراضي)
# DATABASE_URL=sqlite:///wifi_manager.db

# إعدادات الخادم
FLASK_ENV=production
FLASK_DEBUG=False
HOST=0.0.0.0
PORT=5000

# إعدادات البريد الإلكتروني (اختياري)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# إعدادات Redis (اختياري)
REDIS_URL=redis://localhost:6379/0

# إعدادات التسجيل
LOG_LEVEL=INFO
LOG_FILE=logs/wifi_manager.log
```

### تحميل متغيرات البيئة
```python
# في بداية app.py
from dotenv import load_dotenv
load_dotenv()
```

## إعدادات قاعدة البيانات

### SQLite (للتطوير)
```python
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///wifi_manager_dev.db'
    SQLALCHEMY_ECHO = True  # لطباعة استعلامات SQL
```

### PostgreSQL (للإنتاج)
```python
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
```

### إعدادات الأداء
```python
# تحسين أداء قاعدة البيانات
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,           # عدد الاتصالات في المجموعة
    'pool_recycle': 3600,      # إعادة تدوير الاتصالات كل ساعة
    'pool_pre_ping': True,     # اختبار الاتصالات قبل الاستخدام
    'pool_timeout': 30,        # مهلة انتظار الاتصال
    'max_overflow': 40         # اتصالات إضافية عند الحاجة
}
```

## إعدادات الأمان المتقدمة

### مفاتيح التشفير
```python
# توليد مفتاح آمن
import secrets

# مفتاح Flask
SECRET_KEY = secrets.token_urlsafe(32)

# مفتاح JWT
JWT_SECRET_KEY = secrets.token_urlsafe(32)

# حفظ في ملف .env
print(f"SECRET_KEY={SECRET_KEY}")
print(f"JWT_SECRET_KEY={JWT_SECRET_KEY}")
```

### إعدادات JWT المتقدمة
```python
# انتهاء صلاحية الرموز
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# خوارزمية التشفير
JWT_ALGORITHM = 'HS256'

# معرف الجهة المصدرة
JWT_ISSUER = 'wifi-manager-system'

# إعدادات الحماية
JWT_ERROR_MESSAGE_KEY = 'message'
JWT_ACCESS_COOKIE_NAME = 'access_token'
JWT_REFRESH_COOKIE_NAME = 'refresh_token'
```

### CSRF Protection
```python
# تفعيل حماية CSRF
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None
WTF_CSRF_SSL_STRICT = True  # للإنتاج مع HTTPS

# مفتاح CSRF مخصص
WTF_CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY')
```

## إعدادات الشبكة والاتصال

### CORS Configuration
```python
# للتطوير - السماح لجميع المصادر
CORS_ORIGINS = ['*']

# للإنتاج - تحديد النطاقات المسموحة
CORS_ORIGINS = [
    'https://your-domain.com',
    'https://admin.your-domain.com',
    'https://app.your-domain.com'
]

# رؤوس مسموحة
CORS_ALLOW_HEADERS = [
    'Content-Type',
    'Authorization',
    'X-Requested-With'
]

# طرق مسموحة
CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
```

### Rate Limiting
```python
# حدود الطلبات
RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')

# حدود مختلفة حسب نوع المستخدم
RATELIMIT_DEFAULT = "100 per minute"
RATELIMIT_ADMIN = "1000 per minute"
RATELIMIT_API = "200 per minute"

# حدود خاصة للعمليات الثقيلة
RATELIMIT_HEAVY = "10 per minute"
```

## إعدادات الملفات والتخزين

### مجلدات التخزين
```python
# مجلد الملفات المرفوعة
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')

# أنواع الملفات المسموحة
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# حد حجم الملف (16 ميجابايت)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# مجلد الصور المؤقتة
TEMP_FOLDER = os.path.join(basedir, 'temp')

# مجلد النسخ الاحتياطية
BACKUP_FOLDER = os.path.join(basedir, 'backups')
```

### إعدادات QR Code
```python
# إعدادات رموز QR
QR_CODE_SIZE = (200, 200)
QR_CODE_BORDER = 4
QR_CODE_ERROR_CORRECTION = qrcode.constants.ERROR_CORRECT_M

# مجلد حفظ رموز QR
QR_CODE_FOLDER = os.path.join(UPLOAD_FOLDER, 'qr_codes')

# صيغة الصور
QR_CODE_FORMAT = 'PNG'
QR_CODE_QUALITY = 95
```

## إعدادات السجلات (Logging)

### إعداد السجلات الأساسي
```python
import logging
from logging.handlers import RotatingFileHandler

# مستوى السجلات
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

# ملف السجلات
LOG_FILE = os.environ.get('LOG_FILE', 'logs/wifi_manager.log')

# حجم الملف الأقصى (10 ميجابايت)
LOG_MAX_SIZE = 10 * 1024 * 1024

# عدد الملفات الاحتياطية
LOG_BACKUP_COUNT = 5
```

### إعداد السجلات المتقدم
```python
def setup_logging(app):
    if not app.debug and not app.testing:
        # إنشاء مجلد السجلات
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # إعداد ملف السجلات مع التدوير
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT
        )
        
        # تنسيق السجلات
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # إضافة المعالج للتطبيق
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, LOG_LEVEL))
        app.logger.info('نظام إدارة شبكات Wi-Fi بدأ التشغيل')
```

## إعدادات البريد الإلكتروني

### إعداد SMTP
```python
# خادم البريد
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'

# بيانات المصادقة
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# إعدادات الرسائل
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
MAIL_SUBJECT_PREFIX = '[نظام إدارة Wi-Fi] '
```

### قوالب البريد الإلكتروني
```python
# مجلد قوالب البريد
MAIL_TEMPLATES_FOLDER = 'templates/email'

# إعدادات القوالب
MAIL_TEMPLATE_WELCOME = 'welcome.html'
MAIL_TEMPLATE_RESET_PASSWORD = 'reset_password.html'
MAIL_TEMPLATE_VOUCHER_CREATED = 'voucher_created.html'
```

## إعدادات أجهزة التوجيه

### إعدادات MikroTik
```python
# منافذ الاتصال
MIKROTIK_API_PORT = 8728
MIKROTIK_API_SSL_PORT = 8729

# إعدادات الاتصال
MIKROTIK_CONNECTION_TIMEOUT = 10
MIKROTIK_READ_TIMEOUT = 5
MIKROTIK_MAX_RETRIES = 3
```

### إعدادات Ubiquiti
```python
# منافذ Controller
UBIQUITI_API_PORT = 8443
UBIQUITI_INFORM_PORT = 8080

# إعدادات API
UBIQUITI_API_VERSION = 'v1'
UBIQUITI_VERIFY_SSL = False  # للشهادات المحلية
```

### إعدادات Cisco
```python
# إعدادات SSH
CISCO_SSH_PORT = 22
CISCO_SSH_TIMEOUT = 30
CISCO_COMMAND_TIMEOUT = 10

# إعدادات التشفير
CISCO_SSH_CIPHERS = ['aes128-ctr', 'aes192-ctr', 'aes256-ctr']
```

## إعدادات التخزين المؤقت

### Redis Configuration
```python
# اتصال Redis
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# إعدادات التخزين المؤقت
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = REDIS_URL
CACHE_DEFAULT_TIMEOUT = 300  # 5 دقائق

# تخزين الجلسات
SESSION_TYPE = 'redis'
SESSION_REDIS = redis.from_url(REDIS_URL)
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True
```

## التحقق من الإعدادات

### سكريبت فحص الإعدادات
```python
#!/usr/bin/env python3

import os
import sys
from config import Config

def check_config():
    """فحص صحة الإعدادات الأساسية"""
    
    errors = []
    warnings = []
    
    # فحص المفاتيح الأمنية
    if Config.SECRET_KEY == 'your-secret-key-here':
        errors.append("يجب تغيير SECRET_KEY الافتراضي")
    
    if Config.JWT_SECRET_KEY == 'jwt-secret-key':
        errors.append("يجب تغيير JWT_SECRET_KEY الافتراضي")
    
    # فحص قاعدة البيانات
    if not Config.SQLALCHEMY_DATABASE_URI:
        errors.append("يجب تحديد رابط قاعدة البيانات")
    
    # فحص المجلدات
    required_dirs = ['logs', 'static/uploads', 'temp', 'backups']
    for directory in required_dirs:
        if not os.path.exists(directory):
            warnings.append(f"المجلد غير موجود: {directory}")
    
    # طباعة النتائج
    if errors:
        print("❌ أخطاء في الإعدادات:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("⚠️ تحذيرات:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("✅ جميع الإعدادات صحيحة!")
    
    return len(errors) == 0

if __name__ == '__main__':
    success = check_config()
    sys.exit(0 if success else 1)
```

## نصائح للإعداد الآمن

### أفضل الممارسات
1. **استخدم متغيرات البيئة** لجميع البيانات الحساسة
2. **غيّر المفاتيح الافتراضية** قبل النشر
3. **فعّل HTTPS** في بيئة الإنتاج
4. **راقب السجلات** بانتظام
5. **احتفظ بنسخ احتياطية** من الإعدادات

### تجنب هذه الأخطاء
- ❌ تخزين كلمات المرور في ملفات الكود
- ❌ استخدام المفاتيح الافتراضية في الإنتاج
- ❌ تفعيل وضع التطوير في الإنتاج
- ❌ عدم تحديد حدود للموارد
- ❌ إهمال تحديث الإعدادات دورياً

---

**💡 نصيحة**: ابدأ بالإعدادات الأساسية وأضف التعقيدات تدريجياً حسب احتياجاتك.