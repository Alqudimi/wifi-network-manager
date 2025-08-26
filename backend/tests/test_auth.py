"""
اختبارات نظام المصادقة
"""

import pytest
import json
from src.models.user import User, db

class TestAuth:
    """اختبارات المصادقة والتسجيل"""
    
    def test_register_success(self, client):
        """اختبار تسجيل مستخدم جديد بنجاح"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'password123',
            'full_name': 'مستخدم جديد'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@test.com'
    
    def test_register_duplicate_username(self, client, admin_user):
        """اختبار تسجيل مستخدم باسم مستخدم موجود مسبقاً"""
        response = client.post('/api/auth/register', json={
            'username': 'test_admin',  # اسم موجود مسبقاً
            'email': 'newemail@test.com',
            'password': 'password123',
            'full_name': 'مستخدم جديد'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'اسم المستخدم موجود مسبقاً' in data['message']
    
    def test_register_duplicate_email(self, client, admin_user):
        """اختبار تسجيل مستخدم ببريد إلكتروني موجود مسبقاً"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'admin@test.com',  # بريد موجود مسبقاً
            'password': 'password123',
            'full_name': 'مستخدم جديد'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'البريد الإلكتروني موجود مسبقاً' in data['message']
    
    def test_register_missing_fields(self, client):
        """اختبار تسجيل مستخدم بحقول ناقصة"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            # email مفقود
            'password': 'password123'
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client, admin_user):
        """اختبار تسجيل الدخول بنجاح"""
        response = client.post('/api/auth/login', json={
            'username': 'test_admin',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'test_admin'
    
    def test_login_with_email(self, client, admin_user):
        """اختبار تسجيل الدخول بالبريد الإلكتروني"""
        response = client.post('/api/auth/login', json={
            'username': 'admin@test.com',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'admin@test.com'
    
    def test_login_wrong_password(self, client, admin_user):
        """اختبار تسجيل الدخول بكلمة مرور خاطئة"""
        response = client.post('/api/auth/login', json={
            'username': 'test_admin',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'كلمة المرور غير صحيحة' in data['message']
    
    def test_login_nonexistent_user(self, client):
        """اختبار تسجيل الدخول بمستخدم غير موجود"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'المستخدم غير موجود' in data['message']
    
    def test_login_inactive_user(self, client):
        """اختبار تسجيل الدخول بمستخدم غير نشط"""
        # إنشاء مستخدم غير نشط
        with client.application.app_context():
            user = User(
                username='inactive_user',
                email='inactive@test.com',
                password='password123',
                full_name='مستخدم غير نشط',
                role='user'
            )
            user.is_active = False
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'inactive_user',
            'password': 'password123'
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'الحساب غير نشط' in data['message']
    
    def test_get_profile_success(self, client, auth_headers_admin):
        """اختبار الحصول على الملف الشخصي"""
        response = client.get('/api/auth/profile', headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'test_admin'
        assert data['user']['role'] == 'admin'
    
    def test_get_profile_unauthorized(self, client):
        """اختبار الحصول على الملف الشخصي بدون مصادقة"""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
    
    def test_update_profile_success(self, client, auth_headers_admin):
        """اختبار تحديث الملف الشخصي"""
        response = client.put('/api/auth/profile', 
                            headers=auth_headers_admin,
                            json={
                                'full_name': 'اسم محدث',
                                'phone': '0501234567'
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['full_name'] == 'اسم محدث'
        assert data['user']['phone'] == '0501234567'
    
    def test_change_password_success(self, client, auth_headers_admin):
        """اختبار تغيير كلمة المرور"""
        response = client.post('/api/auth/change-password',
                             headers=auth_headers_admin,
                             json={
                                 'current_password': 'admin123',
                                 'new_password': 'newpassword123'
                             })
        
        assert response.status_code == 200
        
        # اختبار تسجيل الدخول بكلمة المرور الجديدة
        login_response = client.post('/api/auth/login', json={
            'username': 'test_admin',
            'password': 'newpassword123'
        })
        
        assert login_response.status_code == 200
    
    def test_change_password_wrong_current(self, client, auth_headers_admin):
        """اختبار تغيير كلمة المرور بكلمة مرور حالية خاطئة"""
        response = client.post('/api/auth/change-password',
                             headers=auth_headers_admin,
                             json={
                                 'current_password': 'wrongpassword',
                                 'new_password': 'newpassword123'
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'كلمة المرور الحالية غير صحيحة' in data['message']
    
    def test_logout_success(self, client, auth_headers_admin):
        """اختبار تسجيل الخروج"""
        response = client.post('/api/auth/logout', headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'تم تسجيل الخروج بنجاح' in data['message']
    
    def test_refresh_token_success(self, client, admin_user):
        """اختبار تجديد التوكن"""
        # تسجيل الدخول أولاً
        login_response = client.post('/api/auth/login', json={
            'username': 'test_admin',
            'password': 'admin123'
        })
        
        refresh_token = login_response.get_json()['refresh_token']
        
        # تجديد التوكن
        response = client.post('/api/auth/refresh', json={
            'refresh_token': refresh_token
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_refresh_token_invalid(self, client):
        """اختبار تجديد التوكن بتوكن غير صحيح"""
        response = client.post('/api/auth/refresh', json={
            'refresh_token': 'invalid_token'
        })
        
        assert response.status_code == 401

