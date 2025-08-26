import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.voucher import Voucher, VoucherBatch, UserSession
from src.models.network import NetworkSettings, RouterConfiguration
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.vouchers import vouchers_bp
from src.routes.admin import admin_bp
from src.utils.auth import auth_manager

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# إعداد CORS للسماح بالطلبات من أي مصدر
CORS(app, origins="*", supports_credentials=True)

# إعدادات التطبيق
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])

# إعداد قاعدة البيانات
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # استخدام PostgreSQL للإنتاج
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # استخدام SQLite للتطوير
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# تهيئة قاعدة البيانات
db.init_app(app)

# تهيئة مدير المصادقة
auth_manager.init_app(app)

# تسجيل المسارات
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(vouchers_bp, url_prefix='/api/vouchers')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# إنشاء الجداول وبيانات البذر
with app.app_context():
    db.create_all()
    
    # إنشاء مستخدم إداري افتراضي إذا لم يكن موجوداً
    from src.models.user import User
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password='admin123',
            full_name='مدير النظام',
            role='admin'
        )
        admin_user.is_active = True
        admin_user.is_verified = True
        db.session.add(admin_user)
        db.session.commit()
        print("تم إنشاء المستخدم الإداري الافتراضي: admin / admin123")

# مسار الصحة للتحقق من حالة الخادم
@app.route('/api/health')
def health_check():
    return {'status': 'ok', 'message': 'خادم إدارة شبكات Wi-Fi يعمل بنجاح'}

# مسار معلومات API
@app.route('/api/info')
def api_info():
    return {
        'name': 'WiFi Network Management API',
        'version': '1.0.0',
        'description': 'API لإدارة شبكات Wi-Fi ونظام الكروت',
        'endpoints': {
            'auth': '/api/auth',
            'vouchers': '/api/vouchers',
            'admin': '/api/admin',
            'users': '/api/users'
        }
    }

# خدمة الملفات الثابتة للواجهة الأمامية
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# معالج الأخطاء
@app.errorhandler(404)
def not_found(error):
    return {'message': 'المسار غير موجود'}, 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return {'message': 'خطأ داخلي في الخادم'}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
