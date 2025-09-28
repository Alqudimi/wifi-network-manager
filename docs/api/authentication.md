# 🔐 المصادقة والتفويض

## نظرة عامة

نظام المصادقة يستخدم JWT (JSON Web Tokens) لحماية API endpoints وإدارة جلسات المستخدمين.

## تسجيل الدخول

### طلب تسجيل الدخول
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

### استجابة ناجحة
```json
{
  "success": true,
  "message": "تم تسجيل الدخول بنجاح",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "permissions": ["read", "write", "admin"]
    }
  }
}
```

## استخدام Token

### إرسال Token في الطلبات
```http
GET /api/vouchers
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

### أمثلة باستخدام curl
```bash
# الحصول على token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  jq -r '.data.token')

# استخدام token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/vouchers
```

## تجديد Token

### طلب تجديد
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

### استجابة التجديد
```json
{
  "success": true,
  "data": {
    "token": "new_access_token...",
    "expires_in": 86400
  }
}
```

## إدارة الصلاحيات

### أنواع الصلاحيات
```python
PERMISSIONS = {
    'admin': ['read', 'write', 'delete', 'admin', 'user_management'],
    'operator': ['read', 'write', 'delete'],
    'user': ['read']
}
```

### فحص الصلاحيات
```python
@admin_required
def admin_only_endpoint():
    return jsonify({'message': 'Admin access granted'})

@permission_required('write')
def write_access_endpoint():
    return jsonify({'message': 'Write access granted'})
```

## أمثلة عملية

### Python
```python
import requests

# تسجيل الدخول
login_data = {
    'username': 'admin',
    'password': 'admin123'
}

response = requests.post(
    'http://localhost:5000/api/auth/login',
    json=login_data
)

if response.status_code == 200:
    token = response.json()['data']['token']
    
    # استخدام token
    headers = {'Authorization': f'Bearer {token}'}
    vouchers = requests.get(
        'http://localhost:5000/api/vouchers',
        headers=headers
    )
    
    print(vouchers.json())
```

### JavaScript
```javascript
// تسجيل الدخول
async function login(username, password) {
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (data.success) {
        localStorage.setItem('token', data.data.token);
        return data.data.token;
    }
    throw new Error(data.error.message);
}

// استخدام token
async function getVouchers() {
    const token = localStorage.getItem('token');
    
    const response = await fetch('/api/vouchers', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    return response.json();
}
```

## معالجة الأخطاء

### أخطاء المصادقة الشائعة
```json
// كلمة مرور خاطئة
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "اسم المستخدم أو كلمة المرور غير صحيحة"
  }
}

// token منتهي الصلاحية
{
  "success": false,
  "error": {
    "code": "TOKEN_EXPIRED", 
    "message": "انتهت صلاحية الرمز المميز"
  }
}

// صلاحيات غير كافية
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "لا توجد صلاحية للوصول لهذا المورد"
  }
}
```