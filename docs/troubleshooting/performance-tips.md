# ⚡ نصائح تحسين الأداء

## تحسين قاعدة البيانات

### فهرسة ذكية
```sql
-- فهارس للاستعلامات الشائعة
CREATE INDEX CONCURRENTLY idx_vouchers_active_status 
ON vouchers(status) WHERE status = 'active';

CREATE INDEX CONCURRENTLY idx_vouchers_recent 
ON vouchers(created_at DESC) WHERE created_at > NOW() - INTERVAL '30 days';

-- إحصائيات الجداول
ANALYZE vouchers;
ANALYZE users;
ANALYZE routers;
```

### تحسين الاستعلامات
```python
# استخدام eager loading لتجنب N+1 queries
vouchers = Voucher.query.options(
    joinedload(Voucher.created_by_user)
).filter_by(status='active').all()

# استخدام pagination للبيانات الكبيرة
vouchers = Voucher.query.paginate(
    page=page, per_page=50, error_out=False
)

# استخدام raw SQL للاستعلامات المعقدة
stats = db.session.execute("""
    SELECT voucher_type, COUNT(*), AVG(data_used_mb)
    FROM vouchers 
    WHERE created_at > NOW() - INTERVAL '7 days'
    GROUP BY voucher_type
""").fetchall()
```

## تحسين التطبيق

### التخزين المؤقت
```python
from flask_caching import Cache

cache = Cache()
cache.init_app(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@cache.cached(timeout=300, key_prefix='dashboard_stats')
def get_dashboard_statistics():
    # حساب الإحصائيات المعقدة
    return expensive_calculation()

@cache.memoize(timeout=600)
def get_user_vouchers(user_id):
    return Voucher.query.filter_by(created_by=user_id).all()
```

### تحسين الاستجابة
```python
# استخدام Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_recycle=3600,
    pool_pre_ping=True
)

# ضغط الاستجابات
from flask_compress import Compress
Compress(app)

# تحسين JSON responses
from flask.json import JSONEncoder
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder
```

## تحسين الشبكة

### CDN للملفات الثابتة
```nginx
location /static/ {
    alias /opt/wifi-manager/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary Accept-Encoding;
    
    # ضغط الملفات
    gzip on;
    gzip_types text/css application/javascript image/svg+xml;
}
```

### تحسين NGINX
```nginx
# تحسين Worker processes
worker_processes auto;
worker_connections 1024;

# تحسين Buffers
client_body_buffer_size 128k;
client_max_body_size 16m;
client_header_buffer_size 1k;
large_client_header_buffers 4 4k;

# تحسين Timeouts
client_body_timeout 12;
client_header_timeout 12;
keepalive_timeout 15;
send_timeout 10;

# تفعيل HTTP/2
listen 443 ssl http2;
```

## مراقبة الأداء

### Application Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        if duration > 1.0:  # أكثر من ثانية واحدة
            app.logger.warning(f"Slow function: {func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper

@monitor_performance
def expensive_operation():
    # عملية مكلفة
    pass
```

### Database Query Monitoring
```python
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.5:  # أكثر من نصف ثانية
        app.logger.warning(f"Slow query: {total:.3f}s - {statement[:100]}...")
```

## تحسين الذاكرة

### إدارة الذاكرة
```python
import gc
import psutil
from flask import g

@app.before_request
def before_request():
    g.start_memory = psutil.Process().memory_info().rss

@app.after_request
def after_request(response):
    if hasattr(g, 'start_memory'):
        current_memory = psutil.Process().memory_info().rss
        memory_diff = current_memory - g.start_memory
        
        if memory_diff > 50 * 1024 * 1024:  # أكثر من 50MB
            app.logger.warning(f"High memory usage: {memory_diff / 1024 / 1024:.1f}MB")
            gc.collect()  # تنظيف الذاكرة
    
    return response
```

### تنظيف البيانات
```python
from celery import Celery
from datetime import datetime, timedelta

celery = Celery('wifi_manager')

@celery.task
def cleanup_expired_vouchers():
    """تنظيف الكروت المنتهية القديمة"""
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    
    expired_count = Voucher.query.filter(
        Voucher.status == 'expired',
        Voucher.expires_at < cutoff_date
    ).delete()
    
    db.session.commit()
    
    return f"Cleaned up {expired_count} expired vouchers"

@celery.task
def optimize_database():
    """تحسين قاعدة البيانات دورياً"""
    db.session.execute("VACUUM ANALYZE")
    db.session.commit()
    
    return "Database optimized"

# جدولة المهام
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'cleanup-expired-vouchers': {
        'task': 'cleanup_expired_vouchers',
        'schedule': crontab(hour=2, minute=0),  # كل يوم في 2 صباحاً
    },
    'optimize-database': {
        'task': 'optimize_database', 
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # كل أحد في 3 صباحاً
    },
}
```

## تحسين أجهزة التوجيه

### Connection Pooling للـ APIs
```python
import threading
from queue import Queue

class RouterConnectionPool:
    def __init__(self, router_config, pool_size=5):
        self.router_config = router_config
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        
        # إنشاء اتصالات مسبقة
        for _ in range(pool_size):
            connection = self.create_connection()
            self.pool.put(connection)
    
    def get_connection(self):
        return self.pool.get()
    
    def return_connection(self, connection):
        if connection and connection.is_alive():
            self.pool.put(connection)
        else:
            # إنشاء اتصال جديد إذا كان التالف
            new_connection = self.create_connection()
            self.pool.put(new_connection)
```

### Batch Operations
```python
def update_multiple_vouchers_on_router(vouchers, router):
    """تحديث عدة كروت دفعة واحدة"""
    commands = []
    
    for voucher in vouchers:
        if voucher.status == 'active':
            commands.append(f"/ip hotspot user add name={voucher.code} password={voucher.code}")
        elif voucher.status == 'disabled':
            commands.append(f"/ip hotspot user remove [find name={voucher.code}]")
    
    # إرسال جميع الأوامر دفعة واحدة
    router_api.send_batch_commands(commands)
```

---

**⚡ نصيحة**: طبق هذه التحسينات تدريجياً وراقب تأثيرها على الأداء قبل الانتقال للتحسين التالي!