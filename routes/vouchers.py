from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.voucher import Voucher
from database import db
from utils.auth import token_required
from utils.qr_generator import generate_qr_code
import uuid

vouchers_bp = Blueprint('vouchers', __name__)

@vouchers_bp.route('/', methods=['GET'])
@token_required
def get_vouchers(current_user):
    """Get vouchers with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        batch_id = request.args.get('batch_id')
        
        query = Voucher.query
        
        if status:
            query = query.filter_by(status=status)
        
        if batch_id:
            query = query.filter_by(batch_id=batch_id)
        
        vouchers = query.order_by(Voucher.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'vouchers': [voucher.to_dict() for voucher in vouchers.items],
            'total': vouchers.total,
            'pages': vouchers.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vouchers_bp.route('/batch', methods=['POST'])
@token_required
def create_voucher_batch(current_user):
    """Create a batch of vouchers"""
    try:
        data = request.get_json()
        
        # Validate input
        count = data.get('count', 1)
        duration_hours = data.get('duration_hours', 24)
        data_limit_mb = data.get('data_limit_mb')
        
        if count < 1 or count > 1000:
            return jsonify({'error': 'عدد الكروت يجب أن يكون بين 1 و 1000'}), 400
        
        if duration_hours < 1 or duration_hours > 8760:  # Max 1 year
            return jsonify({'error': 'مدة الصلاحية يجب أن تكون بين 1 ساعة و 8760 ساعة'}), 400
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())[:8].upper()
        
        vouchers = []
        for _ in range(count):
            voucher = Voucher(
                batch_id=batch_id,
                duration_hours=duration_hours,
                data_limit_mb=data_limit_mb,
                created_by=current_user.id
            )
            voucher.generate_qr_data()
            vouchers.append(voucher)
            db.session.add(voucher)
        
        db.session.commit()
        
        return jsonify({
            'message': f'تم إنشاء {count} كرت بنجاح',
            'batch_id': batch_id,
            'vouchers': [voucher.to_dict() for voucher in vouchers]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vouchers_bp.route('/<int:voucher_id>', methods=['GET'])
@token_required
def get_voucher(current_user, voucher_id):
    """Get specific voucher details"""
    try:
        voucher = Voucher.query.get_or_404(voucher_id)
        return jsonify(voucher.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vouchers_bp.route('/<int:voucher_id>', methods=['PUT'])
@token_required
def update_voucher(current_user, voucher_id):
    """Update voucher"""
    try:
        voucher = Voucher.query.get_or_404(voucher_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'status' in data:
            valid_statuses = ['active', 'disabled', 'expired']
            if data['status'] not in valid_statuses:
                return jsonify({'error': 'حالة الكرت غير صحيحة'}), 400
            voucher.status = data['status']
        
        if 'duration_hours' in data and voucher.status == 'active':
            voucher.duration_hours = data['duration_hours']
        
        if 'data_limit_mb' in data and voucher.status == 'active':
            voucher.data_limit_mb = data['data_limit_mb']
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الكرت بنجاح',
            'voucher': voucher.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vouchers_bp.route('/<int:voucher_id>', methods=['DELETE'])
@token_required
def delete_voucher(current_user, voucher_id):
    """Delete voucher"""
    try:
        voucher = Voucher.query.get_or_404(voucher_id)
        
        if voucher.status == 'used':
            return jsonify({'error': 'لا يمكن حذف كرت مستخدم'}), 400
        
        db.session.delete(voucher)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الكرت بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vouchers_bp.route('/batches', methods=['GET'])
@token_required
def get_batches(current_user):
    """Get voucher batches"""
    try:
        batches = db.session.query(
            Voucher.batch_id,
            db.func.count(Voucher.id).label('total_count'),
            db.func.sum(db.case([(Voucher.status == 'active', 1)], else_=0)).label('active_count'),
            db.func.sum(db.case([(Voucher.status == 'used', 1)], else_=0)).label('used_count'),
            db.func.min(Voucher.created_at).label('created_at')
        ).filter(
            Voucher.batch_id.isnot(None)
        ).group_by(
            Voucher.batch_id
        ).order_by(
            db.func.min(Voucher.created_at).desc()
        ).all()
        
        result = []
        for batch in batches:
            result.append({
                'batch_id': batch.batch_id,
                'total_count': batch.total_count,
                'active_count': batch.active_count or 0,
                'used_count': batch.used_count or 0,
                'created_at': batch.created_at.isoformat() if batch.created_at else None
            })
        
        return jsonify({'batches': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vouchers_bp.route('/batch/<batch_id>/print', methods=['GET'])
@token_required
def print_batch(current_user, batch_id):
    """Get batch vouchers for printing"""
    try:
        vouchers = Voucher.query.filter_by(batch_id=batch_id).all()
        
        if not vouchers:
            return jsonify({'error': 'لم يتم العثور على الدفعة'}), 404
        
        print_data = []
        for voucher in vouchers:
            qr_code_base64 = generate_qr_code(voucher.qr_code_data)
            print_data.append({
                'code': voucher.code,
                'duration_hours': voucher.duration_hours,
                'data_limit_mb': voucher.data_limit_mb,
                'expires_at': voucher.expires_at.isoformat() if voucher.expires_at else None,
                'qr_code': qr_code_base64
            })
        
        return jsonify({
            'batch_id': batch_id,
            'vouchers': print_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
