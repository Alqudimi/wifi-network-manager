# 📖 توثيق نظام إدارة شبكات Wi-Fi

مرحباً بك في التوثيق الشامل لنظام إدارة شبكات Wi-Fi. هذا النظام مصمم لإدارة شبكات WPA/WPA2-Personal مع إدارة الكروت وأنظمة المصادقة ودعم أجهزة التوجيه المتعددة.

## 📚 محتويات التوثيق

### 🔧 التثبيت والإعداد
- [دليل التثبيت السريع](installation/quick-start.md)
- [التثبيت المتقدم](installation/advanced-setup.md)
- [متطلبات النظام](installation/requirements.md)
- [إعداد قاعدة البيانات](installation/database-setup.md)

### 👤 دليل المستخدم
- [البدء السريع](user-guide/getting-started.md)
- [لوحة التحكم](user-guide/dashboard.md)
- [إدارة الكروت](user-guide/voucher-management.md)
- [إدارة الشبكات](user-guide/network-management.md)
- [إدارة المستخدمين](user-guide/user-management.md)
- [التحكم في الشبكة](user-guide/network-control.md)

### 🔗 توثيق API
- [مقدمة للـ API](api/introduction.md)
- [المصادقة والتفويض](api/authentication.md)
- [نقاط النهاية](api/endpoints.md)
- [أمثلة عملية](api/examples.md)

### ⚙️ الإعداد والتكوين
- [ملف الإعداد الأساسي](configuration/basic-config.md)
- [إعداد أجهزة التوجيه](configuration/router-setup.md)
- [إعدادات الأمان](configuration/security-settings.md)
- [متغيرات البيئة](configuration/environment-variables.md)

### 🏗️ معمارية النظام
- [نظرة عامة على المعمارية](architecture/overview.md)
- [قاعدة البيانات](architecture/database-schema.md)
- [مكونات النظام](architecture/system-components.md)
- [تدفق البيانات](architecture/data-flow.md)

### 🛠️ حل المشاكل
- [المشاكل الشائعة](troubleshooting/common-issues.md)
- [سجلات الأخطاء](troubleshooting/error-logs.md)
- [أدوات التشخيص](troubleshooting/diagnostic-tools.md)
- [نصائح الأداء](troubleshooting/performance-tips.md)

## 🚀 البدء السريع

1. **التثبيت**: ابدأ بـ [دليل التثبيت السريع](installation/quick-start.md)
2. **الإعداد الأولي**: راجع [البدء السريع](user-guide/getting-started.md)
3. **إنشاء أول كرت**: تابع [إدارة الكروت](user-guide/voucher-management.md)

## 📊 ميزات النظام

- ✅ واجهة عربية بدعم RTL كامل
- ✅ نظام مصادقة متقدم بـ JWT
- ✅ إدارة كروت Wi-Fi مع رموز QR
- ✅ دعم أجهزة توجيه متعددة (MikroTik, Ubiquiti, Cisco)
- ✅ مراقبة الشبكة في الوقت الفعلي
- ✅ نظام إدارة المستخدمين
- ✅ إحصائيات شاملة ولوحة تحكم

## 💻 متطلبات النظام

- Python 3.11+
- Flask 2.3+
- PostgreSQL أو SQLite
- متصفح حديث يدعم ES6+

## 🔐 بيانات الدخول الافتراضية

```
اسم المستخدم: admin
كلمة المرور: admin123
```

**⚠️ تنبيه أمني**: يجب تغيير كلمة المرور فور تسجيل الدخول الأول!

## 📞 الدعم والمساعدة

إذا واجهت أي مشاكل أو كان لديك أسئلة، راجع:
- [المشاكل الشائعة](troubleshooting/common-issues.md)
- [سجلات الأخطاء](troubleshooting/error-logs.md)
- [أدوات التشخيص](troubleshooting/diagnostic-tools.md)

---

**آخر تحديث**: سبتمبر 2025  
**الإصدار**: 1.0.0  
**الترخيص**: انظر ملف LICENSE