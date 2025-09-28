from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime, timedelta
import jwt
import secrets
import string
from config import Config
from database import db, init_db
from models.user import User
from models.voucher import Voucher
from models.network import Network
from models.router import Router
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.vouchers import vouchers_bp
from routes.networks import networks_bp
from routes.network_control import network_control_bp
from utils.network_manager import start_network_monitoring
from utils.auth import token_required, admin_required

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins="*")
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(vouchers_bp, url_prefix='/api/vouchers')
    app.register_blueprint(networks_bp, url_prefix='/api/networks')
    app.register_blueprint(network_control_bp, url_prefix='/api/control')
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/login')
    def login_page():
        """Login page"""
        return render_template('login.html')
    
    @app.route('/vouchers')
    def vouchers_page():
        """Vouchers management page"""
        return render_template('vouchers.html')
    
    @app.route('/networks')
    def networks_page():
        """Networks management page"""
        return render_template('networks.html')
    
    @app.route('/users')
    def users_page():
        """Users management page"""
        return render_template('users.html')
    
    @app.route('/network_control')
    def network_control_page():
        """Network control page"""
        return render_template('network_control.html')
    
    @app.route('/captive')
    def captive_portal():
        """Captive portal for WiFi authentication"""
        return render_template('captive_portal.html')
    
    @app.route('/api/stats/dashboard')
    @token_required
    def dashboard_stats(current_user):
        """Get dashboard statistics"""
        try:
            total_vouchers = Voucher.query.count()
            active_vouchers = Voucher.query.filter_by(status='active').count()
            used_vouchers = Voucher.query.filter_by(status='used').count()
            total_networks = Network.query.count()
            total_routers = Router.query.count()
            
            # Recent activity
            recent_vouchers = Voucher.query.order_by(Voucher.created_at.desc()).limit(5).all()
            
            stats = {
                'total_vouchers': total_vouchers,
                'active_vouchers': active_vouchers,
                'used_vouchers': used_vouchers,
                'total_networks': total_networks,
                'total_routers': total_routers,
                'recent_vouchers': [{
                    'id': v.id,
                    'code': v.code,
                    'status': v.status,
                    'created_at': v.created_at.isoformat()
                } for v in recent_vouchers]
            }
            
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voucher/redeem', methods=['POST'])
    def redeem_voucher():
        """Redeem a voucher code"""
        try:
            data = request.get_json()
            voucher_code = data.get('code', '').strip()
            
            if not voucher_code:
                return jsonify({'error': 'كود الكرت مطلوب'}), 400
            
            voucher = Voucher.query.filter_by(code=voucher_code, status='active').first()
            
            if not voucher:
                return jsonify({'error': 'كود غير صحيح أو منتهي الصلاحية'}), 404
            
            # Check if voucher is expired
            if voucher.expires_at and voucher.expires_at < datetime.utcnow():
                voucher.status = 'expired'
                db.session.commit()
                return jsonify({'error': 'الكرت منتهي الصلاحية'}), 400
            
            # Activate voucher
            voucher.status = 'used'
            voucher.used_at = datetime.utcnow()
            
            # Create session token for internet access
            session_token = secrets.token_urlsafe(32)
            voucher.session_token = session_token
            
            db.session.commit()
            
            return jsonify({
                'message': 'تم تفعيل الكرت بنجاح',
                'session_token': session_token,
                'duration_hours': voucher.duration_hours,
                'data_limit_mb': voucher.data_limit_mb
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    with app.app_context():
        init_db()
        
        # Create default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User()
            admin_user.username = 'admin'
            admin_user.email = 'admin@wifi-manager.local'
            admin_user.password_hash = generate_password_hash('admin123')
            admin_user.role = 'admin'
            admin_user.is_active = True
            db.session.add(admin_user)
            db.session.commit()
            print("Created default admin user: admin/admin123")
        
        # Start network monitoring
        try:
            start_network_monitoring(app)
            print("Network monitoring started")
        except Exception as e:
            print(f"Failed to start network monitoring: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
