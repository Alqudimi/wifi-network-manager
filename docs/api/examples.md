# 💻 أمثلة عملية لاستخدام API

## أمثلة Python

### إنشاء كرت جديد
```python
import requests
import json

class WiFiManagerAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = None
        self.login(username, password)
    
    def login(self, username, password):
        url = f"{self.base_url}/api/auth/login"
        data = {"username": username, "password": password}
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            self.token = response.json()['data']['token']
        else:
            raise Exception("Login failed")
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def create_voucher(self, voucher_type="standard", duration_hours=24, data_limit_mb=1000):
        url = f"{self.base_url}/api/vouchers"
        data = {
            "voucher_type": voucher_type,
            "duration_hours": duration_hours,
            "data_limit_mb": data_limit_mb,
            "speed_limit_kbps": 1024
        }
        
        response = requests.post(url, json=data, headers=self.get_headers())
        return response.json()
    
    def get_vouchers(self, status=None):
        url = f"{self.base_url}/api/vouchers"
        params = {}
        if status:
            params['status'] = status
            
        response = requests.get(url, params=params, headers=self.get_headers())
        return response.json()

# الاستخدام
api = WiFiManagerAPI("http://localhost:5000", "admin", "admin123")

# إنشاء كرت جديد
voucher = api.create_voucher(voucher_type="premium", duration_hours=48)
print(f"تم إنشاء الكرت: {voucher['data']['code']}")

# عرض جميع الكروت النشطة
active_vouchers = api.get_vouchers(status="active")
print(f"عدد الكروت النشطة: {len(active_vouchers['data']['vouchers'])}")
```

### إنشاء كروت متعددة
```python
def create_bulk_vouchers(api, quantity=50, event_name="EVENT"):
    url = f"{api.base_url}/api/vouchers/batch"
    data = {
        "quantity": quantity,
        "voucher_type": "standard",
        "duration_hours": 12,
        "data_limit_mb": 500,
        "code_prefix": f"{event_name}-",
        "notes": f"كروت للمناسبة {event_name}"
    }
    
    response = requests.post(url, json=data, headers=api.get_headers())
    result = response.json()
    
    if result['success']:
        print(f"تم إنشاء {quantity} كرت بنجاح")
        return result['data']['vouchers']
    else:
        print(f"خطأ: {result['error']['message']}")
        return None

# إنشاء 100 كرت للمؤتمر
vouchers = create_bulk_vouchers(api, quantity=100, event_name="CONFERENCE2025")
```

## أمثلة JavaScript

### فئة لإدارة API
```javascript
class WiFiManagerAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('wifi_token');
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            this.token = data.data.token;
            localStorage.setItem('wifi_token', this.token);
            return true;
        }
        throw new Error(data.error.message);
    }
    
    getHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async createVoucher(config) {
        const response = await fetch(`${this.baseUrl}/api/vouchers`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(config)
        });
        
        return response.json();
    }
    
    async getActiveConnections() {
        const response = await fetch(`${this.baseUrl}/api/control/active`, {
            headers: this.getHeaders()
        });
        
        return response.json();
    }
    
    async disconnectUser(voucherCode, reason = "قطع اتصال إداري") {
        const response = await fetch(`${this.baseUrl}/api/control/disconnect`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({
                voucher_code: voucherCode,
                reason: reason
            })
        });
        
        return response.json();
    }
}

// الاستخدام في صفحة ويب
const api = new WiFiManagerAPI('http://localhost:5000');

// تسجيل الدخول
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        await api.login(username, password);
        console.log('تم تسجيل الدخول بنجاح');
        loadDashboard();
    } catch (error) {
        alert(`خطأ في تسجيل الدخول: ${error.message}`);
    }
});

// إنشاء كرت سريع
async function createQuickVoucher() {
    const config = {
        voucher_type: 'standard',
        duration_hours: 24,
        data_limit_mb: 1000,
        speed_limit_kbps: 1024
    };
    
    try {
        const result = await api.createVoucher(config);
        if (result.success) {
            alert(`تم إنشاء الكرت: ${result.data.code}`);
            refreshVoucherList();
        }
    } catch (error) {
        alert(`خطأ في إنشاء الكرت: ${error.message}`);
    }
}

// مراقبة الاتصالات النشطة
async function monitorConnections() {
    try {
        const result = await api.getActiveConnections();
        if (result.success) {
            updateConnectionsTable(result.data.active_sessions);
        }
    } catch (error) {
        console.error('خطأ في تحديث الاتصالات:', error);
    }
}

// تحديث كل 30 ثانية
setInterval(monitorConnections, 30000);
```

## أمثلة PHP

### فئة PHP لإدارة API
```php
<?php
class WiFiManagerAPI {
    private $baseUrl;
    private $token;
    
    public function __construct($baseUrl) {
        $this->baseUrl = $baseUrl;
    }
    
    public function login($username, $password) {
        $url = $this->baseUrl . '/api/auth/login';
        $data = json_encode([
            'username' => $username,
            'password' => $password
        ]);
        
        $response = $this->makeRequest('POST', $url, $data);
        
        if ($response['success']) {
            $this->token = $response['data']['token'];
            return true;
        }
        
        throw new Exception($response['error']['message']);
    }
    
    public function createVoucher($config) {
        $url = $this->baseUrl . '/api/vouchers';
        $data = json_encode($config);
        
        return $this->makeRequest('POST', $url, $data, $this->getHeaders());
    }
    
    public function getVouchers($status = null) {
        $url = $this->baseUrl . '/api/vouchers';
        if ($status) {
            $url .= '?status=' . urlencode($status);
        }
        
        return $this->makeRequest('GET', $url, null, $this->getHeaders());
    }
    
    private function getHeaders() {
        return [
            'Authorization: Bearer ' . $this->token,
            'Content-Type: application/json'
        ];
    }
    
    private function makeRequest($method, $url, $data = null, $headers = []) {
        $ch = curl_init();
        
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_TIMEOUT => 30
        ]);
        
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        return json_decode($response, true);
    }
}

// الاستخدام
try {
    $api = new WiFiManagerAPI('http://localhost:5000');
    $api->login('admin', 'admin123');
    
    // إنشاء كرت جديد
    $voucherConfig = [
        'voucher_type' => 'standard',
        'duration_hours' => 24,
        'data_limit_mb' => 1000,
        'speed_limit_kbps' => 1024,
        'notes' => 'كرت تجريبي من PHP'
    ];
    
    $result = $api->createVoucher($voucherConfig);
    
    if ($result['success']) {
        echo "تم إنشاء الكرت: " . $result['data']['code'] . "\n";
    }
    
    // عرض الكروت النشطة
    $activeVouchers = $api->getVouchers('active');
    echo "عدد الكروت النشطة: " . count($activeVouchers['data']['vouchers']) . "\n";
    
} catch (Exception $e) {
    echo "خطأ: " . $e->getMessage() . "\n";
}
?>
```

## أمثلة cURL

### تسجيل الدخول
```bash
#!/bin/bash

# متغيرات الإعداد
BASE_URL="http://localhost:5000"
USERNAME="admin"
PASSWORD="admin123"

# تسجيل الدخول والحصول على token
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" | \
  jq -r '.data.token')

echo "Token: $TOKEN"

# إنشاء كرت جديد
curl -X POST "$BASE_URL/api/vouchers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "voucher_type": "standard",
    "duration_hours": 24,
    "data_limit_mb": 1000,
    "speed_limit_kbps": 1024
  }' | jq '.'

# عرض الكروت النشطة
curl -X GET "$BASE_URL/api/vouchers?status=active" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# عرض الاتصالات النشطة
curl -X GET "$BASE_URL/api/control/active" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### سكريبت مراقبة
```bash
#!/bin/bash

# سكريبت مراقبة الاتصالات النشطة
monitor_connections() {
    local token=$1
    
    while true; do
        echo "=== $(date) ==="
        
        # الحصول على الاتصالات النشطة
        CONNECTIONS=$(curl -s -X GET "$BASE_URL/api/control/active" \
          -H "Authorization: Bearer $token")
        
        # عدد الاتصالات
        COUNT=$(echo "$CONNECTIONS" | jq '.data.total_active')
        echo "الاتصالات النشطة: $COUNT"
        
        # عرض تفاصيل الاتصالات
        echo "$CONNECTIONS" | jq -r '.data.active_sessions[] | 
          "الكود: \(.voucher_code) | IP: \(.client_ip) | الوقت المتبقي: \(.time_remaining_minutes) دقيقة"'
        
        echo "------------------------"
        sleep 60
    done
}

# تشغيل المراقبة
monitor_connections "$TOKEN"
```

## أمثلة تكامل مع أنظمة أخرى

### تكامل مع نظام POS
```python
class POSIntegration:
    def __init__(self, wifi_api):
        self.wifi_api = wifi_api
    
    def sell_voucher(self, voucher_type, price, customer_info=None):
        """بيع كرت من خلال نظام نقاط البيع"""
        try:
            # إنشاء الكرت
            voucher_config = self.get_voucher_config(voucher_type)
            voucher_config['price'] = price
            
            result = self.wifi_api.create_voucher(voucher_config)
            
            if result['success']:
                voucher_code = result['data']['code']
                
                # تسجيل البيع في نظام POS
                self.log_sale(voucher_code, price, customer_info)
                
                # طباعة الكرت
                self.print_voucher(result['data'])
                
                return voucher_code
                
        except Exception as e:
            print(f"خطأ في بيع الكرت: {e}")
            return None
    
    def get_voucher_config(self, voucher_type):
        configs = {
            'hourly': {'duration_hours': 1, 'data_limit_mb': 100},
            'daily': {'duration_hours': 24, 'data_limit_mb': 1000},
            'weekly': {'duration_hours': 168, 'data_limit_mb': 5000}
        }
        
        config = configs.get(voucher_type, configs['daily'])
        config['voucher_type'] = 'standard'
        config['speed_limit_kbps'] = 1024
        
        return config
```

### تكامل مع نظام حجوزات الفندق
```php
class HotelIntegration {
    private $wifiApi;
    
    public function __construct($wifiApi) {
        $this->wifiApi = $wifiApi;
    }
    
    public function createGuestVoucher($roomNumber, $checkInDate, $checkOutDate) {
        // حساب مدة الإقامة
        $duration = $this->calculateStayDuration($checkInDate, $checkOutDate);
        
        $voucherConfig = [
            'voucher_type' => 'premium',
            'duration_hours' => $duration * 24,
            'data_limit_mb' => null, // بلا حدود للضيوف
            'speed_limit_kbps' => 5120, // 5 Mbps
            'notes' => "غرفة رقم: $roomNumber"
        ];
        
        $result = $this->wifiApi->createVoucher($voucherConfig);
        
        if ($result['success']) {
            // ربط الكرت بالغرفة في قاعدة بيانات الفندق
            $this->linkVoucherToRoom($result['data']['code'], $roomNumber);
            
            return $result['data'];
        }
        
        return null;
    }
    
    private function calculateStayDuration($checkIn, $checkOut) {
        $start = new DateTime($checkIn);
        $end = new DateTime($checkOut);
        return $start->diff($end)->days;
    }
}
```

---

**💡 نصيحة**: جرب هذه الأمثلة في بيئة التطوير أولاً قبل استخدامها في الإنتاج!