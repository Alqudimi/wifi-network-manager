# 🏗️ نظرة عامة على معمارية النظام

## مقدمة

نظام إدارة شبكات Wi-Fi مصمم بمعمارية حديثة ومرنة تدعم التوسع والصيانة السهلة. يتبع النظام نمط MVC (Model-View-Controller) مع تصميم modular يسمح بإضافة ميزات جديدة بسهولة.

## المعمارية العامة

```
┌─────────────────────────────────────────────────────┐
│                 طبقة العرض (Frontend)                │
│  HTML5 + CSS3 + JavaScript (Vanilla ES6+)          │
│  واجهة عربية بدعم RTL + تصميم متجاوب                │
└─────────────────────────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │   Flask App   │
                    │   (Backend)   │
                    └───────┬───────┘
                            │
┌─────────────────────────────────────────────────────┐
│                Flask Application Layer               │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │    Auth     │  │  Vouchers   │  │   Network   │  │
│  │ Blueprints  │  │ Blueprints  │  │ Blueprints  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │    Admin    │  │   Users     │  │   Control   │  │
│  │ Blueprints  │  │ Blueprints  │  │ Blueprints  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────┐
│                Business Logic Layer                 │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │    Utils    │  │   Models    │  │  Services   │  │
│  │             │  │             │  │             │  │
│  │ • Auth      │  │ • User      │  │ • Network   │  │
│  │ • QR Gen    │  │ • Voucher   │  │   Monitor   │  │
│  │ • Router    │  │ • Network   │  │ • Router    │  │
│  │   Manager   │  │ • Router    │  │   Manager   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────┐
│                 Data Access Layer                   │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ SQLAlchemy  │  │   Redis     │  │    File     │  │
│  │     ORM     │  │   Cache     │  │   Storage   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────┐
│                   Storage Layer                     │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ PostgreSQL  │  │   Redis     │  │  File Sys   │  │
│  │ / SQLite    │  │   Server    │  │  (Static)   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────┐
│              External Integration Layer             │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  MikroTik   │  │  Ubiquiti   │  │    Cisco    │  │
│  │   Routers   │  │  Controllers│  │   Devices   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

## المكونات الأساسية

### 1. طبقة العرض (Presentation Layer)

#### التقنيات المستخدمة
- **HTML5**: هيكل الصفحات مع دعم Semantic HTML
- **CSS3**: تصميم متجاوب مع Grid وFlexbox
- **JavaScript ES6+**: تفاعل ديناميكي بدون frameworks خارجية
- **Arabic RTL**: دعم كامل للنصوص العربية من اليمين لليسار

#### الملفات والمجلدات
```
templates/
├── base.html              # القالب الأساسي
├── dashboard.html         # لوحة التحكم
├── login.html            # صفحة تسجيل الدخول
├── vouchers.html         # إدارة الكروت
├── networks.html         # إدارة الشبكات
├── users.html           # إدارة المستخدمين
├── network_control.html  # التحكم في الشبكة
└── captive_portal.html   # بوابة الدخول للعملاء

static/
├── css/
│   └── style.css         # ملف الأنماط الرئيسي
├── js/
│   ├── app.js           # الوظائف العامة
│   ├── dashboard.js     # وظائف لوحة التحكم
│   ├── vouchers.js      # وظائف إدارة الكروت
│   └── network_control.js # وظائف التحكم بالشبكة
└── uploads/             # الملفات المرفوعة
```

### 2. طبقة التطبيق (Application Layer)

#### Flask Application
```python
# app.py - النقطة الرئيسية للتطبيق
from flask import Flask
from config import Config
from database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # تهيئة الإضافات
    db.init_app(app)
    
    # تسجيل البلوبرينتس
    register_blueprints(app)
    
    return app
```

#### نظام البلوبرينتس (Blueprints)
```
routes/
├── auth.py              # المصادقة وتسجيل الدخول
├── admin.py             # إدارة النظام
├── vouchers.py          # إدارة الكروت
├── networks.py          # إدارة الشبكات
├── network_control.py   # التحكم في الشبكة
└── __init__.py
```

### 3. طبقة المنطق التجاري (Business Logic Layer)

#### النماذج (Models)
```
models/
├── user.py              # نموذج المستخدمين
├── voucher.py           # نموذج الكروت
├── network.py           # نموذج الشبكات
├── router.py            # نموذج أجهزة التوجيه
└── __init__.py
```

#### المرافق (Utils)
```
utils/
├── auth.py              # وظائف المصادقة
├── qr_generator.py      # إنشاء رموز QR
├── router_manager.py    # إدارة أجهزة التوجيه
├── network_manager.py   # إدارة الشبكة
└── __init__.py
```

### 4. طبقة الوصول للبيانات (Data Access Layer)

#### SQLAlchemy ORM
```python
# database.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db():
    """تهيئة قاعدة البيانات"""
    db.create_all()
```

#### نماذج البيانات الأساسية
- **User**: المستخدمين والصلاحيات
- **Voucher**: الكروت وخصائصها
- **Network**: الشبكات المدارة
- **Router**: أجهزة التوجيه المتصلة

## التدفق العام للبيانات

### 1. طلب مستخدم جديد
```
مستخدم → Flask Route → Validation → Business Logic → Database → Response
```

### 2. إنشاء كرت جديد
```
UI Request → /api/vouchers [POST] → Voucher.create() → QR Generation → Database Save → JSON Response
```

### 3. تفعيل كرت
```
Captive Portal → /api/voucher/redeem [POST] → Voucher.validate() → Router API → Network Access → Session Tracking
```

## أنماط التصميم المستخدمة

### 1. Model-View-Controller (MVC)
- **Model**: SQLAlchemy models
- **View**: Jinja2 templates + JavaScript
- **Controller**: Flask routes and blueprints

### 2. Repository Pattern
```python
class VoucherRepository:
    @staticmethod
    def get_active_vouchers():
        return Voucher.query.filter_by(status='active').all()
    
    @staticmethod
    def create_voucher(data):
        voucher = Voucher(**data)
        db.session.add(voucher)
        db.session.commit()
        return voucher
```

### 3. Factory Pattern
```python
def create_router_manager(router_type):
    if router_type == 'MikroTik':
        return MikroTikManager()
    elif router_type == 'Ubiquiti':
        return UbiquitiManager()
    elif router_type == 'Cisco':
        return CiscoManager()
```

### 4. Observer Pattern
```python
class NetworkMonitor:
    def __init__(self):
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify_observers(self, event):
        for observer in self.observers:
            observer.update(event)
```

## إدارة الحالة (State Management)

### 1. جلسات المستخدمين
```python
# JWT-based session management
from flask_jwt_extended import create_access_token, verify_jwt_in_request

def login_user(username, password):
    user = User.authenticate(username, password)
    if user:
        token = create_access_token(identity=user.id)
        return {'token': token, 'user': user.to_dict()}
```

### 2. حالة الكروت
```
نشط (Active) → مستخدم (Used) → منتهي (Expired)
     ↓              ↓             ↓
   معطل        قطع اتصال      أرشفة
```

### 3. مراقبة الشبكة
```python
class SessionTracker:
    def __init__(self):
        self.active_sessions = {}
    
    def add_session(self, voucher_code, client_ip):
        self.active_sessions[voucher_code] = {
            'ip': client_ip,
            'start_time': datetime.utcnow(),
            'data_used': 0
        }
```

## الأمان والحماية

### 1. طبقات الأمان
```
Input Validation → Authentication → Authorization → Data Encryption → Audit Logging
```

### 2. المصادقة متعددة المستويات
- **Level 1**: Basic username/password
- **Level 2**: JWT tokens with expiration
- **Level 3**: Role-based access control (RBAC)
- **Level 4**: API rate limiting

### 3. حماية البيانات
```python
# تشفير كلمات المرور
from werkzeug.security import generate_password_hash, check_password_hash

# تشفير JWT
from flask_jwt_extended import JWTManager

# حماية CSRF
from flask_wtf.csrf import CSRFProtect
```

## التوسع والأداء (Scalability & Performance)

### 1. استراتيجيات التوسع الأفقي
- **Database Sharding**: تقسيم قاعدة البيانات
- **Load Balancing**: توزيع الأحمال
- **Caching**: التخزين المؤقت مع Redis
- **CDN**: شبكة توصيل المحتوى

### 2. تحسين الأداء
```python
# Connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

# Query optimization
@cache.memoize(timeout=300)
def get_dashboard_stats():
    return calculate_statistics()
```

### 3. مراقبة الأداء
- **Application Performance Monitoring (APM)**
- **Database query monitoring**
- **Memory usage tracking**
- **Response time analysis**

## التكامل مع الأنظمة الخارجية

### 1. أجهزة التوجيه
```python
# MikroTik Integration
import librouteros

# Ubiquiti Integration
import requests

# Cisco Integration
import paramiko
```

### 2. خدمات خارجية
- **Email Services**: SMTP للإشعارات
- **SMS Gateways**: لإرسال أكواد التحقق
- **Payment Gateways**: لمعالجة المدفوعات
- **Analytics Services**: لتحليل الاستخدام

## إدارة الأخطاء والاستثناءات

### 1. هيكل معالجة الأخطاء
```python
class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

@app.errorhandler(APIError)
def handle_api_error(error):
    response = {'error': error.message}
    if error.payload:
        response.update(error.payload)
    return jsonify(response), error.status_code
```

### 2. تسجيل الأحداث
```python
import logging

# إعداد ملفات السجلات
logging.basicConfig(
    filename='logs/wifi_manager.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

## اختبار النظام

### 1. أنواع الاختبارات
- **Unit Tests**: اختبار الوحدات المنفردة
- **Integration Tests**: اختبار التكامل
- **End-to-End Tests**: اختبار النظام الكامل
- **Performance Tests**: اختبار الأداء

### 2. إطار الاختبار
```python
import unittest
from app import create_app, db

class VoucherTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def test_create_voucher(self):
        # اختبار إنشاء كرت جديد
        pass
```

## النشر والإنتاج

### 1. بيئات النشر
- **Development**: للتطوير والاختبار
- **Staging**: للاختبار النهائي
- **Production**: للاستخدام الفعلي

### 2. أدوات النشر
- **Docker**: للحاويات
- **Nginx**: كخادم ويب أمامي
- **Gunicorn**: كخادم WSGI
- **Supervisor**: لإدارة العمليات

---

**📋 ملاحظة**: هذه المعمارية مصممة لتكون مرنة وقابلة للتوسع. يمكن تعديل أي مكون حسب احتياجاتك المحددة.