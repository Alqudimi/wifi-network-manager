# 🛠️ المشاكل الشائعة وحلولها

## نظرة عامة

هذا الدليل يغطي أكثر المشاكل شيوعاً التي قد تواجهها أثناء استخدام نظام إدارة شبكات Wi-Fi مع حلول مفصلة خطوة بخطوة.

---

## 🔐 مشاكل تسجيل الدخول والمصادقة

### المشكلة 1: عدم القدرة على تسجيل الدخول
**الأعراض**: رسالة خطأ "اسم المستخدم أو كلمة المرور غير صحيحة"

#### الأسباب المحتملة:
1. **كلمة مرور خاطئة**: تم تغيير كلمة المرور
2. **مشكلة في قاعدة البيانات**: عدم وجود المستخدم الافتراضي
3. **مشكلة في التشفير**: خطأ في تشفير كلمة المرور

#### الحلول:
```bash
# 1. إعادة تعيين كلمة مرور admin
python manage.py reset-admin-password

# 2. التحقق من وجود المستخدم في قاعدة البيانات
python -c "
from models.user import User
from database import db
admin = User.query.filter_by(username='admin').first()
if admin:
    print('المستخدم موجود')
else:
    print('المستخدم غير موجود - يجب إنشاؤه')
"

# 3. إنشاء مستخدم admin جديد
python -c "
from models.user import User
from database import db
from werkzeug.security import generate_password_hash

admin = User()
admin.username = 'admin'
admin.email = 'admin@localhost'
admin.password_hash = generate_password_hash('admin123')
admin.role = 'admin'
admin.is_active = True
db.session.add(admin)
db.session.commit()
print('تم إنشاء مستخدم admin جديد')
"
```

### المشكلة 2: انتهاء صلاحية الجلسة بسرعة
**الأعراض**: يطلب النظام تسجيل الدخول مرة أخرى بعد فترة قصيرة

#### الحل:
```python
# في config.py - زيادة مدة صلاحية JWT
from datetime import timedelta

JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # بدلاً من ساعة واحدة
```

### المشكلة 3: مشكلة في CSRF Token
**الأعراض**: رسالة "CSRF token missing or invalid"

#### الحل:
```python
# في app.py - التأكد من إعداد CSRF
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
csrf.init_app(app)

# أو تعطيل CSRF للتطوير (غير مستحسن للإنتاج)
WTF_CSRF_ENABLED = False
```

---

## 🎫 مشاكل إدارة الكروت

### المشكلة 4: الكروت لا تعمل بعد الإنشاء
**الأعراض**: رمز الكرت لا يُقبل في صفحة التفعيل

#### الأسباب والحلول:
```python
# 1. التحقق من حالة الكرت
from models.voucher import Voucher

voucher = Voucher.query.filter_by(code='YOUR_VOUCHER_CODE').first()
if voucher:
    print(f"حالة الكرت: {voucher.status}")
    print(f"تاريخ الانتهاء: {voucher.expires_at}")
    print(f"تاريخ الإنشاء: {voucher.created_at}")
else:
    print("الكرت غير موجود")

# 2. تفعيل كرت معطل
if voucher and voucher.status == 'disabled':
    voucher.status = 'active'
    db.session.commit()
    print("تم تفعيل الكرت")
```

### المشكلة 5: رموز QR لا تعمل
**الأعراض**: مسح رمز QR لا يؤدي إلى صفحة التفعيل

#### الحل:
```python
# التحقق من رابط QR
import qrcode
from PIL import Image

# قراءة رمز QR موجود
from pyzbar import pyzbar
import cv2

image = cv2.imread('path/to/qr_code.png')
barcodes = pyzbar.decode(image)

for barcode in barcodes:
    barcode_data = barcode.data.decode("utf-8")
    print(f"محتوى QR: {barcode_data}")
    
    # يجب أن يكون الرابط مثل:
    # http://your-domain.com/captive?code=VOUCHER_CODE
```

### المشكلة 6: الكروت تنتهي قبل الوقت المحدد
**الأعراض**: الكروت تصبح منتهية الصلاحية قبل المدة المحددة

#### الحل:
```python
# فحص إعدادات المدة الزمنية
from datetime import datetime, timedelta

# للكروت الجديدة - التأكد من الحساب الصحيح
voucher = Voucher()
voucher.duration_hours = 24
voucher.created_at = datetime.utcnow()
voucher.expires_at = voucher.created_at + timedelta(hours=voucher.duration_hours)

# للكروت الموجودة - تمديد الصلاحية
voucher = Voucher.query.get(voucher_id)
voucher.expires_at = datetime.utcnow() + timedelta(hours=24)
db.session.commit()
```

---

## 🌐 مشاكل الشبكة والاتصال

### المشكلة 7: لا يمكن الوصول للنظام من الخارج
**الأعراض**: النظام يعمل على localhost فقط

#### الحل:
```python
# في app.py - التأكد من bind على جميع العناوين
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# في config.py - إعداد CORS للسماح بالوصول الخارجي
CORS_ORIGINS = ['*']  # للتطوير
# أو للإنتاج:
CORS_ORIGINS = [
    'http://your-domain.com',
    'https://your-domain.com'
]
```

### المشكلة 8: مشاكل اتصال أجهزة التوجيه
**الأعراض**: "فشل الاتصال بجهاز التوجيه"

#### لأجهزة MikroTik:
```python
# فحص اتصال MikroTik
import librouteros

try:
    api = librouteros.connect(
        host='192.168.1.1',
        username='admin',
        password='your_password'
    )
    print("الاتصال ناجح")
    api.close()
except Exception as e:
    print(f"خطأ في الاتصال: {e}")
    
# التحقق من:
# 1. منفذ API مفعل (8728)
# 2. اسم المستخدم وكلمة المرور صحيحة
# 3. Firewall لا يحجب الاتصال
```

#### لأجهزة Ubiquiti:
```python
# فحص اتصال Ubiquiti
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# تسجيل الدخول
login_data = {
    'username': 'admin',
    'password': 'your_password'
}

session = requests.Session()
try:
    response = session.post(
        'https://192.168.1.1:8443/api/login',
        json=login_data,
        verify=False,
        timeout=10
    )
    if response.status_code == 200:
        print("الاتصال ناجح")
    else:
        print(f"فشل الاتصال: {response.status_code}")
except Exception as e:
    print(f"خطأ في الاتصال: {e}")
```

### المشكلة 9: العملاء لا يتم توجيههم لصفحة التفعيل
**الأعراض**: الأجهزة المتصلة بالـ Wi-Fi لا ترى صفحة تسجيل الدخول

#### الحل:
```bash
# 1. التحقق من إعداد Captive Portal في الراوتر
# لـ MikroTik:
/ip hotspot print

# 2. التحقق من DNS settings
# يجب أن يشير DNS إلى عنوان النظام

# 3. التحقق من Firewall rules
# يجب السماح بالوصول لصفحة التفعيل فقط
```

---

## 💾 مشاكل قاعدة البيانات

### المشكلة 10: خطأ "Database locked" في SQLite
**الأعراض**: رسالة "database is locked"

#### الحل:
```python
# 1. إغلاق جميع الاتصالات
from database import db
db.session.close()

# 2. إعادة تشغيل التطبيق
# systemctl restart wifi-manager

# 3. للمشاكل المستمرة - التبديل لـ PostgreSQL
# في .env:
DATABASE_URL=postgresql://username:password@localhost/wifi_manager
```

### المشكلة 11: مشكلة في Migration
**الأعراض**: خطأ عند تشغيل database migrations

#### الحل:
```bash
# 1. إعادة تهيئة migration
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 2. لمشاكل الـ schema
flask db stamp head
flask db migrate -m "Fix schema"
flask db upgrade
```

---

## 🖥️ مشاكل الخادم والأداء

### المشكلة 12: النظام بطيء جداً
**الأعراض**: استجابة بطيئة للصفحات والـ API

#### التشخيص:
```python
# فحص استهلاك الموارد
import psutil

# استهلاك المعالج
cpu_percent = psutil.cpu_percent(interval=1)
print(f"استهلاك المعالج: {cpu_percent}%")

# استهلاك الذاكرة
memory = psutil.virtual_memory()
print(f"استهلاك الذاكرة: {memory.percent}%")

# اتصالات قاعدة البيانات
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    print(f"Query took: {total:.4f} seconds")
```

#### الحلول:
```python
# 1. تفعيل التخزين المؤقت
from flask_caching import Cache

cache = Cache()
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/stats')
@cache.cached(timeout=300)  # 5 دقائق
def get_stats():
    return expensive_calculation()

# 2. تحسين استعلامات قاعدة البيانات
# استخدام eager loading
vouchers = Voucher.query.options(joinedload(Voucher.user)).all()

# 3. إعداد connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### المشكلة 13: خطأ "Port already in use"
**الأعراض**: لا يمكن تشغيل التطبيق على المنفذ 5000

#### الحل:
```bash
# 1. العثور على العملية التي تستخدم المنفذ
sudo netstat -tlnp | grep :5000
# أو
sudo lsof -i :5000

# 2. إيقاف العملية
sudo kill -9 PID_NUMBER

# 3. أو استخدام منفذ آخر
python app.py --port=8000
```

---

## 📱 مشاكل الواجهة والمتصفح

### المشكلة 14: الواجهة لا تظهر بشكل صحيح
**الأعراض**: تخطيط مشوه أو نصوص متداخلة

#### الحل:
```html
<!-- التأكد من meta tags في base.html -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">

<!-- التأكد من دعم RTL -->
<html dir="rtl" lang="ar">

<!-- تحميل الخطوط العربية -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;700&display=swap" rel="stylesheet">
```

### المشكلة 15: JavaScript لا يعمل
**الأعراض**: الأزرار لا تستجيب والنماذج لا تُرسل

#### التشخيص:
```javascript
// فتح Developer Tools (F12) والتحقق من Console
// البحث عن أخطاء JavaScript

// التحقق من تحميل الملفات
console.log("app.js loaded");

// التحقق من jQuery إذا كان مستخدماً
if (typeof jQuery === 'undefined') {
    console.error('jQuery is not loaded');
}
```

#### الحل:
```html
<!-- التأكد من ترتيب تحميل الملفات -->
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>

<!-- التحقق من مسارات الملفات -->
<script>
// في app.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    // باقي الكود هنا
});
</script>
```

---

## 🔧 نصائح عامة للاستكشاف

### أدوات التشخيص المفيدة

#### 1. فحص حالة النظام
```bash
# إنشاء سكريبت للفحص السريع
#!/bin/bash
echo "=== فحص حالة نظام إدارة شبكات Wi-Fi ==="

# فحص العمليات
echo "العمليات النشطة:"
ps aux | grep python

# فحص المنافذ
echo "المنافذ المفتوحة:"
netstat -tlnp | grep -E ":(5000|8728|8443|22)"

# فحص قاعدة البيانات
echo "قاعدة البيانات:"
if [ -f "wifi_manager.db" ]; then
    echo "✓ ملف SQLite موجود"
    sqlite3 wifi_manager.db "SELECT COUNT(*) FROM user;" 2>/dev/null || echo "✗ خطأ في قاعدة البيانات"
else
    echo "✗ ملف قاعدة البيانات غير موجود"
fi

# فحص الملفات الثابتة
echo "الملفات الثابتة:"
[ -d "static" ] && echo "✓ مجلد static موجود" || echo "✗ مجلد static غير موجود"
[ -d "templates" ] && echo "✓ مجلد templates موجود" || echo "✗ مجلد templates غير موجود"

echo "=== انتهى الفحص ==="
```

#### 2. تسجيل مفصل للأخطاء
```python
# في app.py - إضافة تسجيل مفصل
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/wifi_manager.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('نظام إدارة شبكات Wi-Fi بدأ التشغيل')
```

### متى تطلب المساعدة المتخصصة

اطلب المساعدة من متخصص إذا:
- ❌ المشاكل تؤثر على البيانات الحساسة
- ❌ هناك مشاكل أمنية محتملة
- ❌ النظام لا يستجيب بعد تجربة الحلول
- ❌ هناك فقدان في البيانات

### الوقاية من المشاكل

#### نصائح الصيانة الدورية:
1. **النسخ الاحتياطية**: يومية لقاعدة البيانات
2. **تحديث النظام**: شهرياً للأمان
3. **مراقبة الأداء**: أسبوعياً للإحصائيات
4. **فحص السجلات**: يومياً للأخطاء
5. **اختبار الكروت**: يومياً للتأكد من العمل

---

**💡 تذكر**: معظم المشاكل لها حلول بسيطة. ابدأ بالحلول الأساسية قبل الانتقال للمعقدة!