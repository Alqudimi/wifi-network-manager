from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models.user import User
from database import db
from utils.auth import token_required, admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    """Get all users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user(current_user):
    """Create new user"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} مطلوب'}), 400
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'اسم المستخدم أو البريد الإلكتروني موجود مسبقاً'}), 400
        
        # Validate role
        valid_roles = ['admin', 'operator', 'user']
        if data['role'] not in valid_roles:
            return jsonify({'error': 'دور المستخدم غير صحيح'}), 400
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data['role'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء المستخدم بنجاح',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(current_user, user_id):
    """Update user"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'email' in data:
            user.email = data['email']
        
        if 'role' in data:
            valid_roles = ['admin', 'operator', 'user']
            if data['role'] not in valid_roles:
                return jsonify({'error': 'دور المستخدم غير صحيح'}), 400
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث المستخدم بنجاح',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    """Delete user"""
    try:
        if user_id == current_user.id:
            return jsonify({'error': 'لا يمكن حذف حسابك الشخصي'}), 400
        
        user = User.query.get_or_404(user_id)
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المستخدم بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_admin_stats(current_user):
    """Get admin statistics"""
    try:
        from models.voucher import Voucher
        from models.network import Network
        from models.router import Router
        
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'admin_users': User.query.filter_by(role='admin').count(),
            'operator_users': User.query.filter_by(role='operator').count(),
            'regular_users': User.query.filter_by(role='user').count(),
            'total_vouchers': Voucher.query.count(),
            'active_vouchers': Voucher.query.filter_by(status='active').count(),
            'used_vouchers': Voucher.query.filter_by(status='used').count(),
            'total_networks': Network.query.count(),
            'active_networks': Network.query.filter_by(is_active=True).count(),
            'total_routers': Router.query.count(),
            'active_routers': Router.query.filter_by(is_active=True).count()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
