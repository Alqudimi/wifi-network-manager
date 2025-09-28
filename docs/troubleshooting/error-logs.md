# 📝 سجلات الأخطاء

## نظرة عامة

فهم وتحليل سجلات الأخطاء أساسي لصيانة النظام وحل المشاكل بسرعة. هذا الدليل يوضح كيفية قراءة وتفسير أنواع السجلات المختلفة.

## مواقع ملفات السجلات

### الملفات الرئيسية
```bash
# سجلات التطبيق الرئيسية
/var/log/wifi-manager/app.log
/var/log/wifi-manager/error.log
/var/log/wifi-manager/access.log

# سجلات قاعدة البيانات
/var/log/postgresql/postgresql-13-main.log
/var/log/wifi-manager/database.log

# سجلات النظام
/var/log/syslog
/var/log/nginx/error.log
/var/log/nginx/access.log

# سجلات الأمان
/var/log/wifi-manager/security.log
/var/log/auth.log
```

### هيكل ملفات السجلات
```
logs/
├── app.log              # سجل التطبيق الرئيسي
├── error.log           # الأخطاء فقط
├── access.log          # طلبات HTTP
├── security.log        # أحداث أمنية
├── database.log        # استعلامات قاعدة البيانات
├── router.log          # تفاعل مع أجهزة التوجيه
└── background.log      # المهام في الخلفية
```

## تنسيقات السجلات

### تنسيق السجل الأساسي
```
2025-09-28 20:30:15,123 [INFO] module_name:line_number - رسالة السجل
```

### مكونات السجل
- **التاريخ والوقت**: `2025-09-28 20:30:15,123`
- **مستوى السجل**: `[INFO]`, `[WARNING]`, `[ERROR]`, `[CRITICAL]`
- **الموقع**: `module_name:line_number`
- **الرسالة**: نص وصفي للحدث

### أمثلة سجلات مختلفة
```bash
# سجل نجاح العملية
2025-09-28 20:30:15,123 [INFO] vouchers:45 - تم إنشاء كرت جديد: WIFI-ABC123

# سجل تحذير
2025-09-28 20:30:16,456 [WARNING] database:23 - استعلام بطيء: 2.3 ثانية

# سجل خطأ
2025-09-28 20:30:17,789 [ERROR] router_manager:67 - فشل الاتصال بجهاز التوجيه 192.168.1.1

# سجل خطأ حرج
2025-09-28 20:30:18,012 [CRITICAL] app:12 - فشل تحميل إعدادات قاعدة البيانات
```

## أنواع الأخطاء الشائعة

### 1. أخطاء قاعدة البيانات
```bash
# فقدان الاتصال
[ERROR] database:45 - SQLSTATE[HY000] [2002] Connection refused
[ERROR] database:67 - SQLSTATE[08006] server closed the connection unexpectedly

# جدول غير موجود
[ERROR] database:89 - SQLSTATE[42P01] relation "vouchers" does not exist

# انتهاك القيود
[ERROR] database:123 - SQLSTATE[23505] duplicate key value violates unique constraint
```

**كيفية الحل:**
```bash
# فحص حالة قاعدة البيانات
sudo systemctl status postgresql

# فحص اتصال قاعدة البيانات
psql -h localhost -U wifi_manager -d wifi_manager_db -c "SELECT 1;"

# فحص المساحة المتاحة
df -h /var/lib/postgresql/
```

### 2. أخطاء أجهزة التوجيه
```bash
# انقطاع الاتصال
[ERROR] router_manager:34 - Connection timeout to 192.168.1.1:8728
[ERROR] router_manager:45 - Authentication failed for user 'admin'

# خطأ في API
[ERROR] mikrotik_api:67 - Invalid command: /ip/hotspot/user/add
[ERROR] ubiquiti_api:89 - HTTP 401: Unauthorized access

# جهاز غير مدعوم
[WARNING] router_manager:23 - Unknown router type: TP-Link
```

**خطوات التشخيص:**
```bash
# فحص الاتصال
ping 192.168.1.1

# فحص المنفذ
telnet 192.168.1.1 8728

# فحص بيانات الدخول
# راجع إعدادات الجهاز في قاعدة البيانات
```

### 3. أخطاء المصادقة
```bash
# كلمة مرور خاطئة
[WARNING] auth:23 - Failed login attempt for user 'admin' from 192.168.1.50

# رمز JWT منتهي
[ERROR] auth:45 - Token expired for user ID 123

# صلاحيات غير كافية
[WARNING] auth:67 - User 'operator1' attempted unauthorized access to /admin/users

# تجاوز حد المحاولات
[ERROR] auth:89 - Account locked for user 'admin' after 5 failed attempts
```

### 4. أخطاء الشبكة
```bash
# مشكلة في البورت
[ERROR] app:12 - [Errno 98] Address already in use: ('0.0.0.0', 5000)

# خطأ CORS
[WARNING] cors:34 - CORS error: Origin 'http://localhost:3000' not allowed

# خطأ SSL
[ERROR] ssl:56 - SSL certificate verification failed

# انقطاع الإنترنت
[ERROR] network:78 - DNS resolution failed for domain.com
```

### 5. أخطاء الذاكرة والأداء
```bash
# نفاد الذاكرة
[CRITICAL] system:23 - Out of memory: cannot allocate region

# استهلاك عالي للمعالج
[WARNING] monitor:45 - High CPU usage: 95% for 5 minutes

# قرص ممتلئ
[ERROR] system:67 - No space left on device: /var/log

# عملية بطيئة
[WARNING] performance:89 - Slow operation: voucher_creation took 5.2 seconds
```

## تحليل السجلات

### أدوات التحليل

#### grep للبحث في السجلات
```bash
# البحث عن أخطاء محددة
grep "ERROR" /var/log/wifi-manager/app.log

# البحث في فترة زمنية محددة
grep "2025-09-28 20:" /var/log/wifi-manager/app.log

# البحث عن أخطاء الراوتر
grep -i "router\|connection" /var/log/wifi-manager/error.log

# عد الأخطاء
grep -c "ERROR" /var/log/wifi-manager/app.log
```

#### tail لمتابعة السجلات الحية
```bash
# متابعة السجل في الوقت الفعلي
tail -f /var/log/wifi-manager/app.log

# متابعة آخر 100 سطر
tail -n 100 /var/log/wifi-manager/app.log

# متابعة عدة ملفات
tail -f /var/log/wifi-manager/*.log
```

#### awk للتحليل المتقدم
```bash
# استخراج الأخطاء حسب الوقت
awk '/ERROR/ {print $1, $2, $NF}' /var/log/wifi-manager/app.log

# إحصائيات مستويات السجلات
awk '{print $3}' /var/log/wifi-manager/app.log | sort | uniq -c

# أكثر الأخطاء تكراراً
awk -F'] ' '/ERROR/ {print $2}' /var/log/wifi-manager/app.log | sort | uniq -c | sort -nr
```

### سكريبت تحليل السجلات
```bash
#!/bin/bash
# log_analyzer.sh

LOG_FILE="/var/log/wifi-manager/app.log"
DATE_FILTER=${1:-$(date +%Y-%m-%d)}

echo "=== تحليل سجلات $DATE_FILTER ==="

# إحصائيات عامة
echo -e "\nإحصائيات عامة:"
echo "إجمالي الأسطر: $(grep "$DATE_FILTER" "$LOG_FILE" | wc -l)"
echo "أخطاء: $(grep "$DATE_FILTER" "$LOG_FILE" | grep -c ERROR)"
echo "تحذيرات: $(grep "$DATE_FILTER" "$LOG_FILE" | grep -c WARNING)"
echo "معلومات: $(grep "$DATE_FILTER" "$LOG_FILE" | grep -c INFO)"

# أكثر الأخطاء شيوعاً
echo -e "\nأكثر الأخطاء شيوعاً:"
grep "$DATE_FILTER" "$LOG_FILE" | grep ERROR | awk -F'] ' '{print $2}' | \
  cut -d':' -f1 | sort | uniq -c | sort -nr | head -5

# أوقات الذروة للأخطاء
echo -e "\nتوزيع الأخطاء حسب الساعة:"
grep "$DATE_FILTER" "$LOG_FILE" | grep ERROR | \
  awk '{print $2}' | cut -d':' -f1 | sort | uniq -c

# أخطاء قاعدة البيانات
echo -e "\nأخطاء قاعدة البيانات:"
grep "$DATE_FILTER" "$LOG_FILE" | grep -i "database\|sql\|connection" | grep ERROR | wc -l

# أخطاء أجهزة التوجيه
echo -e "\nأخطاء أجهزة التوجيه:"
grep "$DATE_FILTER" "$LOG_FILE" | grep -i "router\|mikrotik\|ubiquiti" | grep ERROR | wc -l
```

## مراقبة السجلات في الوقت الفعلي

### إعداد logrotate
```bash
# /etc/logrotate.d/wifi-manager
/var/log/wifi-manager/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload wifi-manager
    endscript
}
```

### مراقبة تلقائية للأخطاء
```python
#!/usr/bin/env python3
# error_monitor.py

import time
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogMonitor(FileSystemEventHandler):
    def __init__(self):
        self.error_patterns = [
            r'CRITICAL.*',
            r'ERROR.*database.*',
            r'ERROR.*router.*connection',
            r'WARNING.*failed login.*'
        ]
    
    def on_modified(self, event):
        if event.src_path.endswith('.log'):
            self.check_new_errors(event.src_path)
    
    def check_new_errors(self, log_file):
        try:
            with open(log_file, 'r') as f:
                # قراءة آخر 10 أسطر
                lines = f.readlines()[-10:]
                
            for line in lines:
                for pattern in self.error_patterns:
                    if re.search(pattern, line):
                        self.send_alert(line.strip())
                        
        except Exception as e:
            print(f"خطأ في مراقبة السجل: {e}")
    
    def send_alert(self, error_line):
        # إرسال تنبيه (email, SMS, webhook, etc.)
        print(f"🚨 خطأ مكتشف: {error_line}")
        
        # يمكن إضافة إرسال بريد إلكتروني هنا
        # send_email_alert(error_line)

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(LogMonitor(), '/var/log/wifi-manager/', recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

## استكشاف أخطاء محددة

### مشكلة: كروت لا تعمل
```bash
# فحص سجلات إنشاء الكروت
grep "voucher.*created\|voucher.*failed" /var/log/wifi-manager/app.log

# فحص مزامنة الراوتر
grep "router.*sync\|router.*failed" /var/log/wifi-manager/router.log

# فحص قاعدة البيانات
grep "INSERT INTO vouchers\|voucher.*constraint" /var/log/wifi-manager/database.log
```

### مشكلة: بطء في النظام
```bash
# فحص الاستعلامات البطيئة
grep "slow.*query\|query.*took" /var/log/wifi-manager/database.log

# فحص استهلاك الذاكرة
grep "memory\|OutOfMemory" /var/log/wifi-manager/app.log

# فحص الحمولة العالية
grep "high.*load\|cpu.*usage" /var/log/syslog
```

### مشكلة: مستخدمون لا يستطيعون الدخول
```bash
# فحص محاولات تسجيل الدخول
grep "login.*attempt\|authentication" /var/log/wifi-manager/security.log

# فحص أخطاء الجلسات
grep "session.*expired\|token.*invalid" /var/log/wifi-manager/app.log

# فحص قاعدة بيانات المستخدمين
grep "SELECT.*users\|user.*not.*found" /var/log/wifi-manager/database.log
```

## أتمتة تنظيف السجلات

### سكريبت تنظيف يومي
```bash
#!/bin/bash
# cleanup_logs.sh

LOG_DIR="/var/log/wifi-manager"
RETENTION_DAYS=30

echo "بدء تنظيف السجلات القديمة..."

# حذف السجلات الأقدم من 30 يوم
find "$LOG_DIR" -name "*.log" -mtime +$RETENTION_DAYS -delete

# ضغط السجلات الأقدم من 7 أيام
find "$LOG_DIR" -name "*.log" -mtime +7 ! -name "*.gz" -exec gzip {} \;

# إحصائيات بعد التنظيف
echo "حجم مجلد السجلات بعد التنظيف: $(du -sh $LOG_DIR)"

echo "تم الانتهاء من تنظيف السجلات"
```

### إعداد crontab للتنظيف التلقائي
```bash
# تشغيل التنظيف يومياً في 2 صباحاً
0 2 * * * /usr/local/bin/cleanup_logs.sh

# إرسال تقرير أسبوعي للأخطاء
0 8 * * 1 /usr/local/bin/log_analyzer.sh $(date -d '7 days ago' +%Y-%m-%d) | mail -s "تقرير أخطاء أسبوعي" admin@company.com
```

---

**📊 نصيحة**: راجع السجلات بانتظام وأنشئ تنبيهات للأخطاء الحرجة لتفادي المشاكل قبل تفاقمها!