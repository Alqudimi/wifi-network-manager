# 🔗 مقدمة إلى API

## نظرة عامة

يوفر نظام إدارة شبكات Wi-Fi واجهة برمجة تطبيقات (API) شاملة تتيح للمطورين التكامل مع النظام وأتمتة العمليات المختلفة.

## مميزات API

### 🔐 آمن ومحمي
- مصادقة JWT متقدمة
- تشفير جميع البيانات المنقولة
- صلاحيات متدرجة حسب نوع المستخدم

### 📊 شامل
- إدارة الكروت والمستخدمين
- مراقبة الشبكة والإحصائيات
- التحكم في أجهزة التوجيه
- تصدير البيانات بصيغ متعددة

### 🚀 سريع وموثوق
- استجابة سريعة (< 100ms معظم الطلبات)
- معالجة أخطاء شاملة
- توثيق تفاعلي كامل

## العنوان الأساسي للـ API

```
https://your-domain.com/api/
```

## إصدار API

```
الإصدار الحالي: v1
```

جميع endpoints تبدأ بـ `/api/` متبوعة بنوع العملية.

## أنواع البيانات المدعومة

### الطلبات (Requests)
- **Content-Type**: `application/json`
- **المصادقة**: `Bearer <JWT_TOKEN>`
- **اللغة**: `Accept-Language: ar` (للواجهة العربية)

### الاستجابات (Responses)
- **الصيغة**: JSON دائماً
- **الترميز**: UTF-8
- **أوقات التواريخ**: ISO 8601 (UTC)

## هيكل الاستجابة القياسي

### نجاح العملية
```json
{
  "success": true,
  "message": "تمت العملية بنجاح",
  "data": {
    // بيانات الاستجابة
  },
  "timestamp": "2025-09-28T20:30:00Z"
}
```

### فشل العملية
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "خطأ في التحقق من صحة البيانات",
    "details": {
      "field": "email",
      "issue": "تنسيق البريد الإلكتروني غير صحيح"
    }
  },
  "timestamp": "2025-09-28T20:30:00Z"
}
```

## أكواد الحالة (Status Codes)

### الحالات الناجحة
- **200 OK**: طلب ناجح وإرجاع البيانات
- **201 Created**: تم إنشاء مورد جديد بنجاح
- **204 No Content**: طلب ناجح بدون بيانات للإرجاع

### أخطاء العميل
- **400 Bad Request**: خطأ في بيانات الطلب
- **401 Unauthorized**: مصادقة مطلوبة أو فاشلة
- **403 Forbidden**: لا توجد صلاحية للوصول
- **404 Not Found**: المورد المطلوب غير موجود
- **422 Unprocessable Entity**: بيانات صحيحة لكن منطقياً خاطئة

### أخطاء الخادم
- **500 Internal Server Error**: خطأ داخلي في الخادم
- **503 Service Unavailable**: الخدمة غير متاحة مؤقتاً

## حدود الاستخدام (Rate Limiting)

### الحدود الافتراضية
- **المستخدم العادي**: 100 طلب/دقيقة
- **المدير**: 1000 طلب/دقيقة
- **الطلبات الثقيلة**: 10 طلب/دقيقة (مثل التصدير)

### رؤوس المعلومات
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1695750000
```

## المجموعات الرئيسية للـ API

### 🔐 المصادقة والتفويض
```
POST /api/auth/login       # تسجيل الدخول
POST /api/auth/logout      # تسجيل الخروج
POST /api/auth/refresh     # تجديد الرمز المميز
GET  /api/auth/profile     # بيانات المستخدم الحالي
```

### 🎫 إدارة الكروت
```
GET    /api/vouchers       # قائمة الكروت
POST   /api/vouchers       # إنشاء كرت جديد
GET    /api/vouchers/{id}  # تفاصيل كرت محدد
PUT    /api/vouchers/{id}  # تعديل كرت
DELETE /api/vouchers/{id}  # حذف كرت
POST   /api/vouchers/batch # إنشاء كروت متعددة
```

### 👥 إدارة المستخدمين
```
GET    /api/users          # قائمة المستخدمين
POST   /api/users          # إنشاء مستخدم جديد
GET    /api/users/{id}     # تفاصيل مستخدم
PUT    /api/users/{id}     # تعديل مستخدم
DELETE /api/users/{id}     # حذف مستخدم
```

### 🌐 إدارة الشبكات
```
GET    /api/networks       # قائمة الشبكات
POST   /api/networks       # إضافة شبكة جديدة
GET    /api/routers        # قائمة أجهزة التوجيه
POST   /api/routers        # إضافة جهاز توجيه
```

### 📊 الإحصائيات والتقارير
```
GET /api/stats/dashboard   # إحصائيات لوحة التحكم
GET /api/stats/vouchers    # إحصائيات الكروت
GET /api/stats/usage       # إحصائيات الاستخدام
GET /api/reports/export    # تصدير التقارير
```

### 🎛️ التحكم في الشبكة
```
GET    /api/control/active     # الاتصالات النشطة
POST   /api/control/disconnect # قطع اتصال محدد
GET    /api/control/monitor    # مراقبة الشبكة
```

## أمثلة سريعة

### تسجيل الدخول
```bash
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-password"
  }'
```

### إنشاء كرت جديد
```bash
curl -X POST https://your-domain.com/api/vouchers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "voucher_type": "standard",
    "duration_hours": 24,
    "data_limit_mb": 1000,
    "speed_limit_kbps": 1024
  }'
```

### عرض الكروت النشطة
```bash
curl -X GET https://your-domain.com/api/vouchers?status=active \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## مكتبات SDK المتاحة

### JavaScript/Node.js
```javascript
import { WiFiManagerAPI } from 'wifi-manager-sdk';

const api = new WiFiManagerAPI({
  baseURL: 'https://your-domain.com/api',
  token: 'YOUR_JWT_TOKEN'
});

// إنشاء كرت جديد
const voucher = await api.vouchers.create({
  voucher_type: 'standard',
  duration_hours: 24
});
```

### Python
```python
from wifi_manager_sdk import WiFiManagerAPI

api = WiFiManagerAPI(
    base_url='https://your-domain.com/api',
    token='YOUR_JWT_TOKEN'
)

# إنشاء كرت جديد
voucher = api.vouchers.create(
    voucher_type='standard',
    duration_hours=24
)
```

### PHP
```php
<?php
use WiFiManager\SDK\Client;

$api = new Client([
    'base_url' => 'https://your-domain.com/api',
    'token' => 'YOUR_JWT_TOKEN'
]);

// إنشاء كرت جديد
$voucher = $api->vouchers()->create([
    'voucher_type' => 'standard',
    'duration_hours' => 24
]);
?>
```

## معالجة الأخطاء

### التحقق من نجاح الطلب
```javascript
if (response.success) {
  // معالجة البيانات الناجحة
  console.log(response.data);
} else {
  // معالجة الخطأ
  console.error(response.error.message);
}
```

### إعادة المحاولة التلقائية
```javascript
async function retryRequest(apiCall, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

## الأمان وأفضل الممارسات

### حماية الرموز المميزة
- ✅ احفظ JWT في مكان آمن
- ✅ جدد الرموز قبل انتهائها
- ✅ لا تشارك الرموز في الكود العام
- ✅ استخدم HTTPS دائماً

### تجنب هذه الأخطاء
- ❌ تخزين كلمات المرور في النص الخام
- ❌ إرسال طلبات حساسة عبر HTTP
- ❌ تجاهل أكواد الأخطاء
- ❌ عدم التحقق من صحة البيانات

## الحصول على المساعدة

### الموارد المفيدة
- [دليل المصادقة التفصيلي](authentication.md)
- [قائمة شاملة بنقاط النهاية](endpoints.md)
- [أمثلة عملية متقدمة](examples.md)

### الدعم
إذا واجهت مشاكل في استخدام API:
1. راجع [الأخطاء الشائعة](../troubleshooting/common-issues.md)
2. تحقق من [سجلات الأخطاء](../troubleshooting/error-logs.md)
3. جرب [أدوات التشخيص](../troubleshooting/diagnostic-tools.md)

---

**🚀 مستعد للبدء؟** انتقل إلى [دليل المصادقة](authentication.md) لبدء استخدام API.