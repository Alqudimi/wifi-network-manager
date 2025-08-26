import jwt
import redis
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from src.models.user import User, db

# إعداد Redis للتخزين المؤقت
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class AuthManager:
    """مدير المصادقة والتوكنات"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة المدير مع التطبيق"""
        app.config.setdefault('JWT_SECRET_KEY', 'your-secret-key')
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    
    def generate_tokens(self, user_id):
        """توليد access token و refresh token"""
        now = datetime.utcnow()
        
        # Access Token
        access_payload = {
            'user_id': user_id,
            'type': 'access',
            'iat': now,
            'exp': now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
        access_token = jwt.encode(
            access_payload, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
        
        # Refresh Token
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': now + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
        }
        refresh_token = jwt.encode(
            refresh_payload, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
        
        # حفظ الـ refresh token في Redis
        redis_client.setex(
            f"refresh_token:{user_id}", 
            int(current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds()),
            refresh_token
        )
        
        return access_token, refresh_token
    
    def verify_token(self, token, token_type='access'):
        """التحقق من صحة التوكن"""
        try:
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            if payload.get('type') != token_type:
                return None
            
            # التحقق من انتهاء الصلاحية
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                return None
            
            # للـ refresh token، التحقق من وجوده في Redis
            if token_type == 'refresh':
                stored_token = redis_client.get(f"refresh_token:{payload['user_id']}")
                if stored_token != token:
                    return None
            
            return payload
        
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, user_id, token_type='refresh'):
        """إلغاء التوكن"""
        if token_type == 'refresh':
            redis_client.delete(f"refresh_token:{user_id}")
    
    def refresh_access_token(self, refresh_token):
        """تجديد الـ access token باستخدام refresh token"""
        payload = self.verify_token(refresh_token, 'refresh')
        if not payload:
            return None
        
        user_id = payload['user_id']
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return None
        
        # توليد access token جديد
        access_token, _ = self.generate_tokens(user_id)
        return access_token


# إنشاء مثيل مدير المصادقة
auth_manager = AuthManager()


def token_required(f):
    """ديكوريتر للتحقق من وجود توكن صالح"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # البحث عن التوكن في الهيدر
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'تنسيق التوكن غير صحيح'}), 401
        
        if not token:
            return jsonify({'message': 'التوكن مطلوب'}), 401
        
        # التحقق من صحة التوكن
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'message': 'التوكن غير صالح أو منتهي الصلاحية'}), 401
        
        # الحصول على المستخدم
        current_user = User.query.get(payload['user_id'])
        if not current_user or not current_user.is_active:
            return jsonify({'message': 'المستخدم غير موجود أو غير مفعل'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """ديكوريتر للتحقق من صلاحيات الإدارة"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'message': 'صلاحيات إدارية مطلوبة'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def operator_required(f):
    """ديكوريتر للتحقق من صلاحيات المشغل"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_operator():
            return jsonify({'message': 'صلاحيات مشغل مطلوبة'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def permission_required(permission):
    """ديكوريتر للتحقق من صلاحية معينة"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(current_user, *args, **kwargs):
            if not current_user.has_permission(permission):
                return jsonify({'message': f'الصلاحية {permission} مطلوبة'}), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated
    return decorator


class RateLimiter:
    """محدد معدل الطلبات"""
    
    def __init__(self, max_requests=100, window_seconds=3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier):
        """التحقق من السماح بالطلب"""
        key = f"rate_limit:{identifier}"
        current_requests = redis_client.get(key)
        
        if current_requests is None:
            # أول طلب في النافزة الزمنية
            redis_client.setex(key, self.window_seconds, 1)
            return True
        
        current_requests = int(current_requests)
        if current_requests >= self.max_requests:
            return False
        
        # زيادة عدد الطلبات
        redis_client.incr(key)
        return True
    
    def get_remaining_requests(self, identifier):
        """الحصول على عدد الطلبات المتبقية"""
        key = f"rate_limit:{identifier}"
        current_requests = redis_client.get(key)
        
        if current_requests is None:
            return self.max_requests
        
        return max(0, self.max_requests - int(current_requests))


def rate_limit(max_requests=100, window_seconds=3600):
    """ديكوريتر لتحديد معدل الطلبات"""
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # استخدام IP address كمعرف
            identifier = request.remote_addr
            
            if not limiter.is_allowed(identifier):
                return jsonify({
                    'message': 'تم تجاوز الحد المسموح من الطلبات',
                    'retry_after': window_seconds
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def get_current_user():
    """الحصول على المستخدم الحالي من التوكن"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return None
    
    if not token:
        return None
    
    payload = auth_manager.verify_token(token)
    if not payload:
        return None
    
    return User.query.get(payload['user_id'])

