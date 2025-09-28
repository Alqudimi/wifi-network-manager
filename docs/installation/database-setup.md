# 💾 إعداد قاعدة البيانات

## نظرة عامة

نظام إدارة شبكات Wi-Fi يدعم قواعد بيانات متعددة. هذا الدليل يوضح كيفية إعداد وتكوين قواعد البيانات المختلفة.

## خيارات قواعد البيانات

### 1. SQLite (للتطوير والاختبار)
**المميزات:**
- ✅ سهل الإعداد (لا يحتاج خادم منفصل)
- ✅ مناسب للتطوير والاختبار
- ✅ ملف واحد محمول

**العيوب:**
- ❌ أداء محدود مع المستخدمين المتعددين
- ❌ لا يدعم الكتابة المتزامنة بكفاءة
- ❌ غير مناسب للإنتاج الكبير

### 2. PostgreSQL (مستحسن للإنتاج)
**المميزات:**
- ✅ أداء عالي ومعالجة متقدمة
- ✅ دعم كامل للمعاملات المعقدة
- ✅ مقاوم للأخطاء وآمن
- ✅ يدعم JSON وأنواع بيانات متقدمة

### 3. MySQL/MariaDB (بديل جيد)
**المميزات:**
- ✅ واسع الانتشار وسهل الإدارة
- ✅ أداء جيد للتطبيقات المتوسطة
- ✅ دعم جيد للاستضافة المشتركة

---

## إعداد SQLite

### التثبيت والإعداد
SQLite مضمن مع Python ولا يحتاج تثبيت منفصل.

```bash
# التحقق من وجود SQLite
python -c "import sqlite3; print('SQLite version:', sqlite3.sqlite_version)"
```

### الإعداد في التطبيق
```python
# في config.py
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///wifi_manager_dev.db'
    SQLALCHEMY_ECHO = True  # لعرض SQL queries
```

### إنشاء قاعدة البيانات
```bash
# تشغيل التطبيق لإنشاء قاعدة البيانات تلقائياً
python app.py

# أو يدوياً
python -c "
from app import create_app
from database import db

app = create_app()
with app.app_context():
    db.create_all()
    print('تم إنشاء قاعدة البيانات بنجاح')
"
```

### أدوات إدارة SQLite
```bash
# تثبيت sqlite3 command line
sudo apt-get install sqlite3  # Ubuntu/Debian
brew install sqlite3          # macOS

# الاتصال بقاعدة البيانات
sqlite3 wifi_manager.db

# أوامر مفيدة في sqlite3
.tables                    # عرض الجداول
.schema user               # عرض هيكل جدول المستخدمين
.quit                      # الخروج
```

---

## إعداد PostgreSQL

### تثبيت PostgreSQL

#### Ubuntu/Debian:
```bash
# تثبيت PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# تثبيت مكتبة Python
pip install psycopg2-binary
```

#### CentOS/RHEL:
```bash
# تثبيت PostgreSQL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# تثبيت مكتبة Python
pip install psycopg2-binary
```

#### macOS:
```bash
# باستخدام Homebrew
brew install postgresql
brew services start postgresql

# تثبيت مكتبة Python
pip install psycopg2-binary
```

### إعداد المستخدم وقاعدة البيانات
```bash
# التبديل للمستخدم postgres
sudo -u postgres psql

# في shell PostgreSQL:
-- إنشاء مستخدم جديد
CREATE USER wifi_manager WITH PASSWORD 'secure_password';

-- إنشاء قاعدة البيانات
CREATE DATABASE wifi_manager_db OWNER wifi_manager;

-- منح الصلاحيات
GRANT ALL PRIVILEGES ON DATABASE wifi_manager_db TO wifi_manager;

-- الخروج
\q
```

### إعداد الاتصال الآمن
```bash
# تعديل ملف pg_hba.conf
sudo nano /etc/postgresql/13/main/pg_hba.conf

# إضافة السطر التالي:
# local   wifi_manager_db   wifi_manager                     md5
# host    wifi_manager_db   wifi_manager   127.0.0.1/32      md5

# إعادة تشغيل PostgreSQL
sudo systemctl restart postgresql
```

### إعداد التطبيق للـ PostgreSQL
```python
# في .env
DATABASE_URL=postgresql://wifi_manager:secure_password@localhost/wifi_manager_db

# في config.py
import os

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 40
    }
```

### اختبار الاتصال
```python
# اختبار الاتصال بـ PostgreSQL
python -c "
import os
from sqlalchemy import create_engine

# استخدام DATABASE_URL من البيئة
db_url = os.environ.get('DATABASE_URL', 'postgresql://wifi_manager:secure_password@localhost/wifi_manager_db')

try:
    engine = create_engine(db_url)
    connection = engine.connect()
    result = connection.execute('SELECT version()')
    print('اتصال ناجح!')
    print('إصدار PostgreSQL:', result.fetchone()[0])
    connection.close()
except Exception as e:
    print('خطأ في الاتصال:', e)
"
```

---

## إعداد MySQL/MariaDB

### تثبيت MySQL

#### Ubuntu/Debian:
```bash
# تثبيت MySQL
sudo apt update
sudo apt install mysql-server

# أو MariaDB
sudo apt install mariadb-server

# تثبيت مكتبة Python
pip install mysqlclient
# أو
pip install PyMySQL
```

### إعداد قاعدة البيانات
```bash
# تشغيل سكريبت الأمان
sudo mysql_secure_installation

# الدخول لـ MySQL
sudo mysql -u root -p

# في shell MySQL:
-- إنشاء قاعدة البيانات
CREATE DATABASE wifi_manager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- إنشاء المستخدم
CREATE USER 'wifi_manager'@'localhost' IDENTIFIED BY 'secure_password';

-- منح الصلاحيات
GRANT ALL PRIVILEGES ON wifi_manager_db.* TO 'wifi_manager'@'localhost';
FLUSH PRIVILEGES;

-- الخروج
EXIT;
```

### إعداد التطبيق للـ MySQL
```python
# في .env
DATABASE_URL=mysql+pymysql://wifi_manager:secure_password@localhost/wifi_manager_db

# في config.py
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 7200,
        'pool_pre_ping': True
    }
```

---

## إدارة قاعدة البيانات مع Flask-Migrate

### تثبيت وإعداد Migrations
```bash
# التأكد من تثبيت Flask-Migrate
pip install Flask-Migrate

# تهيئة migrations (مرة واحدة فقط)
flask db init

# إنشاء migration جديد
flask db migrate -m "Initial migration"

# تطبيق migrations على قاعدة البيانات
flask db upgrade
```

### إدارة Schema Changes
```bash
# بعد تعديل النماذج، إنشاء migration جديد
flask db migrate -m "Add new fields to voucher table"

# مراجعة ملف migration قبل التطبيق
nano migrations/versions/xxx_add_new_fields.py

# تطبيق التغييرات
flask db upgrade

# في حالة وجود مشاكل، العودة للإصدار السابق
flask db downgrade
```

### أوامر Migration المفيدة
```bash
# عرض تاريخ migrations
flask db history

# عرض الـ migration الحالي
flask db current

# العودة لـ migration محدد
flask db downgrade <revision_id>

# تطبيق migration محدد
flask db upgrade <revision_id>
```

---

## النسخ الاحتياطية والاستعادة

### SQLite Backups
```bash
#!/bin/bash
# سكريبت نسخ احتياطي لـ SQLite

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
DB_FILE="wifi_manager.db"

# إنشاء مجلد النسخ الاحتياطية
mkdir -p $BACKUP_DIR

# إنشاء نسخة احتياطية
cp $DB_FILE "$BACKUP_DIR/wifi_manager_backup_$DATE.db"

# ضغط النسخة الاحتياطية
gzip "$BACKUP_DIR/wifi_manager_backup_$DATE.db"

echo "تم إنشاء نسخة احتياطية: wifi_manager_backup_$DATE.db.gz"

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

### PostgreSQL Backups
```bash
#!/bin/bash
# سكريبت نسخ احتياطي لـ PostgreSQL

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
DB_NAME="wifi_manager_db"
DB_USER="wifi_manager"

# إنشاء مجلد النسخ الاحتياطية
mkdir -p $BACKUP_DIR

# إنشاء نسخة احتياطية مضغوطة
pg_dump -U $DB_USER -h localhost -d $DB_NAME | gzip > "$BACKUP_DIR/postgres_backup_$DATE.sql.gz"

echo "تم إنشاء نسخة احتياطية: postgres_backup_$DATE.sql.gz"

# استعادة من نسخة احتياطية
# gunzip -c backup_file.sql.gz | psql -U wifi_manager -d wifi_manager_db
```

### MySQL Backups
```bash
#!/bin/bash
# سكريبت نسخ احتياطي لـ MySQL

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
DB_NAME="wifi_manager_db"
DB_USER="wifi_manager"
DB_PASS="secure_password"

# إنشاء مجلد النسخ الاحتياطية
mkdir -p $BACKUP_DIR

# إنشاء نسخة احتياطية
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > "$BACKUP_DIR/mysql_backup_$DATE.sql.gz"

echo "تم إنشاء نسخة احتياطية: mysql_backup_$DATE.sql.gz"
```

---

## تحسين الأداء

### PostgreSQL Optimization
```sql
-- في postgresql.conf
shared_buffers = 256MB          -- ذاكرة مشتركة
effective_cache_size = 1GB      -- حجم الكاش
work_mem = 4MB                  -- ذاكرة العمليات
maintenance_work_mem = 64MB     -- ذاكرة الصيانة
checkpoint_completion_target = 0.7
wal_buffers = 16MB
random_page_cost = 1.1          -- للـ SSD

-- إنشاء indexes مفيدة
CREATE INDEX idx_voucher_status ON voucher(status);
CREATE INDEX idx_voucher_code ON voucher(code);
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_voucher_created_at ON voucher(created_at);
```

### MySQL Optimization
```sql
-- في my.cnf
[mysqld]
innodb_buffer_pool_size = 512M
innodb_log_file_size = 64M
innodb_flush_log_at_trx_commit = 2
query_cache_size = 32M
query_cache_type = 1

-- إنشاء indexes
CREATE INDEX idx_voucher_status ON voucher(status);
CREATE INDEX idx_voucher_code ON voucher(code);
CREATE INDEX idx_user_username ON user(username);
```

### تحسين SQLAlchemy
```python
# في config.py
class ProductionConfig(Config):
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,                    # حجم مجموعة الاتصالات
        'pool_recycle': 3600,               # إعادة تدوير الاتصالات
        'pool_pre_ping': True,              # اختبار الاتصالات
        'pool_timeout': 30,                 # مهلة انتظار الاتصال
        'max_overflow': 40,                 # اتصالات إضافية
        'echo': False,                      # عدم طباعة SQL (للإنتاج)
        'future': True                      # استخدام SQLAlchemy 2.0 style
    }
```

---

## مراقبة قاعدة البيانات

### PostgreSQL Monitoring
```sql
-- مراقبة الاتصالات النشطة
SELECT count(*) as active_connections FROM pg_stat_activity;

-- مراقبة استهلاك المساحة
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public';

-- مراقبة الـ queries البطيئة
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

### MySQL Monitoring
```sql
-- مراقبة الاتصالات
SHOW STATUS LIKE 'Threads_connected';

-- مراقبة استهلاك المساحة
SELECT 
    table_schema as 'Database',
    table_name as 'Table',
    round(((data_length + index_length) / 1024 / 1024), 2) as 'Size (MB)'
FROM information_schema.tables 
ORDER BY (data_length + index_length) DESC;

-- مراقبة الـ queries البطيئة
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;
```

---

## استكشاف المشاكل

### مشاكل الاتصال الشائعة

#### مشكلة: "Connection refused"
```bash
# التحقق من تشغيل الخدمة
sudo systemctl status postgresql  # أو mysql

# التحقق من المنافذ
sudo netstat -tlnp | grep 5432    # PostgreSQL
sudo netstat -tlnp | grep 3306    # MySQL

# فحص الـ firewall
sudo ufw status
```

#### مشكلة: "Authentication failed"
```bash
# PostgreSQL - فحص pg_hba.conf
sudo nano /etc/postgresql/13/main/pg_hba.conf

# MySQL - إعادة تعيين كلمة المرور
sudo mysql -u root -p
ALTER USER 'wifi_manager'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

#### مشكلة: "Database does not exist"
```bash
# التحقق من وجود قاعدة البيانات
# PostgreSQL:
sudo -u postgres psql -l

# MySQL:
mysql -u root -p -e "SHOW DATABASES;"
```

### سكريبت فحص سريع
```python
#!/usr/bin/env python3
"""سكريبت فحص صحة قاعدة البيانات"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def check_database():
    """فحص الاتصال بقاعدة البيانات"""
    
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///wifi_manager.db')
    
    try:
        engine = create_engine(db_url)
        
        with engine.connect() as connection:
            # اختبار اتصال بسيط
            if 'postgresql' in db_url:
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL متصل: {version}")
                
            elif 'mysql' in db_url:
                result = connection.execute(text("SELECT VERSION()"))
                version = result.fetchone()[0]
                print(f"✅ MySQL متصل: {version}")
                
            else:  # SQLite
                result = connection.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                print(f"✅ SQLite متصل: {version}")
            
            # فحص الجداول الأساسية
            tables = ['user', 'voucher', 'network', 'router']
            for table in tables:
                try:
                    connection.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    print(f"✅ جدول {table} موجود")
                except:
                    print(f"❌ جدول {table} غير موجود")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

if __name__ == '__main__':
    success = check_database()
    exit(0 if success else 1)
```

---

**💡 نصيحة**: ابدأ بـ SQLite للتطوير والاختبار، ثم انتقل لـ PostgreSQL عند النشر للإنتاج.