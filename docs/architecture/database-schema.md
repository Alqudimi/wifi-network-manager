# 💾 مخطط قاعدة البيانات

## الجداول الأساسية

### جدول المستخدمين (users)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### جدول الكروت (vouchers)
```sql
CREATE TABLE vouchers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    voucher_type VARCHAR(20) DEFAULT 'standard',
    status VARCHAR(20) DEFAULT 'active',
    duration_hours INTEGER NOT NULL,
    data_limit_mb INTEGER,
    speed_limit_kbps INTEGER,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    used_at TIMESTAMP,
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    client_ip INET,
    client_mac MACADDR,
    data_used_mb INTEGER DEFAULT 0,
    session_token VARCHAR(255),
    created_by INTEGER REFERENCES users(id),
    batch_id VARCHAR(100),
    notes TEXT
);
```

### جدول الشبكات (networks)
```sql
CREATE TABLE networks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ssid VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    captive_portal_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### جدول أجهزة التوجيه (routers)
```sql
CREATE TABLE routers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ip_address INET NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(100),
    username VARCHAR(50) NOT NULL,
    password_encrypted TEXT NOT NULL,
    api_port INTEGER DEFAULT 8728,
    is_active BOOLEAN DEFAULT true,
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
```

## الفهارس والقيود

### الفهارس للأداء
```sql
-- فهارس للبحث السريع
CREATE INDEX idx_vouchers_code ON vouchers(code);
CREATE INDEX idx_vouchers_status ON vouchers(status);
CREATE INDEX idx_vouchers_created_at ON vouchers(created_at);
CREATE INDEX idx_vouchers_expires_at ON vouchers(expires_at);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- فهارس مركبة للاستعلامات المعقدة
CREATE INDEX idx_vouchers_status_type ON vouchers(status, voucher_type);
CREATE INDEX idx_vouchers_session_active ON vouchers(status, session_start, session_end);
```

### القيود والتحقق
```sql
-- قيود للتحقق من صحة البيانات
ALTER TABLE vouchers ADD CONSTRAINT chk_voucher_status 
    CHECK (status IN ('active', 'used', 'expired', 'disabled'));

ALTER TABLE vouchers ADD CONSTRAINT chk_voucher_type 
    CHECK (voucher_type IN ('standard', 'premium', 'vip'));

ALTER TABLE users ADD CONSTRAINT chk_user_role 
    CHECK (role IN ('admin', 'operator', 'user'));

-- قيود للتواريخ
ALTER TABLE vouchers ADD CONSTRAINT chk_session_dates 
    CHECK (session_end > session_start OR session_end IS NULL);
```

## العلاقات بين الجداول

### مخطط ERD
```
users (1) ──────── (∞) vouchers
                        │
                        │ (created_by)
                        │
networks (∞) ────── (∞) router_networks ────── (∞) routers
    │                                               │
    │                                               │
    └─────────── (∞) network_vouchers (∞) ─────────┘
```

## Views للاستعلامات المعقدة

### إحصائيات الكروت
```sql
CREATE VIEW voucher_stats AS
SELECT 
    voucher_type,
    status,
    COUNT(*) as count,
    SUM(price) as total_revenue,
    AVG(data_used_mb) as avg_data_usage,
    AVG(EXTRACT(EPOCH FROM (session_end - session_start))/3600) as avg_session_hours
FROM vouchers 
GROUP BY voucher_type, status;
```

### الاتصالات النشطة
```sql
CREATE VIEW active_sessions AS
SELECT 
    v.code,
    v.client_ip,
    v.client_mac,
    v.session_start,
    v.session_end,
    v.data_used_mb,
    v.data_limit_mb,
    u.username as created_by_user,
    EXTRACT(EPOCH FROM (v.session_end - NOW()))/60 as minutes_remaining
FROM vouchers v
LEFT JOIN users u ON v.created_by = u.id
WHERE v.status = 'used' 
    AND v.session_end > NOW()
    AND v.session_start IS NOT NULL;
```

## Functions المساعدة

### تنظيف البيانات القديمة
```sql
CREATE OR REPLACE FUNCTION cleanup_old_vouchers()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- حذف الكروت المنتهية الأقدم من 90 يوم
    DELETE FROM vouchers 
    WHERE status = 'expired' 
        AND expires_at < NOW() - INTERVAL '90 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- تسجيل العملية
    INSERT INTO system_logs (event_type, message, created_at)
    VALUES ('cleanup', 'Deleted ' || deleted_count || ' old vouchers', NOW());
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
```

### إحصائيات يومية
```sql
CREATE OR REPLACE FUNCTION daily_stats(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE(
    vouchers_created INTEGER,
    vouchers_used INTEGER,
    total_revenue DECIMAL,
    active_sessions INTEGER,
    data_consumed_gb DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(CASE WHEN DATE(created_at) = target_date THEN 1 END)::INTEGER,
        COUNT(CASE WHEN DATE(used_at) = target_date THEN 1 END)::INTEGER,
        COALESCE(SUM(CASE WHEN DATE(used_at) = target_date THEN price END), 0),
        COUNT(CASE WHEN status = 'used' AND session_end > NOW() THEN 1 END)::INTEGER,
        COALESCE(SUM(data_used_mb), 0) / 1024.0
    FROM vouchers;
END;
$$ LANGUAGE plpgsql;
```