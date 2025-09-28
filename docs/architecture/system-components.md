# 🧩 مكونات النظام

## نظرة عامة

نظام إدارة شبكات Wi-Fi يتكون من عدة مكونات متكاملة تعمل معاً لتوفير حل شامل لإدارة الشبكات اللاسلكية.

## المكونات الأساسية

### 1. Flask Application Core
```python
# app.py - القلب النابض للتطبيق
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
db = SQLAlchemy(app)
jwt = JWTManager(app)
```

**المسؤوليات:**
- إدارة طلبات HTTP/HTTPS
- توجيه الطلبات للمعالجات المناسبة
- إدارة الجلسات والمصادقة
- معالجة الأخطاء والاستثناءات

**التقنيات المستخدمة:**
- Flask 2.3+ كإطار العمل الأساسي
- Werkzeug للتعامل مع WSGI
- Jinja2 لمحرك القوالب

### 2. Database Layer
```
قاعدة البيانات
├── Models (SQLAlchemy ORM)
│   ├── User
│   ├── Voucher  
│   ├── Network
│   ├── Router
│   └── SystemLog
├── Migrations (Flask-Migrate)
└── Connection Pool
```

**المسؤوليات:**
- تخزين البيانات بشكل آمن ومنظم
- إدارة العلاقات بين الكيانات
- ضمان سلامة البيانات (ACID)
- تحسين الأداء مع الفهرسة

**أنواع البيانات المخزنة:**
- بيانات المستخدمين والمصادقة
- كروت Wi-Fi وحالتها
- إعدادات الشبكات وأجهزة التوجيه
- سجلات النشاط والإحصائيات

### 3. Authentication & Authorization
```python
# utils/auth.py
class AuthManager:
    def authenticate_user(username, password)
    def generate_jwt_token(user)
    def verify_token(token)
    def check_permissions(user, resource)
```

**المكونات الفرعية:**
- **JWT Manager**: إدارة رموز الدخول
- **Password Hasher**: تشفير كلمات المرور
- **Permission Checker**: فحص الصلاحيات
- **Session Manager**: إدارة جلسات المستخدمين

**مستويات الأمان:**
- تشفير كلمات المرور بـ bcrypt
- رموز JWT مع انتهاء صلاحية
- تحديد الصلاحيات حسب الدور
- حماية من CSRF attacks

### 4. Voucher Management System
```python
# models/voucher.py
class Voucher:
    - code: رمز الكرت الفريد
    - voucher_type: نوع الكرت (standard/premium/vip)
    - duration_hours: مدة الصلاحية
    - data_limit_mb: حد البيانات
    - speed_limit_kbps: حد السرعة
    - status: الحالة الحالية
```

**وظائف أساسية:**
- إنشاء كروت فردية أو متعددة
- إدارة دورة حياة الكرت
- تتبع الاستخدام والاستهلاك
- إنشاء رموز QR تلقائياً

**حالات الكرت:**
1. **Active**: جاهز للاستخدام
2. **Used**: قيد الاستخدام
3. **Expired**: انتهت الصلاحية
4. **Disabled**: معطل يدوياً

### 5. Network Control Engine
```python
# utils/network_manager.py
class NetworkManager:
    def monitor_active_sessions()
    def disconnect_session(voucher_code)
    def update_session_limits(session_id, limits)
    def collect_usage_statistics()
```

**المهام الأساسية:**
- مراقبة الاتصالات النشطة
- تطبيق حدود السرعة والبيانات
- قطع الاتصالات عند الحاجة
- جمع إحصائيات الاستخدام

**معلومات المراقبة:**
- عنوان IP للعميل
- كمية البيانات المستهلكة
- مدة الاتصال
- سرعة النقل الحالية

### 6. Router Integration Layer
```python
# utils/router_manager.py
class RouterManager:
    def get_router_handler(router_type)
    def test_connection(router_config)
    def sync_voucher_data(vouchers)
    def get_router_statistics()
```

**الأجهزة المدعومة:**

#### MikroTik Handler
```python
class MikroTikManager:
    def connect_api()
    def create_hotspot_user()
    def get_active_users()
    def update_user_profile()
```

#### Ubiquiti Handler  
```python
class UbiquitiManager:
    def authenticate_controller()
    def manage_guest_portal()
    def get_client_statistics()
    def update_firewall_rules()
```

#### Cisco Handler
```python
class CiscoManager:
    def connect_ssh()
    def configure_web_auth()
    def monitor_associations()
    def update_access_lists()
```

### 7. QR Code Generator
```python
# utils/qr_generator.py
class QRCodeGenerator:
    def generate_voucher_qr(voucher_code, portal_url)
    def customize_qr_design(logo, colors)
    def batch_generate_qr_codes(vouchers)
```

**المواصفات:**
- حجم قابل للتخصيص (100x100 إلى 500x500)
- دعم إضافة شعار في المنتصف
- تخصيص الألوان والتصميم
- تصدير بصيغ PNG/JPG/SVG

### 8. Caching System
```python
# utils/cache_manager.py
class CacheManager:
    def cache_dashboard_stats()
    def cache_user_sessions()
    def invalidate_cache(key_pattern)
    def get_cache_statistics()
```

**طبقات التخزين المؤقت:**
- **Application Cache**: إحصائيات وبيانات ثقيلة
- **Session Cache**: جلسات المستخدمين
- **Query Cache**: نتائج استعلامات قاعدة البيانات
- **Static Cache**: ملفات CSS/JS/Images

### 9. API Layer
```python
# routes/api/
├── auth.py      # نقاط المصادقة
├── vouchers.py  # إدارة الكروت
├── networks.py  # إدارة الشبكات
├── users.py     # إدارة المستخدمين
└── control.py   # التحكم في الشبكة
```

**مواصفات API:**
- RESTful architecture
- JSON request/response
- JWT authentication
- Rate limiting
- Error handling standardized

### 10. Background Tasks
```python
# tasks/
├── cleanup_tasks.py     # تنظيف البيانات القديمة
├── monitoring_tasks.py  # مراقبة الأجهزة
├── backup_tasks.py      # النسخ الاحتياطية
└── notification_tasks.py # الإشعارات
```

**المهام المجدولة:**
- تنظيف الكروت المنتهية
- فحص حالة أجهزة التوجيه
- إنشاء نسخ احتياطية
- إرسال تقارير دورية

## التكامل بين المكونات

### تدفق إنشاء كرت جديد
```
1. UI Request → 2. Auth Check → 3. Voucher Creation → 4. QR Generation → 5. Router Sync → 6. Response
```

### تدفق تفعيل كرت
```
1. Captive Portal → 2. Voucher Validation → 3. Session Creation → 4. Router Configuration → 5. Network Access
```

### تدفق مراقبة الشبكة
```
1. Background Monitor → 2. Router Data Collection → 3. Database Update → 4. Cache Refresh → 5. UI Update
```

## إدارة الموارد

### Memory Management
```python
# تحسين استخدام الذاكرة
import gc
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(data):
    # عملية حسابية مكلفة
    return result

# تنظيف دوري للذاكرة
def cleanup_memory():
    gc.collect()
```

### Connection Pooling
```python
# إدارة اتصالات قاعدة البيانات
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'pool_timeout': 30,
    'max_overflow': 40
}
```

## مراقبة الصحة

### Health Check System
```python
@app.route('/health')
def health_check():
    components = {
        'database': check_database_health(),
        'cache': check_cache_health(),
        'routers': check_routers_health(),
        'disk_space': check_disk_space(),
        'memory': check_memory_usage()
    }
    
    overall_health = all(components.values())
    
    return jsonify({
        'status': 'healthy' if overall_health else 'unhealthy',
        'components': components,
        'timestamp': datetime.utcnow().isoformat()
    })
```

### Component Monitoring
```python
class ComponentMonitor:
    def monitor_database_performance()
    def monitor_router_connectivity()
    def monitor_memory_usage()
    def monitor_cache_hit_ratio()
    def generate_health_report()
```

## توسيع النظام

### Plugin Architecture
```python
# plugins/
├── custom_routers/     # دعم أجهزة إضافية
├── payment_gateways/   # بوابات الدفع
├── sms_providers/      # موفري SMS
└── analytics/          # أدوات التحليل
```

### API Extensions
```python
# extensions/api/
├── mobile_app.py       # API للتطبيقات المحمولة
├── third_party.py      # تكامل أنظمة خارجية
└── webhooks.py         # Webhook notifications
```

### Microservices Ready
النظام مصمم للتحول لـ microservices:
- مكونات منفصلة ومستقلة
- APIs محددة بوضوح
- قواعد بيانات قابلة للفصل
- حالة مشتركة محدودة

---

**📋 ملاحظة**: كل مكون مصمم ليكون قابلاً للاختبار والصيانة والتوسع بشكل مستقل.