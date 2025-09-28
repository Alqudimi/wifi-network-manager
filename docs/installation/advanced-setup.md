# 🔧 التثبيت المتقدم

## نظرة عامة

هذا الدليل للمستخدمين المتقدمين الذين يحتاجون إعداد مخصص أو نشر على خوادم إنتاج مع متطلبات خاصة.

## إعداد بيئة الإنتاج

### خادم Linux مخصص
```bash
# إعداد المستخدم المخصص
sudo useradd -m -s /bin/bash wifimanager
sudo usermod -aG sudo wifimanager

# إعداد المجلدات
sudo mkdir -p /opt/wifi-manager
sudo chown wifimanager:wifimanager /opt/wifi-manager
cd /opt/wifi-manager

# تثبيت متطلبات النظام
sudo apt update
sudo apt install -y python3.11 python3.11-venv nginx postgresql redis-server supervisor
```

### إعداد قاعدة البيانات الإنتاج
```bash
# PostgreSQL للإنتاج
sudo -u postgres createuser --createdb --pwprompt wifimanager
sudo -u postgres createdb -O wifimanager wifi_manager_prod

# إعداد النسخ الاحتياطية التلقائية
sudo crontab -e
# إضافة: 0 2 * * * pg_dump wifi_manager_prod | gzip > /backup/wifi_$(date +\%Y\%m\%d).sql.gz
```

### إعداد خادم الويب
```nginx
# /etc/nginx/sites-available/wifi-manager
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static {
        alias /opt/wifi-manager/static;
        expires 1d;
    }
}
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://wifi:password@db:5432/wifi_manager
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: wifi_manager
      POSTGRES_USER: wifi
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    
volumes:
  postgres_data:
```

## Load Balancing

### HAProxy Configuration
```
global
    maxconn 4096
    
defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    
frontend wifi_frontend
    bind *:80
    default_backend wifi_servers
    
backend wifi_servers
    balance roundrobin
    server wifi1 127.0.0.1:5001 check
    server wifi2 127.0.0.1:5002 check
    server wifi3 127.0.0.1:5003 check
```

## Monitoring والصحة

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    try:
        # فحص قاعدة البيانات
        db.session.execute('SELECT 1')
        
        # فحص Redis
        from redis import Redis
        r = Redis.from_url(app.config['REDIS_URL'])
        r.ping()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'ok',
            'cache': 'ok'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('wifi_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('wifi_request_duration_seconds', 'Request latency')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    REQUEST_COUNT.labels(request.method, request.endpoint).inc()
    REQUEST_LATENCY.observe(time.time() - request.start_time)
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```