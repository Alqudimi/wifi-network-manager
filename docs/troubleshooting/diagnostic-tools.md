# 🔧 أدوات التشخيص

## نظرة عامة

أدوات التشخيص تساعد في تحديد وحل مشاكل النظام بسرعة ودقة. هذا الدليل يغطي الأدوات المدمجة والخارجية للفحص والصيانة.

## الأدوات المدمجة في النظام

### 1. أداة فحص الصحة العامة
```python
#!/usr/bin/env python3
# health_check.py

import psutil
import requests
import subprocess
import json
from datetime import datetime

class SystemHealthChecker:
    def __init__(self):
        self.results = {}
    
    def check_system_resources(self):
        """فحص موارد النظام"""
        self.results['system'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg()[0]
        }
        
        return self.results['system']
    
    def check_database_connection(self):
        """فحص اتصال قاعدة البيانات"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                database="wifi_manager",
                user="wifi_manager",
                password="your_password"
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            self.results['database'] = {
                'status': 'healthy',
                'response_time': 'fast',
                'connection': 'ok'
            }
            
            conn.close()
            
        except Exception as e:
            self.results['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        return self.results['database']
    
    def check_application_health(self):
        """فحص صحة التطبيق"""
        try:
            response = requests.get('http://localhost:5000/health', timeout=5)
            
            if response.status_code == 200:
                self.results['application'] = {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'details': response.json()
                }
            else:
                self.results['application'] = {
                    'status': 'unhealthy',
                    'http_code': response.status_code
                }
                
        except Exception as e:
            self.results['application'] = {
                'status': 'unreachable',
                'error': str(e)
            }
        
        return self.results['application']
    
    def check_router_connectivity(self):
        """فحص الاتصال بأجهزة التوجيه"""
        routers = [
            {'ip': '192.168.1.1', 'type': 'MikroTik'},
            {'ip': '192.168.1.2', 'type': 'Ubiquiti'}
        ]
        
        self.results['routers'] = []
        
        for router in routers:
            try:
                # فحص ping
                ping_result = subprocess.run(
                    ['ping', '-c', '1', '-W', '3', router['ip']], 
                    capture_output=True, text=True
                )
                
                if ping_result.returncode == 0:
                    status = 'reachable'
                    ping_time = self.extract_ping_time(ping_result.stdout)
                else:
                    status = 'unreachable'
                    ping_time = None
                
                self.results['routers'].append({
                    'ip': router['ip'],
                    'type': router['type'],
                    'status': status,
                    'ping_time': ping_time
                })
                
            except Exception as e:
                self.results['routers'].append({
                    'ip': router['ip'],
                    'type': router['type'],
                    'status': 'error',
                    'error': str(e)
                })
        
        return self.results['routers']
    
    def extract_ping_time(self, ping_output):
        """استخراج وقت الـ ping من النتائج"""
        import re
        match = re.search(r'time=(\d+\.?\d*)', ping_output)
        return float(match.group(1)) if match else None
    
    def generate_report(self):
        """إنشاء تقرير شامل"""
        self.check_system_resources()
        self.check_database_connection()
        self.check_application_health()
        self.check_router_connectivity()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': self.determine_overall_status(),
            'components': self.results
        }
        
        return report
    
    def determine_overall_status(self):
        """تحديد الحالة العامة للنظام"""
        issues = []
        
        # فحص الموارد
        system = self.results.get('system', {})
        if system.get('cpu_percent', 0) > 90:
            issues.append('High CPU usage')
        if system.get('memory_percent', 0) > 90:
            issues.append('High memory usage')
        if system.get('disk_usage', 0) > 90:
            issues.append('Low disk space')
        
        # فحص قاعدة البيانات
        if self.results.get('database', {}).get('status') != 'healthy':
            issues.append('Database issues')
        
        # فحص التطبيق
        if self.results.get('application', {}).get('status') != 'healthy':
            issues.append('Application issues')
        
        # فحص الراوترات
        unreachable_routers = [
            r for r in self.results.get('routers', []) 
            if r.get('status') != 'reachable'
        ]
        if unreachable_routers:
            issues.append(f'{len(unreachable_routers)} routers unreachable')
        
        if not issues:
            return 'healthy'
        elif len(issues) <= 2:
            return 'warning'
        else:
            return 'critical'

# تشغيل الفحص
if __name__ == '__main__':
    checker = SystemHealthChecker()
    report = checker.generate_report()
    
    print(json.dumps(report, indent=2, ensure_ascii=False))
```

### 2. أداة تشخيص قاعدة البيانات
```python
#!/usr/bin/env python3
# database_diagnostic.py

import psycopg2
from datetime import datetime, timedelta

class DatabaseDiagnostic:
    def __init__(self, connection_string):
        self.conn_string = connection_string
        self.results = {}
    
    def check_table_sizes(self):
        """فحص أحجام الجداول"""
        query = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY size_bytes DESC;
        """
        
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()
            cursor.execute(query)
            
            self.results['table_sizes'] = [
                {
                    'schema': row[0],
                    'table': row[1], 
                    'size': row[2],
                    'size_bytes': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
        except Exception as e:
            self.results['table_sizes'] = {'error': str(e)}
        
        return self.results['table_sizes']
    
    def check_slow_queries(self):
        """فحص الاستعلامات البطيئة"""
        query = """
        SELECT 
            query,
            mean_exec_time,
            calls,
            total_exec_time
        FROM pg_stat_statements 
        WHERE mean_exec_time > 1000  -- أكثر من ثانية واحدة
        ORDER BY mean_exec_time DESC 
        LIMIT 10;
        """
        
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()
            cursor.execute(query)
            
            self.results['slow_queries'] = [
                {
                    'query': row[0][:100] + '...' if len(row[0]) > 100 else row[0],
                    'mean_time_ms': row[1],
                    'calls': row[2],
                    'total_time_ms': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
        except Exception as e:
            self.results['slow_queries'] = {'error': str(e)}
        
        return self.results['slow_queries']
    
    def check_connection_stats(self):
        """فحص إحصائيات الاتصالات"""
        query = """
        SELECT 
            count(*) as total_connections,
            count(*) FILTER (WHERE state = 'active') as active_connections,
            count(*) FILTER (WHERE state = 'idle') as idle_connections,
            count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
        FROM pg_stat_activity;
        """
        
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()
            cursor.execute(query)
            
            row = cursor.fetchone()
            self.results['connections'] = {
                'total': row[0],
                'active': row[1],
                'idle': row[2],
                'idle_in_transaction': row[3]
            }
            
            conn.close()
            
        except Exception as e:
            self.results['connections'] = {'error': str(e)}
        
        return self.results['connections']
    
    def check_index_usage(self):
        """فحص استخدام الفهارس"""
        query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes 
        WHERE idx_tup_read = 0
        ORDER BY schemaname, tablename;
        """
        
        try:
            conn = psycopg2.connect(self.conn_string)
            cursor = conn.cursor()
            cursor.execute(query)
            
            self.results['unused_indexes'] = [
                {
                    'schema': row[0],
                    'table': row[1],
                    'index': row[2],
                    'reads': row[3],
                    'fetches': row[4]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
        except Exception as e:
            self.results['unused_indexes'] = {'error': str(e)}
        
        return self.results['unused_indexes']

    def generate_database_report(self):
        """إنشاء تقرير شامل لقاعدة البيانات"""
        self.check_table_sizes()
        self.check_slow_queries()
        self.check_connection_stats()
        self.check_index_usage()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'database_health': self.results
        }
```

### 3. أداة مراقبة أجهزة التوجيه
```python
#!/usr/bin/env python3
# router_diagnostic.py

import subprocess
import socket
import time
from concurrent.futures import ThreadPoolExecutor

class RouterDiagnostic:
    def __init__(self):
        self.routers = [
            {'ip': '192.168.1.1', 'type': 'MikroTik', 'api_port': 8728},
            {'ip': '192.168.1.2', 'type': 'Ubiquiti', 'api_port': 8443}
        ]
        self.results = {}
    
    def ping_test(self, ip, count=3):
        """اختبار ping لجهاز التوجيه"""
        try:
            result = subprocess.run(
                ['ping', '-c', str(count), '-W', '3', ip],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # استخراج إحصائيات الـ ping
                lines = result.stdout.split('\n')
                stats_line = [line for line in lines if 'min/avg/max' in line]
                
                if stats_line:
                    stats = stats_line[0].split('=')[1].strip().split('/')
                    return {
                        'status': 'success',
                        'min_ms': float(stats[0]),
                        'avg_ms': float(stats[1]),
                        'max_ms': float(stats[2]),
                        'packet_loss': 0
                    }
            
            return {'status': 'failed', 'error': 'No response'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def port_scan(self, ip, port, timeout=3):
        """فحص إمكانية الوصول للمنفذ"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            return result == 0
            
        except Exception:
            return False
    
    def test_api_connectivity(self, router):
        """اختبار الاتصال بـ API الجهاز"""
        ip = router['ip']
        port = router['api_port']
        
        if router['type'] == 'MikroTik':
            return self.test_mikrotik_api(ip, port)
        elif router['type'] == 'Ubiquiti':
            return self.test_ubiquiti_api(ip, port)
        else:
            return {'status': 'unsupported', 'message': 'Router type not supported'}
    
    def test_mikrotik_api(self, ip, port):
        """اختبار API خاص بـ MikroTik"""
        try:
            import librouteros
            
            api = librouteros.connect(
                host=ip,
                username='admin',
                password='admin',  # يجب أن يكون من الإعدادات
                port=port,
                timeout=5
            )
            
            # اختبار بسيط - الحصول على هوية الجهاز
            identity = list(api.path('system', 'identity').select('name'))
            api.close()
            
            return {
                'status': 'success',
                'identity': identity[0]['name'] if identity else 'Unknown'
            }
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def test_ubiquiti_api(self, ip, port):
        """اختبار API خاص بـ Ubiquiti"""
        try:
            import requests
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            
            # محاولة الوصول لصفحة تسجيل الدخول
            response = requests.get(
                f'https://{ip}:{port}/api/login',
                verify=False,
                timeout=5
            )
            
            if response.status_code in [200, 401]:  # 401 يعني أن API يعمل لكن يحتاج مصادقة
                return {'status': 'success', 'api_accessible': True}
            else:
                return {'status': 'failed', 'http_code': response.status_code}
                
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def diagnose_router(self, router):
        """تشخيص شامل لجهاز التوجيه"""
        ip = router['ip']
        router_type = router['type']
        
        diagnosis = {
            'ip': ip,
            'type': router_type,
            'timestamp': time.time()
        }
        
        # اختبار ping
        diagnosis['ping'] = self.ping_test(ip)
        
        # اختبار المنفذ
        diagnosis['port_accessible'] = self.port_scan(ip, router['api_port'])
        
        # اختبار API
        if diagnosis['port_accessible']:
            diagnosis['api_test'] = self.test_api_connectivity(router)
        else:
            diagnosis['api_test'] = {'status': 'port_closed'}
        
        # تحديد الحالة العامة
        if (diagnosis['ping']['status'] == 'success' and 
            diagnosis['port_accessible'] and 
            diagnosis['api_test']['status'] == 'success'):
            diagnosis['overall_status'] = 'healthy'
        elif diagnosis['ping']['status'] == 'success':
            diagnosis['overall_status'] = 'ping_only'
        else:
            diagnosis['overall_status'] = 'unreachable'
        
        return diagnosis
    
    def diagnose_all_routers(self):
        """تشخيص جميع أجهزة التوجيه بالتوازي"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.diagnose_router, router): router 
                for router in self.routers
            }
            
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    router = futures[future]
                    results.append({
                        'ip': router['ip'],
                        'type': router['type'],
                        'overall_status': 'error',
                        'error': str(e)
                    })
        
        return results

# تشغيل التشخيص
if __name__ == '__main__':
    diagnostic = RouterDiagnostic()
    results = diagnostic.diagnose_all_routers()
    
    print("=== تقرير تشخيص أجهزة التوجيه ===")
    for result in results:
        print(f"\nجهاز: {result['ip']} ({result['type']})")
        print(f"الحالة: {result['overall_status']}")
        
        if 'ping' in result:
            ping = result['ping']
            if ping['status'] == 'success':
                print(f"Ping: {ping['avg_ms']:.1f}ms")
            else:
                print(f"Ping: فشل - {ping.get('error', 'غير معروف')}")
        
        if 'api_test' in result:
            api = result['api_test']
            print(f"API: {api['status']}")
            if api['status'] == 'failed':
                print(f"خطأ API: {api.get('error', 'غير معروف')}")
```

## أدوات سطر الأوامر

### فحص سريع للنظام
```bash
#!/bin/bash
# quick_check.sh

echo "=== فحص سريع لنظام إدارة شبكات Wi-Fi ==="

# فحص العمليات
echo -e "\n1. حالة العمليات:"
if pgrep -f "wifi-manager" > /dev/null; then
    echo "✅ تطبيق WiFi Manager يعمل"
else
    echo "❌ تطبيق WiFi Manager متوقف"
fi

# فحص قاعدة البيانات
echo -e "\n2. قاعدة البيانات:"
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL يعمل"
    
    # فحص الاتصال
    if sudo -u postgres psql -d wifi_manager -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ الاتصال بقاعدة البيانات ناجح"
    else
        echo "❌ فشل الاتصال بقاعدة البيانات"
    fi
else
    echo "❌ PostgreSQL متوقف"
fi

# فحص المنافذ
echo -e "\n3. المنافذ:"
if netstat -tln | grep ":5000" > /dev/null; then
    echo "✅ منفذ 5000 مفتوح"
else
    echo "❌ منفذ 5000 مغلق"
fi

# فحص المساحة
echo -e "\n4. مساحة القرص:"
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ مساحة القرص: ${DISK_USAGE}%"
else
    echo "⚠️ مساحة القرص منخفضة: ${DISK_USAGE}%"
fi

# فحص الذاكرة
echo -e "\n5. استهلاك الذاكرة:"
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    echo "✅ استهلاك الذاكرة: ${MEMORY_USAGE}%"
else
    echo "⚠️ استهلاك ذاكرة عالي: ${MEMORY_USAGE}%"
fi

# فحص السجلات للأخطاء الحديثة
echo -e "\n6. الأخطاء الحديثة:"
ERROR_COUNT=$(tail -n 100 /var/log/wifi-manager/app.log 2>/dev/null | grep -c ERROR || echo "0")
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "✅ لا توجد أخطاء حديثة"
else
    echo "⚠️ عدد الأخطاء الحديثة: $ERROR_COUNT"
fi

echo -e "\n=== انتهى الفحص ==="
```

### أداة فحص الشبكة
```bash
#!/bin/bash
# network_check.sh

echo "=== فحص شبكة أجهزة التوجيه ==="

ROUTERS=("192.168.1.1" "192.168.1.2")

for router in "${ROUTERS[@]}"; do
    echo -e "\nفحص $router:"
    
    # فحص ping
    if ping -c 1 -W 3 "$router" > /dev/null 2>&1; then
        echo "✅ Ping ناجح"
        
        # فحص SSH (إذا كان متاح)
        if timeout 3 bash -c "</dev/tcp/$router/22" 2>/dev/null; then
            echo "✅ SSH متاح"
        else
            echo "⚠️ SSH غير متاح"
        fi
        
        # فحص HTTP
        if timeout 3 bash -c "</dev/tcp/$router/80" 2>/dev/null; then
            echo "✅ HTTP متاح"
        else
            echo "⚠️ HTTP غير متاح"
        fi
        
    else
        echo "❌ Ping فاشل - الجهاز غير متاح"
    fi
done
```

## أدوات المراقبة المستمرة

### مراقب الأداء
```python
#!/usr/bin/env python3
# performance_monitor.py

import psutil
import time
import json
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, interval=30):
        self.interval = interval
        self.metrics = []
    
    def collect_metrics(self):
        """جمع مقاييس الأداء"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict(),
            'network_io': psutil.net_io_counters()._asdict(),
            'load_average': psutil.getloadavg(),
            'process_count': len(psutil.pids())
        }
    
    def monitor_continuously(self, duration_minutes=60):
        """مراقبة مستمرة لفترة محددة"""
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            metrics = self.collect_metrics()
            self.metrics.append(metrics)
            
            # إظهار تحديث مباشر
            print(f"CPU: {metrics['cpu_percent']:5.1f}% | "
                  f"Memory: {metrics['memory_percent']:5.1f}% | "
                  f"Load: {metrics['load_average'][0]:5.2f}")
            
            time.sleep(self.interval)
        
        return self.metrics
    
    def save_metrics(self, filename):
        """حفظ المقاييس في ملف"""
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)

if __name__ == '__main__':
    monitor = PerformanceMonitor(interval=10)
    
    print("بدء مراقبة الأداء لمدة 30 دقيقة...")
    metrics = monitor.monitor_continuously(30)
    
    # حفظ النتائج
    filename = f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    monitor.save_metrics(filename)
    
    print(f"تم حفظ مقاييس الأداء في: {filename}")
```

### تقرير تشخيص شامل
```bash
#!/bin/bash
# comprehensive_diagnostic.sh

REPORT_DIR="/tmp/wifi_manager_diagnostic_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$REPORT_DIR"

echo "إنشاء تقرير تشخيص شامل في: $REPORT_DIR"

# معلومات النظام
echo "=== معلومات النظام ===" > "$REPORT_DIR/system_info.txt"
uname -a >> "$REPORT_DIR/system_info.txt"
cat /etc/os-release >> "$REPORT_DIR/system_info.txt"
free -h >> "$REPORT_DIR/system_info.txt"
df -h >> "$REPORT_DIR/system_info.txt"

# حالة الخدمات
echo "=== حالة الخدمات ===" > "$REPORT_DIR/services.txt"
systemctl status wifi-manager >> "$REPORT_DIR/services.txt" 2>&1
systemctl status postgresql >> "$REPORT_DIR/services.txt" 2>&1
systemctl status nginx >> "$REPORT_DIR/services.txt" 2>&1

# العمليات النشطة
echo "=== العمليات النشطة ===" > "$REPORT_DIR/processes.txt"
ps aux | grep -E "(wifi|postgres|nginx)" >> "$REPORT_DIR/processes.txt"

# اتصالات الشبكة
echo "=== اتصالات الشبكة ===" > "$REPORT_DIR/network.txt"
netstat -tln >> "$REPORT_DIR/network.txt"
ss -tln >> "$REPORT_DIR/network.txt"

# السجلات الحديثة
echo "نسخ السجلات الحديثة..."
tail -n 500 /var/log/wifi-manager/app.log > "$REPORT_DIR/app_log.txt" 2>/dev/null
tail -n 100 /var/log/wifi-manager/error.log > "$REPORT_DIR/error_log.txt" 2>/dev/null
tail -n 100 /var/log/syslog > "$REPORT_DIR/syslog.txt" 2>/dev/null

# إعدادات النظام
echo "نسخ ملفات الإعداد..."
cp /etc/wifi-manager/*.conf "$REPORT_DIR/" 2>/dev/null
cp ~/.env "$REPORT_DIR/environment_vars.txt" 2>/dev/null

# اختبارات الاتصال
echo "=== اختبارات الاتصال ===" > "$REPORT_DIR/connectivity.txt"
curl -I http://localhost:5000/health >> "$REPORT_DIR/connectivity.txt" 2>&1
ping -c 3 8.8.8.8 >> "$REPORT_DIR/connectivity.txt" 2>&1

# ضغط التقرير
tar -czf "${REPORT_DIR}.tar.gz" -C "$(dirname "$REPORT_DIR")" "$(basename "$REPORT_DIR")"

echo "تم إنشاء تقرير التشخيص: ${REPORT_DIR}.tar.gz"
echo "يمكنك إرسال هذا الملف للدعم الفني لتحليل المشاكل"
```

---

**🔍 نصيحة**: استخدم هذه الأدوات بانتظام للصيانة الوقائية وتجنب المشاكل قبل حدوثها!