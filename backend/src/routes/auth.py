from flask import Blueprint, request, jsonify
from src.models.user import User, db
from src.utils.auth import auth_manager, token_required, rate_limit
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=300)  # 5 طلبات كل 5 دقائق
def register():
    """تسجيل مستخدم جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'الحقل {field} مطلوب'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        
        # التحقق من صحة البيانات
        if len(username) < 3:
            return jsonify({'message': 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'}), 400
        
        # التحقق من صحة البريد الإلكتروني
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'message': 'البريد الإلكتروني غير صحيح'}), 400
        
        # التحقق من عدم وجود المستخدم مسبقاً
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'اسم المستخدم موجود مسبقاً'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'البريد الإلكتروني موجود مسبقاً'}), 409
        
        # إنشاء المستخدم الجديد
        user = User(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            role='user'  # المستخدمون الجدد يحصلون على دور 'user' افتراضياً
        )
        
        db.session.add(user)
        db.session.commit()
        
        # توليد التوكنات
        access_token, refresh_token = auth_manager.generate_tokens(user.id)
        
        return jsonify({
            'message': 'تم تسجيل المستخدم بنجاح',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=300)  # 10 محاولات كل 5 دقائق
def login():
    """تسجيل الدخول"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # البحث عن المستخدم (بواسطة اسم المستخدم أو البريد الإلكتروني)
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'الحساب غير مفعل'}), 401
        
        # تحديث وقت آخر تسجيل دخول
        user.update_last_login()
        db.session.commit()
        
        # توليد التوكنات
        access_token, refresh_token = auth_manager.generate_tokens(user.id)
        
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """تجديد الـ access token"""
    try:
        data = request.get_json()
        
        if not data.get('refresh_token'):
            return jsonify({'message': 'الـ refresh token مطلوب'}), 400
        
        refresh_token = data['refresh_token']
        
        # تجديد الـ access token
        new_access_token = auth_manager.refresh_access_token(refresh_token)
        
        if not new_access_token:
            return jsonify({'message': 'الـ refresh token غير صالح أو منتهي الصلاحية'}), 401
        
        return jsonify({
            'access_token': new_access_token
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """تسجيل الخروج"""
    try:
        # إلغاء الـ refresh token
        auth_manager.revoke_token(current_user.id)
        
        return jsonify({'message': 'تم تسجيل الخروج بنجاح'}), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """الحصول على ملف المستخدم الشخصي"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """تحديث ملف المستخدم الشخصي"""
    try:
        data = request.get_json()
        
        # الحقول القابلة للتحديث
        updatable_fields = ['full_name', 'phone']
        
        for field in updatable_fields:
            if field in data:
                setattr(current_user, field, data[field].strip() if data[field] else None)
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الملف الشخصي بنجاح',
            'user': current_user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """تغيير كلمة المرور"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'الحقل {field} مطلوب'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # التحقق من كلمة المرور الحالية
        if not current_user.check_password(current_password):
            return jsonify({'message': 'كلمة المرور الحالية غير صحيحة'}), 401
        
        # التحقق من قوة كلمة المرور الجديدة
        if len(new_password) < 6:
            return jsonify({'message': 'كلمة المرور الجديدة يجب أن تكون 6 أحرف على الأقل'}), 400
        
        # تحديث كلمة المرور
        current_user.set_password(new_password)
        db.session.commit()
        
        # إلغاء جميع الـ refresh tokens للمستخدم
        auth_manager.revoke_token(current_user.id)
        
        return jsonify({'message': 'تم تغيير كلمة المرور بنجاح'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """التحقق من صحة التوكن"""
    try:
        data = request.get_json()
        
        if not data.get('token'):
            return jsonify({'message': 'التوكن مطلوب'}), 400
        
        token = data['token']
        payload = auth_manager.verify_token(token)
        
        if not payload:
            return jsonify({'valid': False, 'message': 'التوكن غير صالح'}), 200
        
        # الحصول على المستخدم
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'valid': False, 'message': 'المستخدم غير موجود أو غير مفعل'}), 200
        
        return jsonify({
            'valid': True,
            'user': user.to_dict(),
            'expires_at': payload['exp']
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500

