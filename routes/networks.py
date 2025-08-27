from flask import Blueprint, request, jsonify
from models.network import Network
from models.router import Router
from database import db
from utils.auth import token_required, admin_required

networks_bp = Blueprint('networks', __name__)

@networks_bp.route('/', methods=['GET'])
@token_required
def get_networks(current_user):
    """Get all networks"""
    try:
        networks = Network.query.order_by(Network.created_at.desc()).all()
        return jsonify({
            'networks': [network.to_dict() for network in networks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@networks_bp.route('/', methods=['POST'])
@admin_required
def create_network(current_user):
    """Create new network"""
    try:
        data = request.get_json()
        
        required_fields = ['ssid', 'security_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} مطلوب'}), 400
        
        # Check if SSID already exists
        existing_network = Network.query.filter_by(ssid=data['ssid']).first()
        if existing_network:
            return jsonify({'error': 'اسم الشبكة موجود مسبقاً'}), 400
        
        # Validate security type
        valid_security_types = ['WPA2-Personal', 'WPA3-Personal', 'Open']
        if data['security_type'] not in valid_security_types:
            return jsonify({'error': 'نوع الحماية غير صحيح'}), 400
        
        # Password required for secured networks
        if data['security_type'] != 'Open' and not data.get('password'):
            return jsonify({'error': 'كلمة المرور مطلوبة للشبكات المحمية'}), 400
        
        network = Network(
            ssid=data['ssid'],
            password=data.get('password'),
            security_type=data['security_type'],
            description=data.get('description'),
            captive_portal_enabled=data.get('captive_portal_enabled', True),
            portal_title=data.get('portal_title', 'WiFi Access'),
            portal_message=data.get('portal_message', 'Please enter your voucher code'),
            max_download_mbps=data.get('max_download_mbps'),
            max_upload_mbps=data.get('max_upload_mbps'),
            router_id=data.get('router_id')
        )
        
        db.session.add(network)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء الشبكة بنجاح',
            'network': network.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@networks_bp.route('/<int:network_id>', methods=['PUT'])
@admin_required
def update_network(current_user, network_id):
    """Update network"""
    try:
        network = Network.query.get_or_404(network_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'ssid' in data:
            # Check if new SSID already exists (excluding current network)
            existing = Network.query.filter(
                Network.ssid == data['ssid'],
                Network.id != network_id
            ).first()
            if existing:
                return jsonify({'error': 'اسم الشبكة موجود مسبقاً'}), 400
            network.ssid = data['ssid']
        
        if 'password' in data:
            network.password = data['password']
        
        if 'security_type' in data:
            valid_security_types = ['WPA2-Personal', 'WPA3-Personal', 'Open']
            if data['security_type'] not in valid_security_types:
                return jsonify({'error': 'نوع الحماية غير صحيح'}), 400
            network.security_type = data['security_type']
        
        if 'description' in data:
            network.description = data['description']
        
        if 'is_active' in data:
            network.is_active = data['is_active']
        
        if 'captive_portal_enabled' in data:
            network.captive_portal_enabled = data['captive_portal_enabled']
        
        if 'portal_title' in data:
            network.portal_title = data['portal_title']
        
        if 'portal_message' in data:
            network.portal_message = data['portal_message']
        
        if 'max_download_mbps' in data:
            network.max_download_mbps = data['max_download_mbps']
        
        if 'max_upload_mbps' in data:
            network.max_upload_mbps = data['max_upload_mbps']
        
        if 'router_id' in data:
            network.router_id = data['router_id']
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الشبكة بنجاح',
            'network': network.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@networks_bp.route('/<int:network_id>', methods=['DELETE'])
@admin_required
def delete_network(current_user, network_id):
    """Delete network"""
    try:
        network = Network.query.get_or_404(network_id)
        
        db.session.delete(network)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الشبكة بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@networks_bp.route('/routers', methods=['GET'])
@token_required
def get_routers(current_user):
    """Get all routers"""
    try:
        routers = Router.query.order_by(Router.created_at.desc()).all()
        return jsonify({
            'routers': [router.to_dict() for router in routers]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@networks_bp.route('/routers', methods=['POST'])
@admin_required
def create_router(current_user):
    """Create new router"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'brand', 'ip_address', 'username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} مطلوب'}), 400
        
        # Validate brand
        valid_brands = ['MikroTik', 'Ubiquiti', 'Cisco']
        if data['brand'] not in valid_brands:
            return jsonify({'error': 'نوع الراوتر غير صحيح'}), 400
        
        router = Router(
            name=data['name'],
            brand=data['brand'],
            model=data.get('model'),
            ip_address=data['ip_address'],
            username=data['username'],
            password=data['password'],
            api_port=data.get('api_port'),
            radius_server=data.get('radius_server'),
            radius_secret=data.get('radius_secret')
        )
        
        db.session.add(router)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء الراوتر بنجاح',
            'router': router.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@networks_bp.route('/routers/<int:router_id>', methods=['PUT'])
@admin_required
def update_router(current_user, router_id):
    """Update router"""
    try:
        router = Router.query.get_or_404(router_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            router.name = data['name']
        
        if 'brand' in data:
            valid_brands = ['MikroTik', 'Ubiquiti', 'Cisco']
            if data['brand'] not in valid_brands:
                return jsonify({'error': 'نوع الراوتر غير صحيح'}), 400
            router.brand = data['brand']
        
        if 'model' in data:
            router.model = data['model']
        
        if 'ip_address' in data:
            router.ip_address = data['ip_address']
        
        if 'username' in data:
            router.username = data['username']
        
        if 'password' in data:
            router.password = data['password']
        
        if 'api_port' in data:
            router.api_port = data['api_port']
        
        if 'is_active' in data:
            router.is_active = data['is_active']
        
        if 'radius_server' in data:
            router.radius_server = data['radius_server']
        
        if 'radius_secret' in data:
            router.radius_secret = data['radius_secret']
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الراوتر بنجاح',
            'router': router.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@networks_bp.route('/routers/<int:router_id>', methods=['DELETE'])
@admin_required
def delete_router(current_user, router_id):
    """Delete router"""
    try:
        router = Router.query.get_or_404(router_id)
        
        # Check if router has associated networks
        if router.networks:
            return jsonify({'error': 'لا يمكن حذف راوتر مرتبط بشبكات'}), 400
        
        db.session.delete(router)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الراوتر بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
