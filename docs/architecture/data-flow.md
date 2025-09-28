# 🔄 تدفق البيانات

## نظرة عامة

هذا المستند يوضح كيف تتدفق البيانات عبر النظام من نقطة الدخول حتى النتيجة النهائية.

## التدفقات الأساسية

### 1. تدفق تسجيل الدخول
```
المستخدم → واجهة تسجيل الدخول → Flask Route → Auth Manager → Database → JWT Creation → Response
```

#### خطوات مفصلة:
```mermaid
sequenceDiagram
    participant U as المستخدم
    participant UI as واجهة المستخدم
    participant API as Flask API
    participant Auth as Auth Manager
    participant DB as قاعدة البيانات
    participant JWT as JWT Manager

    U->>UI: إدخال اسم مستخدم/كلمة مرور
    UI->>API: POST /api/auth/login
    API->>Auth: validate_credentials()
    Auth->>DB: SELECT user WHERE username=?
    DB-->>Auth: user_data
    Auth->>Auth: check_password_hash()
    Auth->>JWT: generate_token(user)
    JWT-->>API: access_token
    API-->>UI: JSON response with token
    UI-->>U: تحويل للوحة التحكم
```

### 2. تدفق إنشاء كرت جديد
```
طلب إنشاء → التحقق من الصلاحيات → إنشاء الكرت → إنشاء QR → مزامنة الراوتر → رد JSON
```

#### مخطط التدفق:
```mermaid
flowchart TD
    A[طلب إنشاء كرت] --> B{فحص الصلاحيات}
    B -->|مرفوض| C[رد بخطأ 403]
    B -->|مقبول| D[تولید کود فریگ]
    D --> E[حفظ في قاعدة البيانات]
    E --> F[إنشاء رمز QR]
    F --> G[حفظ صورة QR]
    G --> H{مزامنة مع الراوتر}
    H -->|نجح| I[رد بالنجاح + بيانات الكرت]
    H -->|فشل| J[تسجيل الخطأ + رد بالنجاح*]
    
    style C fill:#ffcccc
    style I fill:#ccffcc
    style J fill:#ffffcc
```

### 3. تدفق تفعيل كرت (Captive Portal)
```
عميل يتصل بـ WiFi → يُحوّل لصفحة التفعيل → إدخال الكود → التحقق → إنشاء جلسة → وصول للإنترنت
```

#### التسلسل الزمني:
```mermaid
sequenceDiagram
    participant Client as عميل WiFi
    participant Router as جهاز التوجيه
    participant Portal as Captive Portal
    participant API as WiFi Manager API
    participant DB as قاعدة البيانات

    Client->>Router: محاولة الاتصال بالإنترنت
    Router->>Portal: إعادة توجيه لصفحة التفعيل
    Portal->>Client: عرض نموذج إدخال الكود
    Client->>Portal: إدخال كود الكرت
    Portal->>API: POST /api/voucher/redeem
    API->>DB: SELECT voucher WHERE code=?
    DB-->>API: voucher_data
    API->>API: validate_voucher()
    API->>DB: UPDATE voucher SET status='used'
    API->>Router: configure_client_access()
    Router-->>API: access_granted
    API-->>Portal: success_response
    Portal-->>Client: رسالة نجاح + وصول للإنترنت
```

### 4. تدفق مراقبة الشبكة
```
مهمة مراقبة → جمع بيانات من الراوترات → تحديث قاعدة البيانات → تحديث Cache → إشعار الواجهة
```

#### عملية المراقبة:
```mermaid
graph LR
    A[Background Task] --> B[Router 1]
    A --> C[Router 2]
    A --> D[Router N]
    
    B --> E[جمع الإحصائيات]
    C --> E
    D --> E
    
    E --> F[معالجة البيانات]
    F --> G[تحديث قاعدة البيانات]
    G --> H[تحديث Cache]
    H --> I[WebSocket Notification]
    I --> J[تحديث الواجهة]
```

## تدفقات البيانات المتقدمة

### 5. تدفق إنشاء كروت متعددة
```python
# نمط Batch Processing
def create_bulk_vouchers(quantity, config):
    vouchers = []
    for i in range(quantity):
        voucher = create_single_voucher(config, batch_id)
        vouchers.append(voucher)
        
        # إنشاء QR كل 10 كروت
        if i % 10 == 0:
            generate_qr_batch(vouchers[-10:])
    
    # مزامنة مع الراوترات
    sync_vouchers_to_routers(vouchers)
    
    return vouchers
```

### 6. تدفق معالجة الأخطاء
```mermaid
flowchart TD
    A[حدوث خطأ] --> B{نوع الخطأ}
    B -->|خطأ تطبيق| C[تسجيل في ملف السجل]
    B -->|خطأ قاعدة بيانات| D[محاولة إعادة الاتصال]
    B -->|خطأ راوتر| E[وضع في قائمة الأخطاء]
    
    C --> F[إرسال استجابة خطأ للمستخدم]
    D --> G{نجحت إعادة المحاولة؟}
    E --> H[إشعار المشرف]
    
    G -->|نعم| I[متابعة العملية]
    G -->|لا| J[تسجيل فشل + إشعار]
    
    F --> K[عرض رسالة خطأ]
    H --> L[محاولة مع راوتر آخر]
    J --> K
    I --> M[عملية ناجحة]
    L --> N{متوفر راوتر بديل؟}
    
    N -->|نعم| O[تحويل العملية]
    N -->|لا| P[فشل العملية]
```

## تدفق البيانات في الوقت الفعلي

### 7. Real-time Updates
```javascript
// Frontend WebSocket handling
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'new_voucher':
            updateVouchersList(data.voucher);
            break;
        case 'session_update':
            updateActiveSessionsTable(data.session);
            break;
        case 'router_status':
            updateRouterStatus(data.router_id, data.status);
            break;
    }
};
```

```python
# Backend WebSocket broadcasting
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

def broadcast_voucher_created(voucher):
    socketio.emit('new_voucher', {
        'type': 'new_voucher',
        'voucher': voucher.to_dict()
    }, room='admins')

def broadcast_session_update(session):
    socketio.emit('session_update', {
        'type': 'session_update', 
        'session': session.to_dict()
    }, room='operators')
```

### 8. تدفق التخزين المؤقت
```mermaid
graph TD
    A[طلب بيانات] --> B{موجود في Cache؟}
    B -->|نعم| C[إرجاع من Cache]
    B -->|لا| D[جلب من قاعدة البيانات]
    D --> E[حفظ في Cache]
    E --> F[إرجاع البيانات]
    
    G[تحديث بيانات] --> H[تحديث قاعدة البيانات]
    H --> I[مسح Cache المرتبط]
    I --> J[Cache جديد عند الطلب التالي]
    
    style C fill:#ccffcc
    style F fill:#ccffcc
```

## تدفق إدارة الجلسات

### 9. دورة حياة الجلسة
```python
class SessionLifecycle:
    def create_session(voucher_code, client_ip):
        # 1. التحقق من صحة الكرت
        voucher = validate_voucher(voucher_code)
        
        # 2. إنشاء جلسة جديدة
        session = Session(
            voucher=voucher,
            client_ip=client_ip,
            start_time=datetime.utcnow(),
            end_time=voucher.calculate_end_time()
        )
        
        # 3. تكوين الراوتر
        configure_router_access(session)
        
        # 4. بدء المراقبة
        start_session_monitoring(session)
        
        return session
    
    def monitor_session(session):
        while session.is_active():
            # جمع إحصائيات الاستخدام
            usage = collect_usage_stats(session)
            
            # فحص الحدود
            if usage.data_exceeded() or usage.time_exceeded():
                terminate_session(session)
                break
            
            # تحديث البيانات
            update_session_stats(session, usage)
            
            sleep(30)  # مراقبة كل 30 ثانية
```

### 10. تدفق النسخ الاحتياطية
```mermaid
sequenceDiagram
    participant Scheduler as مجدول المهام
    participant Backup as خدمة النسخ الاحتياطية
    participant DB as قاعدة البيانات
    participant Storage as مخزن الملفات
    participant Cloud as التخزين السحابي

    Scheduler->>Backup: تشغيل مهمة النسخ الاحتياطية
    Backup->>DB: إنشاء دمپ لقاعدة البيانات
    DB-->>Backup: ملف SQL
    Backup->>Backup: ضغط الملف
    Backup->>Storage: حفظ محلياً
    Backup->>Cloud: رفع للتخزين السحابي
    Cloud-->>Backup: تأكيد الرفع
    Backup->>Storage: حذف النسخ القديمة
    Backup->>Scheduler: تأكيد اكتمال المهمة
```

## تدفق معالجة الأخطاء المتقدمة

### 11. Error Recovery Patterns
```python
class ErrorRecoveryManager:
    def handle_database_error(self, error):
        if "connection lost" in str(error):
            # إعادة تأسيس الاتصال
            self.reconnect_database()
            return "retry"
        elif "deadlock" in str(error):
            # إعادة المحاولة بعد فترة
            time.sleep(random.uniform(0.1, 0.5))
            return "retry"
        else:
            # تسجيل وإبلاغ
            self.log_error(error)
            self.notify_admin(error)
            return "fail"
    
    def handle_router_error(self, router, error):
        # محاولة راوتر بديل
        backup_router = self.find_backup_router(router)
        if backup_router:
            return self.failover_to_backup(backup_router)
        
        # وضع الراوتر في قائمة الصيانة
        self.mark_router_down(router)
        return "partial_failure"
```

### 12. تدفق تحليل الأداء
```python
class PerformanceAnalyzer:
    def analyze_request_flow(self, request_id):
        timeline = []
        
        # جمع نقاط القياس
        timeline.append(("request_start", self.get_timestamp()))
        timeline.append(("auth_check", self.get_timestamp()))
        timeline.append(("database_query", self.get_timestamp()))
        timeline.append(("business_logic", self.get_timestamp()))
        timeline.append(("response_sent", self.get_timestamp()))
        
        # تحليل الاختناقات
        bottlenecks = self.identify_bottlenecks(timeline)
        
        # إنشاء توصيات التحسين
        recommendations = self.generate_recommendations(bottlenecks)
        
        return {
            'timeline': timeline,
            'bottlenecks': bottlenecks,
            'recommendations': recommendations
        }
```

## تحسين تدفق البيانات

### نصائح للأداء
1. **استخدم Connection Pooling** لقاعدة البيانات
2. **فعّل Caching** للبيانات المتكررة
3. **استخدم Async Operations** للعمليات البطيئة
4. **راقب Memory Usage** وقم بالتنظيف الدوري
5. **استخدم Batch Processing** للعمليات المتعددة

### مراقبة التدفق
```python
# تتبع تدفق البيانات
import logging
from functools import wraps

def trace_data_flow(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_id = generate_request_id()
        
        logging.info(f"[{request_id}] Starting {func.__name__}")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logging.info(f"[{request_id}] Completed {func.__name__} in {duration:.3f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"[{request_id}] Failed {func.__name__} after {duration:.3f}s: {e}")
            raise
    
    return wrapper
```

---

**🔄 خلاصة**: فهم تدفق البيانات ضروري لتحسين الأداء وحل المشاكل بفعالية!