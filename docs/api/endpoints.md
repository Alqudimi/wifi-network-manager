# 🔗 نقاط النهاية (API Endpoints)

## نظرة عامة

هذا المرجع الشامل لجميع نقاط النهاية المتاحة في API نظام إدارة شبكات Wi-Fi.

**العنوان الأساسي**: `https://your-domain.com/api/`

---

## 🔐 المصادقة والتفويض

### POST /api/auth/login
**الوصف**: تسجيل الدخول والحصول على رمز JWT

**المتطلبات**:
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم تسجيل الدخول بنجاح",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "is_active": true
    }
  },
  "timestamp": "2025-09-28T20:30:00Z"
}
```

**أخطاء محتملة**:
- `400`: بيانات مفقودة
- `401`: اسم المستخدم أو كلمة المرور خاطئة
- `403`: الحساب معطل

---

### POST /api/auth/logout
**الوصف**: تسجيل الخروج وإلغاء الرمز المميز

**المتطلبات**: 
- Header: `Authorization: Bearer <token>`

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم تسجيل الخروج بنجاح",
  "timestamp": "2025-09-28T20:30:00Z"
}
```

---

### GET /api/auth/profile
**الوصف**: الحصول على بيانات المستخدم الحالي

**المتطلبات**: 
- Header: `Authorization: Bearer <token>`

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-09-28T20:30:00Z"
  }
}
```

---

## 🎫 إدارة الكروت

### GET /api/vouchers
**الوصف**: الحصول على قائمة الكروت مع إمكانية الفلترة

**المعاملات الاختيارية**:
- `status`: فلترة حسب الحالة (`active`, `used`, `expired`, `disabled`)
- `voucher_type`: فلترة حسب النوع (`standard`, `premium`, `vip`)
- `page`: رقم الصفحة (افتراضي: 1)
- `per_page`: عدد العناصر بالصفحة (افتراضي: 20)
- `search`: البحث في كود الكرت

**مثال الطلب**:
```
GET /api/vouchers?status=active&page=1&per_page=10
```

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "vouchers": [
      {
        "id": 1,
        "code": "WIFI-ABC123",
        "voucher_type": "standard",
        "status": "active",
        "duration_hours": 24,
        "data_limit_mb": 1000,
        "speed_limit_kbps": 1024,
        "price": 15.0,
        "created_at": "2025-09-28T10:00:00Z",
        "expires_at": "2025-10-28T10:00:00Z",
        "qr_code_url": "/static/qr_codes/WIFI-ABC123.png"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 156,
      "pages": 16
    }
  }
}
```

---

### POST /api/vouchers
**الوصف**: إنشاء كرت جديد

**المتطلبات**:
```json
{
  "voucher_type": "standard",
  "duration_hours": 24,
  "data_limit_mb": 1000,
  "speed_limit_kbps": 1024,
  "price": 15.0,
  "notes": "كرت يومي للعملاء العاديين"
}
```

**الحقول الاختيارية**:
- `data_limit_mb`: حد البيانات (null = غير محدود)
- `speed_limit_kbps`: حد السرعة
- `price`: السعر
- `notes`: ملاحظات

**الاستجابة الناجحة** (201):
```json
{
  "success": true,
  "message": "تم إنشاء الكرت بنجاح",
  "data": {
    "id": 157,
    "code": "WIFI-XYZ789",
    "voucher_type": "standard",
    "status": "active",
    "duration_hours": 24,
    "data_limit_mb": 1000,
    "speed_limit_kbps": 1024,
    "price": 15.0,
    "created_at": "2025-09-28T20:30:00Z",
    "expires_at": null,
    "qr_code_url": "/static/qr_codes/WIFI-XYZ789.png"
  }
}
```

---

### GET /api/vouchers/{id}
**الوصف**: الحصول على تفاصيل كرت محدد

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "code": "WIFI-ABC123",
    "voucher_type": "standard",
    "status": "used",
    "duration_hours": 24,
    "data_limit_mb": 1000,
    "data_used_mb": 450,
    "speed_limit_kbps": 1024,
    "price": 15.0,
    "created_at": "2025-09-28T10:00:00Z",
    "used_at": "2025-09-28T15:00:00Z",
    "session_start": "2025-09-28T15:00:00Z",
    "session_end": "2025-09-29T15:00:00Z",
    "client_ip": "192.168.1.100",
    "client_mac": "aa:bb:cc:dd:ee:ff",
    "session_token": "sess_abc123xyz",
    "qr_code_url": "/static/qr_codes/WIFI-ABC123.png"
  }
}
```

---

### PUT /api/vouchers/{id}
**الوصف**: تعديل كرت موجود

**المتطلبات** (جميع الحقول اختيارية):
```json
{
  "duration_hours": 48,
  "data_limit_mb": 2000,
  "speed_limit_kbps": 2048,
  "price": 25.0,
  "notes": "تم ترقية الكرت لمدة يومين"
}
```

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم تعديل الكرت بنجاح",
  "data": {
    // بيانات الكرت المحدثة
  }
}
```

---

### DELETE /api/vouchers/{id}
**الوصف**: حذف كرت (فقط الكروت غير المستخدمة)

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم حذف الكرت بنجاح"
}
```

**أخطاء محتملة**:
- `400`: لا يمكن حذف كرت مستخدم
- `404`: الكرت غير موجود

---

### POST /api/vouchers/batch
**الوصف**: إنشاء كروت متعددة

**المتطلبات**:
```json
{
  "quantity": 50,
  "voucher_type": "standard",
  "duration_hours": 24,
  "data_limit_mb": 1000,
  "speed_limit_kbps": 1024,
  "price": 15.0,
  "code_prefix": "EVENT-",
  "notes": "كروت للمؤتمر السنوي"
}
```

**الاستجابة الناجحة** (201):
```json
{
  "success": true,
  "message": "تم إنشاء 50 كرت بنجاح",
  "data": {
    "batch_id": "BATCH_20250928_203000",
    "quantity": 50,
    "vouchers": [
      {
        "id": 158,
        "code": "EVENT-001",
        "voucher_type": "standard"
      },
      // ... باقي الكروت
    ]
  }
}
```

---

### POST /api/vouchers/{id}/disable
**الوصف**: تعطيل كرت

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم تعطيل الكرت بنجاح"
}
```

---

### POST /api/vouchers/{id}/enable
**الوصف**: تفعيل كرت معطل

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم تفعيل الكرت بنجاح"
}
```

---

## 👥 إدارة المستخدمين

### GET /api/users
**الوصف**: الحصول على قائمة المستخدمين (مديرون فقط)

**المعاملات الاختيارية**:
- `role`: فلترة حسب الدور (`admin`, `operator`, `user`)
- `is_active`: فلترة حسب الحالة (`true`, `false`)
- `page`: رقم الصفحة
- `per_page`: عدد العناصر بالصفحة

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-09-28T20:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 5,
      "pages": 1
    }
  }
}
```

---

### POST /api/users
**الوصف**: إنشاء مستخدم جديد (مديرون فقط)

**المتطلبات**:
```json
{
  "username": "new_operator",
  "email": "operator@example.com",
  "password": "secure_password",
  "role": "operator",
  "is_active": true
}
```

**الاستجابة الناجحة** (201):
```json
{
  "success": true,
  "message": "تم إنشاء المستخدم بنجاح",
  "data": {
    "id": 6,
    "username": "new_operator",
    "email": "operator@example.com",
    "role": "operator",
    "is_active": true,
    "created_at": "2025-09-28T20:30:00Z"
  }
}
```

---

### PUT /api/users/{id}
**الوصف**: تعديل مستخدم موجود

**المتطلبات** (جميع الحقول اختيارية):
```json
{
  "email": "updated@example.com",
  "role": "admin",
  "is_active": false
}
```

---

### DELETE /api/users/{id}
**الوصف**: حذف مستخدم (لا يمكن حذف النفس)

---

## 🌐 إدارة الشبكات

### GET /api/networks
**الوصف**: الحصول على قائمة الشبكات المدارة

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "networks": [
      {
        "id": 1,
        "name": "WiFi-Guest",
        "ssid": "GuestNetwork",
        "description": "شبكة الضيوف",
        "is_active": true,
        "captive_portal_enabled": true,
        "created_at": "2025-09-01T00:00:00Z"
      }
    ]
  }
}
```

---

### GET /api/routers
**الوصف**: الحصول على قائمة أجهزة التوجيه

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "routers": [
      {
        "id": 1,
        "name": "راوتر الطابق الأول",
        "ip_address": "192.168.1.1",
        "brand": "MikroTik",
        "model": "RB750Gr3",
        "is_active": true,
        "last_seen": "2025-09-28T20:25:00Z",
        "status": "online"
      }
    ]
  }
}
```

---

### POST /api/routers
**الوصف**: إضافة جهاز توجيه جديد

**المتطلبات**:
```json
{
  "name": "راوتر الطابق الثاني",
  "ip_address": "192.168.1.2",
  "brand": "MikroTik",
  "model": "hAP ac²",
  "username": "admin",
  "password": "router_password",
  "api_port": 8728,
  "description": "جهاز توجيه للطابق الثاني"
}
```

---

### POST /api/routers/{id}/test
**الوصف**: اختبار الاتصال بجهاز التوجيه

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم الاتصال بجهاز التوجيه بنجاح",
  "data": {
    "response_time": 45,
    "router_info": {
      "version": "6.48.6",
      "board_name": "RB750Gr3",
      "uptime": "2w3d4h15m"
    }
  }
}
```

---

## 📊 الإحصائيات والتقارير

### GET /api/stats/dashboard
**الوصف**: إحصائيات لوحة التحكم الرئيسية

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "total_vouchers": 1250,
    "active_vouchers": 45,
    "used_vouchers": 892,
    "expired_vouchers": 313,
    "total_networks": 3,
    "total_routers": 2,
    "online_routers": 2,
    "current_sessions": 12,
    "total_data_consumed_gb": 1456.7,
    "revenue_total": 18750.0,
    "recent_vouchers": [
      {
        "id": 157,
        "code": "WIFI-XYZ789",
        "status": "active",
        "created_at": "2025-09-28T20:30:00Z"
      }
      // ... آخر 5 كروت
    ]
  }
}
```

---

### GET /api/stats/vouchers
**الوصف**: إحصائيات مفصلة للكروت

**المعاملات الاختيارية**:
- `period`: الفترة الزمنية (`today`, `week`, `month`, `year`)
- `voucher_type`: نوع الكرت

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "period": "month",
    "voucher_stats": {
      "total_created": 156,
      "total_used": 134,
      "usage_rate": 85.9,
      "average_session_duration": 18.5,
      "total_data_consumed_gb": 234.6,
      "revenue": 2340.0
    },
    "by_type": {
      "standard": {
        "count": 120,
        "revenue": 1800.0
      },
      "premium": {
        "count": 30,
        "revenue": 450.0
      },
      "vip": {
        "count": 6,
        "revenue": 90.0
      }
    },
    "daily_breakdown": [
      {
        "date": "2025-09-28",
        "created": 5,
        "used": 4,
        "revenue": 60.0
      }
      // ... باقي الأيام
    ]
  }
}
```

---

## 🎛️ التحكم في الشبكة

### GET /api/control/active
**الوصف**: الاتصالات النشطة الحالية

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "active_sessions": [
      {
        "voucher_code": "WIFI-ABC123",
        "client_ip": "192.168.1.100",
        "client_mac": "aa:bb:cc:dd:ee:ff",
        "session_start": "2025-09-28T15:00:00Z",
        "session_end": "2025-09-29T15:00:00Z",
        "time_remaining_minutes": 1380,
        "data_used_mb": 450,
        "data_limit_mb": 1000,
        "speed_limit_kbps": 1024,
        "router_id": 1
      }
    ],
    "total_active": 12
  }
}
```

---

### POST /api/control/disconnect
**الوصف**: قطع اتصال جلسة محددة

**المتطلبات**:
```json
{
  "voucher_code": "WIFI-ABC123",
  "reason": "انتهاء الصلاحية"
}
```

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم قطع الاتصال بنجاح"
}
```

---

### GET /api/control/monitor
**الوصف**: معلومات مراقبة الشبكة

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "data": {
    "network_status": "online",
    "total_bandwidth_usage": 45.6,
    "router_status": [
      {
        "router_id": 1,
        "status": "online",
        "cpu_usage": 15,
        "memory_usage": 45,
        "active_users": 8
      }
    ],
    "alerts": [
      {
        "type": "warning",
        "message": "استهلاك مرتفع للبيانات",
        "timestamp": "2025-09-28T20:25:00Z"
      }
    ]
  }
}
```

---

## 🔄 عمليات أخرى

### POST /api/voucher/redeem
**الوصف**: تفعيل كرت (للعملاء في Captive Portal)

**المتطلبات**:
```json
{
  "code": "WIFI-ABC123"
}
```

**الاستجابة الناجحة** (200):
```json
{
  "success": true,
  "message": "تم تفعيل الكرت بنجاح",
  "data": {
    "session_token": "sess_abc123xyz",
    "duration_hours": 24,
    "data_limit_mb": 1000,
    "speed_limit_kbps": 1024,
    "session_end": "2025-09-29T15:00:00Z"
  }
}
```

---

### GET /api/reports/export
**الوصف**: تصدير التقارير

**المعاملات**:
- `type`: نوع التقرير (`vouchers`, `users`, `revenue`)
- `format`: صيغة التصدير (`csv`, `excel`, `pdf`)
- `period`: الفترة الزمنية

**مثال**:
```
GET /api/reports/export?type=vouchers&format=csv&period=month
```

**الاستجابة** (200):
- Headers: `Content-Type: text/csv`
- Body: ملف CSV

---

## معالجة الأخطاء العامة

### هيكل الأخطاء
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

### أكواد الأخطاء الشائعة
- `VALIDATION_ERROR`: خطأ في البيانات المرسلة
- `AUTHENTICATION_REQUIRED`: مطلوب تسجيل دخول
- `PERMISSION_DENIED`: لا توجد صلاحية
- `RESOURCE_NOT_FOUND`: المورد غير موجود
- `DUPLICATE_RESOURCE`: مورد مكرر
- `RATE_LIMIT_EXCEEDED`: تجاوز حد الطلبات
- `SERVER_ERROR`: خطأ داخلي في الخادم

---

**💡 نصيحة**: استخدم أدوات مثل Postman أو curl لاختبار API endpoints قبل التكامل في تطبيقك.