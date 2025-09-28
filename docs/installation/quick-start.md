# 🚀 دليل التثبيت السريع

## نظرة عامة

هذا الدليل سيساعدك على تشغيل نظام إدارة شبكات Wi-Fi في أقل من 10 دقائق.

## متطلبات النظام

### الحد الأدنى
- **نظام التشغيل**: Linux, macOS, أو Windows 10+
- **Python**: الإصدار 3.11 أو أحدث
- **الذاكرة**: 512 MB RAM
- **التخزين**: 100 MB مساحة حرة
- **الشبكة**: اتصال إنترنت للتثبيت الأولي

### المستحسن
- **Python**: 3.11+
- **الذاكرة**: 2 GB RAM
- **التخزين**: 1 GB مساحة حرة
- **قاعدة البيانات**: PostgreSQL 12+

## 1. تحميل المشروع

### من GitHub
```bash
git clone https://github.com/your-repo/wifi-manager.git
cd wifi-manager
```

### أو تحميل ZIP
1. اذهب إلى صفحة المشروع على GitHub
2. انقر على "Code" ← "Download ZIP"
3. استخرج الملفات في المجلد المطلوب

## 2. إعداد Python والمتطلبات

### إنشاء بيئة افتراضية
```bash
python3 -m venv venv
source venv/bin/activate  # في Linux/macOS
# أو
venv\Scripts\activate     # في Windows
```

### تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

## 3. إعداد قاعدة البيانات

### استخدام SQLite (للتطوير)
النظام سيستخدم SQLite تلقائياً إذا لم تكن قاعدة بيانات PostgreSQL متوفرة.

### استخدام PostgreSQL (للإنتاج)
```bash
# إنشاء قاعدة بيانات جديدة
createdb wifi_manager

# تعيين متغير البيئة
export DATABASE_URL="postgresql://username:password@localhost/wifi_manager"
```

## 4. تشغيل التطبيق

### التشغيل المباشر
```bash
python app.py
```

### أو باستخدام Flask
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## 5. الوصول للنظام

1. افتح متصفحك واذهب إلى: `http://localhost:5000`
2. استخدم بيانات الدخول الافتراضية:
   - **اسم المستخدم**: `admin`
   - **كلمة المرور**: `admin123`

## 6. الإعداد الأولي

### تغيير كلمة المرور
1. سجل الدخول بالبيانات الافتراضية
2. اذهب إلى إعدادات المستخدم
3. غيّر كلمة المرور فوراً

### إضافة أول جهاز توجيه
1. اذهب إلى "إدارة الشبكات"
2. انقر على "إضافة جهاز توجيه جديد"
3. أدخل تفاصيل جهاز التوجيه:
   - عنوان IP
   - نوع الجهاز (MikroTik/Ubiquiti/Cisco)
   - بيانات المصادقة

### إنشاء أول كرت
1. اذهب إلى "إدارة الكروت"
2. انقر على "إنشاء كرت جديد"
3. حدد المدة وحد البيانات
4. انقر على "إنشاء"

## ✅ التحقق من التثبيت

### فحص الاتصال بقاعدة البيانات
```bash
python -c "from database import db; print('Database connected successfully!')"
```

### فحص الوحدات المطلوبة
```bash
python -c "import flask, jwt, qrcode; print('All modules imported successfully!')"
```

### فحص المنافذ
```bash
netstat -an | grep :5000
```

## 🔧 الاستكشاف وإصلاح المشاكل

### المشكلة: خطأ في الاتصال بقاعدة البيانات
**الحل**: تأكد من تشغيل PostgreSQL أو استخدم SQLite:
```bash
export DATABASE_URL=""  # للعودة إلى SQLite
```

### المشكلة: المنفذ 5000 مستخدم
**الحل**: استخدم منفذ آخر:
```bash
python app.py --port=8000
```

### المشكلة: خطأ في استيراد الوحدات
**الحل**: تأكد من تفعيل البيئة الافتراضية:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 🎯 الخطوات التالية

1. راجع [دليل المستخدم الشامل](../user-guide/getting-started.md)
2. اطلع على [إعدادات الأمان](../configuration/security-settings.md)
3. قم بإعداد [المراقبة والسجلات](../troubleshooting/error-logs.md)
4. اقرأ عن [أفضل الممارسات](../configuration/best-practices.md)

## 📞 الحصول على المساعدة

إذا واجهت أي مشاكل:
1. راجع [المشاكل الشائعة](../troubleshooting/common-issues.md)
2. تحقق من [سجلات الأخطاء](../troubleshooting/error-logs.md)
3. استخدم [أدوات التشخيص](../troubleshooting/diagnostic-tools.md)

---

**تهانينا! 🎉** نظام إدارة شبكات Wi-Fi جاهز للاستخدام الآن.