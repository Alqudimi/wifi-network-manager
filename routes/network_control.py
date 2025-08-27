from flask import Blueprint, request, jsonify
from utils.auth import token_required, admin_required
from models.voucher import Voucher
from models.router import Router
from models.network import Network
from utils.router_manager import get_router_manager
from database import db
import json
from datetime import datetime, timedelta

network_control_bp = Blueprint('network_control', __name__)

@network_control_bp.route('/routers', methods=['GET'])
@token_required
def get_routers(current_user):
    """Get all configured routers"""
    try:
        routers = Router.query.all()
        return jsonify([router.to_dict() for router in routers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_control_bp.route('/routers', methods=['POST'])
@admin_required
def add_router(current_user):
    """Add new router configuration"""
    try:
        data = request.get_json()
        
        router = Router()
        router.name = data.get('name')
        router.brand = data.get('brand')
        router.model = data.get('model')
        router.ip_address = data.get('ip_address')
        router.username = data.get('username')
        router.password = data.get('password')
        router.api_port = data.get('api_port')
        router.is_active = True
        
        # Test connection
        try:
            manager = get_router_manager(router)
            if manager.test_connection():
                router.status = 'connected'
                router.last_seen = datetime.utcnow()
            else:
                router.status = 'disconnected'
        except Exception:
            router.status = 'error'
        
        db.session.add(router)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة الراوتر بنجاح',
            'router': router.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_control_bp.route('/routers/<int:router_id>/test', methods=['POST'])
@admin_required
def test_router_connection(current_user, router_id):
    """Test router connection"""
    try:
        router = Router.query.get_or_404(router_id)
        
        manager = get_router_manager(router)
        connected = manager.test_connection()
        
        if connected:
            router.status = 'connected'
            router.last_seen = datetime.utcnow()
            message = 'الاتصال بالراوتر ناجح'
        else:
            router.status = 'disconnected'
            message = 'فشل في الاتصال بالراوتر'
        
        db.session.commit()
        
        return jsonify({
            'connected': connected,
            'message': message,
            'router': router.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_control_bp.route('/vouchers/create_batch', methods=['POST'])
@admin_required
def create_voucher_batch(current_user):
    """Create batch of vouchers with advanced options"""
    try:
        data = request.get_json()
        
        quantity = int(data.get('quantity', 1))
        batch_id = f"BATCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Voucher configuration
        duration_hours = int(data.get('duration_hours', 24))
        data_limit_mb = data.get('data_limit_mb')
        speed_limit_kbps = data.get('speed_limit_kbps')
        voucher_type = data.get('voucher_type', 'standard')
        price = float(data.get('price', 0))
        
        vouchers = []
        
        for i in range(quantity):
            voucher = Voucher()
            voucher.batch_id = batch_id
            voucher.duration_hours = duration_hours
            voucher.data_limit_mb = int(data_limit_mb) if data_limit_mb else None
            voucher.speed_limit_kbps = int(speed_limit_kbps) if speed_limit_kbps else None
            voucher.voucher_type = voucher_type
            voucher.price = price
            voucher.created_by = current_user.id
            
            # Set expiration date for voucher usage
            if data.get('voucher_expires_days'):
                voucher.expires_at = datetime.utcnow() + timedelta(days=int(data.get('voucher_expires_days')))
            
            # Network restrictions
            if data.get('allowed_networks'):
                voucher.allowed_networks = json.dumps(data.get('allowed_networks'))
            
            # Generate QR code
            base_url = data.get('base_url', 'http://localhost:5000')
            voucher.generate_qr_data(base_url)
            
            db.session.add(voucher)
            vouchers.append(voucher)
        
        db.session.commit()
        
        return jsonify({
            'message': f'تم إنشاء {quantity} كارت بنجاح',
            'batch_id': batch_id,
            'vouchers': [v.to_dict() for v in vouchers]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_control_bp.route('/vouchers/<voucher_code>/activate', methods=['POST'])
def activate_voucher(voucher_code):
    """Activate voucher and grant network access"""
    try:
        data = request.get_json()
        client_mac = data.get('client_mac')
        client_ip = data.get('client_ip')
        
        voucher = Voucher.query.filter_by(code=voucher_code).first()
        
        if not voucher:
            return jsonify({'error': 'كود الكارت غير صحيح'}), 404
        
        if not voucher.is_valid():
            return jsonify({'error': 'كارت الاتصال منتهي الصلاحية أو مستخدم'}), 400
        
        # Mark voucher as used
        voucher.mark_as_used()
        voucher.session_start = datetime.utcnow()
        voucher.client_mac = client_mac
        voucher.client_ip = client_ip
        
        # Calculate session end time
        if voucher.duration_hours:
            voucher.session_end = datetime.utcnow() + timedelta(hours=voucher.duration_hours)
        
        # Apply voucher to router(s)
        routers = Router.query.filter_by(is_active=True).all()
        
        for router in routers:
            try:
                manager = get_router_manager(router)
                if manager.connect():
                    # Add user to router's hotspot/guest system
                    if router.brand == 'MikroTik':
                        success = manager.add_hotspot_user(
                            username=voucher_code,
                            password=voucher.session_token,
                            profile='voucher_profile'
                        )
                    elif router.brand == 'Ubiquiti':
                        success = manager.add_guest_user(
                            username=voucher_code,
                            password=voucher.session_token,
                            duration_minutes=voucher.duration_hours * 60 if voucher.duration_hours else 1440
                        )
                    else:
                        success = False
                    
                    if success:
                        router.last_seen = datetime.utcnow()
                        router.status = 'connected'
                
                manager.disconnect()
                
            except Exception as e:
                print(f"Error applying voucher to router {router.name}: {e}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تفعيل كارت الاتصال بنجاح',
            'session_token': voucher.session_token,
            'duration_hours': voucher.duration_hours,
            'data_limit_mb': voucher.data_limit_mb,
            'speed_limit_kbps': voucher.speed_limit_kbps,
            'session_end': voucher.session_end.isoformat() if voucher.session_end else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_control_bp.route('/vouchers/<voucher_code>/usage', methods=['GET'])
def get_voucher_usage(voucher_code):
    """Get voucher usage statistics"""
    try:
        voucher = Voucher.query.filter_by(code=voucher_code).first()
        
        if not voucher:
            return jsonify({'error': 'كود الكارت غير صحيح'}), 404
        
        usage_info = {
            'code': voucher.code,
            'status': voucher.status,
            'data_used_mb': voucher.data_used_mb,
            'data_limit_mb': voucher.data_limit_mb,
            'session_start': voucher.session_start.isoformat() if voucher.session_start else None,
            'session_end': voucher.session_end.isoformat() if voucher.session_end else None,
            'remaining_time': None,
            'remaining_data': None
        }
        
        # Calculate remaining time
        if voucher.session_end and voucher.status == 'used':
            remaining_seconds = (voucher.session_end - datetime.utcnow()).total_seconds()
            if remaining_seconds > 0:
                usage_info['remaining_time'] = int(remaining_seconds / 60)  # in minutes
            else:
                usage_info['remaining_time'] = 0
        
        # Calculate remaining data
        if voucher.data_limit_mb:
            usage_info['remaining_data'] = max(0, voucher.data_limit_mb - voucher.data_used_mb)
        
        return jsonify(usage_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_control_bp.route('/vouchers/<voucher_code>/disconnect', methods=['POST'])
@admin_required
def disconnect_voucher(current_user, voucher_code):
    """Disconnect voucher session"""
    try:
        voucher = Voucher.query.filter_by(code=voucher_code).first()
        
        if not voucher:
            return jsonify({'error': 'كود الكارت غير صحيح'}), 404
        
        if voucher.status != 'used':
            return jsonify({'error': 'الكارت غير نشط'}), 400
        
        # Remove from routers
        routers = Router.query.filter_by(is_active=True).all()
        
        for router in routers:
            try:
                manager = get_router_manager(router)
                if manager.connect():
                    if router.brand == 'MikroTik':
                        manager.remove_hotspot_user(voucher_code)
                    # Add disconnect logic for other router types
                
                manager.disconnect()
                
            except Exception as e:
                print(f"Error disconnecting voucher from router {router.name}: {e}")
        
        # Mark voucher as expired
        voucher.status = 'expired'
        voucher.session_end = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'تم قطع الاتصال بنجاح'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@network_control_bp.route('/network/clients', methods=['GET'])
@token_required
def get_connected_clients(current_user):
    """Get list of connected clients"""
    try:
        # Get active vouchers (connected clients)
        active_vouchers = Voucher.query.filter_by(status='used').filter(
            Voucher.session_end > datetime.utcnow()
        ).all()
        
        clients = []
        for voucher in active_vouchers:
            if voucher.session_start and voucher.session_end:
                remaining_time = (voucher.session_end - datetime.utcnow()).total_seconds() / 60
                if remaining_time > 0:
                    clients.append({
                        'voucher_code': voucher.code,
                        'client_mac': voucher.client_mac,
                        'client_ip': voucher.client_ip,
                        'session_start': voucher.session_start.isoformat(),
                        'remaining_minutes': int(remaining_time),
                        'data_used_mb': voucher.data_used_mb,
                        'data_limit_mb': voucher.data_limit_mb
                    })
        
        return jsonify({
            'connected_clients': len(clients),
            'clients': clients
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500