"""
إعدادات pytest للاختبارات
"""

import pytest
import tempfile
import os
from src.main import app
from src.models.user import db, User
from src.models.voucher import VoucherBatch, Voucher
from src.models.network import NetworkSettings, RouterConfiguration

@pytest.fixture
def client():
    """إنشاء عميل اختبار Flask"""
    # إنشاء قاعدة بيانات مؤقتة
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.config["DATABASE"]}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def admin_user(client):
    """إنشاء مستخدم إداري للاختبار"""
    with app.app_context():
        admin = User(
            username='test_admin',
            email='admin@test.com',
            password='admin123',
            full_name='مدير الاختبار',
            role='admin'
        )
        admin.is_active = True
        admin.is_verified = True
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def operator_user(client):
    """إنشاء مستخدم مشغل للاختبار"""
    with app.app_context():
        operator = User(
            username='test_operator',
            email='operator@test.com',
            password='operator123',
            full_name='مشغل الاختبار',
            role='operator'
        )
        operator.is_active = True
        operator.is_verified = True
        db.session.add(operator)
        db.session.commit()
        return operator

@pytest.fixture
def regular_user(client):
    """إنشاء مستخدم عادي للاختبار"""
    with app.app_context():
        user = User(
            username='test_user',
            email='user@test.com',
            password='user123',
            full_name='مستخدم الاختبار',
            role='user'
        )
        user.is_active = True
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_headers_admin(client, admin_user):
    """الحصول على headers المصادقة للمدير"""
    response = client.post('/api/auth/login', json={
        'username': 'test_admin',
        'password': 'admin123'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def auth_headers_operator(client, operator_user):
    """الحصول على headers المصادقة للمشغل"""
    response = client.post('/api/auth/login', json={
        'username': 'test_operator',
        'password': 'operator123'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def auth_headers_user(client, regular_user):
    """الحصول على headers المصادقة للمستخدم العادي"""
    response = client.post('/api/auth/login', json={
        'username': 'test_user',
        'password': 'user123'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_voucher_batch(client, admin_user):
    """إنشاء دفعة كروت للاختبار"""
    with app.app_context():
        batch = VoucherBatch(
            name='دفعة اختبار',
            description='دفعة للاختبار',
            voucher_count=10,
            value='ساعة واحدة',
            duration_minutes=60,
            created_by=admin_user.id
        )
        db.session.add(batch)
        db.session.commit()
        
        # إنشاء الكروت
        for i in range(10):
            voucher = Voucher(
                batch_id=batch.id,
                code=f'TEST{i:04d}',
                value=batch.value,
                duration_minutes=batch.duration_minutes,
                max_usage_count=1
            )
            db.session.add(voucher)
        
        db.session.commit()
        return batch

@pytest.fixture
def sample_network_settings(client, admin_user):
    """إنشاء إعدادات شبكة للاختبار"""
    with app.app_context():
        settings = NetworkSettings(
            name='إعدادات اختبار',
            description='إعدادات للاختبار',
            network_name='TEST_WIFI',
            network_ip_range='192.168.1.0/24',
            gateway_ip='192.168.1.1',
            created_by=admin_user.id
        )
        db.session.add(settings)
        db.session.commit()
        return settings

