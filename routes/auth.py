from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from models.user import User
from database import db
from utils.auth import token_required
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'الحساب غير مفعل'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate JWT token
        token_payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, Config.JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """User logout endpoint"""
    try:
        # In a real implementation, you might want to blacklist the token
        return jsonify({'message': 'تم تسجيل الخروج بنجاح'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    try:
        return jsonify(current_user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update current user profile"""
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'email' in data:
            current_user.email = data['email']
        
        # Change password if provided
        if 'current_password' in data and 'new_password' in data:
            if not current_user.check_password(data['current_password']):
                return jsonify({'error': 'كلمة المرور الحالية غير صحيحة'}), 400
            
            current_user.set_password(data['new_password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الملف الشخصي بنجاح',
            'user': current_user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'valid': False, 'error': 'No token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        
        if not user or not user.is_active:
            return jsonify({'valid': False, 'error': 'Invalid user'}), 401
        
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500
