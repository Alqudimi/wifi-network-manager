"""
اختبارات وظائف الإدارة
"""

import pytest
import json
from src.models.user import User, db
from src.models.network import NetworkSettings, RouterConfiguration

class TestAdmin:
    """اختبارات وظائف الإدارة"""
    
    def test_get_users_success(self, client, auth_headers_admin, admin_user, operator_user):
        """اختبار الحصول على قائمة المستخدمين"""
        response = client.get('/api/admin/users', headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert 'pagination' in data
        assert len(data['users']) >= 2  # admin + operator
    
    def test_get_users_operator_forbidden(self, client, auth_headers_operator):
        """اختبار منع المشغل من الوصول لقائمة المستخدمين"""
        response = client.get('/api/admin/users', headers=auth_headers_operator)
        
        assert response.status_code == 403
    
    def test_create_user_success(self, client, auth_headers_admin):
        """اختبار إنشاء مستخدم جديد"""
        response = client.post('/api/admin/users',
                             headers=auth_headers_admin,
                             json={
                                 'username': 'new_operator',
                                 'email': 'newoperator@test.com',
                                 'password': 'password123',
                                 'full_name': 'مشغل جديد',
                                 'role': 'operator',
                                 'phone': '0501234567'
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'new_operator'
        assert data['user']['role'] == 'operator'
        assert data['user']['is_active'] == True
    
    def test_create_user_invalid_role(self, client, auth_headers_admin):
        """اختبار إنشاء مستخدم بدور غير صحيح"""
        response = client.post('/api/admin/users',
                             headers=auth_headers_admin,
                             json={
                                 'username': 'invalid_user',
                                 'email': 'invalid@test.com',
                                 'password': 'password123',
                                 'role': 'invalid_role'
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'الدور غير صحيح' in data['message']
    
    def test_update_user_success(self, client, auth_headers_admin, operator_user):
        """اختبار تحديث مستخدم"""
        user_id = operator_user.id
        response = client.put(f'/api/admin/users/{user_id}',
                            headers=auth_headers_admin,
                            json={
                                'full_name': 'اسم محدث',
                                'phone': '0509876543',
                                'is_active': False
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['full_name'] == 'اسم محدث'
        assert data['user']['phone'] == '0509876543'
        assert data['user']['is_active'] == False
    
    def test_delete_user_success(self, client, auth_headers_admin, operator_user):
        """اختبار حذف مستخدم"""
        user_id = operator_user.id
        response = client.delete(f'/api/admin/users/{user_id}',
                               headers=auth_headers_admin)
        
        assert response.status_code == 200
        
        # التحقق من أن المستخدم تم تعطيله وليس حذفه
        with client.application.app_context():
            user = User.query.get(user_id)
            assert user.is_active == False
            assert user.username.startswith('deleted_')
    
    def test_delete_own_account_forbidden(self, client, auth_headers_admin, admin_user):
        """اختبار منع حذف الحساب الشخصي"""
        user_id = admin_user.id
        response = client.delete(f'/api/admin/users/{user_id}',
                               headers=auth_headers_admin)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'لا يمكن حذف حسابك الخاص' in data['message']
    
    def test_get_dashboard_stats_success(self, client, auth_headers_operator):
        """اختبار الحصول على إحصائيات لوحة التحكم"""
        response = client.get('/api/admin/dashboard/stats', headers=auth_headers_operator)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'general_stats' in data
        assert 'period_stats' in data
        assert 'daily_stats' in data
        
        # التحقق من وجود الإحصائيات الأساسية
        general_stats = data['general_stats']
        assert 'total_users' in general_stats
        assert 'total_vouchers' in general_stats
        assert 'active_vouchers' in general_stats
    
    def test_get_network_settings_success(self, client, auth_headers_operator, sample_network_settings):
        """اختبار الحصول على إعدادات الشبكة"""
        response = client.get('/api/admin/network-settings', headers=auth_headers_operator)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'settings' in data
        assert len(data['settings']) >= 1
    
    def test_create_network_settings_success(self, client, auth_headers_admin):
        """اختبار إنشاء إعدادات شبكة جديدة"""
        response = client.post('/api/admin/network-settings',
                             headers=auth_headers_admin,
                             json={
                                 'name': 'إعدادات جديدة',
                                 'description': 'وصف الإعدادات',
                                 'network_name': 'NEW_WIFI',
                                 'network_ip_range': '10.0.0.0/24',
                                 'gateway_ip': '10.0.0.1',
                                 'dns_primary': '8.8.8.8',
                                 'dns_secondary': '8.8.4.4'
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'settings' in data
        assert data['settings']['name'] == 'إعدادات جديدة'
        assert data['settings']['network_name'] == 'NEW_WIFI'
    
    def test_update_network_settings_success(self, client, auth_headers_admin, sample_network_settings):
        """اختبار تحديث إعدادات الشبكة"""
        settings_id = sample_network_settings.id
        response = client.put(f'/api/admin/network-settings/{settings_id}',
                            headers=auth_headers_admin,
                            json={
                                'name': 'إعدادات محدثة',
                                'description': 'وصف محدث',
                                'session_timeout': 7200,
                                'is_default': True
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['settings']['name'] == 'إعدادات محدثة'
        assert data['settings']['session_timeout'] == 7200
        assert data['settings']['is_default'] == True
    
    def test_get_routers_success(self, client, auth_headers_operator):
        """اختبار الحصول على قائمة الراوترات"""
        response = client.get('/api/admin/routers', headers=auth_headers_operator)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'routers' in data
    
    def test_create_router_success(self, client, auth_headers_admin):
        """اختبار إضافة راوتر جديد"""
        response = client.post('/api/admin/routers',
                             headers=auth_headers_admin,
                             json={
                                 'name': 'راوتر اختبار',
                                 'router_type': 'mikrotik',
                                 'ip_address': '192.168.1.1',
                                 'username': 'admin',
                                 'password': 'password',
                                 'api_port': 8728,
                                 'description': 'راوتر للاختبار'
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'router' in data
        assert data['router']['name'] == 'راوتر اختبار'
        assert data['router']['router_type'] == 'mikrotik'
        assert data['router']['ip_address'] == '192.168.1.1'
    
    def test_create_router_invalid_type(self, client, auth_headers_admin):
        """اختبار إضافة راوتر بنوع غير صحيح"""
        response = client.post('/api/admin/routers',
                             headers=auth_headers_admin,
                             json={
                                 'name': 'راوتر خاطئ',
                                 'router_type': 'invalid_type',
                                 'ip_address': '192.168.1.1'
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'نوع الراوتر غير صحيح' in data['message']
    
    def test_test_router_connection(self, client, auth_headers_admin):
        """اختبار اختبار الاتصال بالراوتر"""
        # إنشاء راوتر أولاً
        with client.application.app_context():
            router = RouterConfiguration(
                name='راوتر اختبار',
                router_type='mikrotik',
                ip_address='192.168.1.1',
                username='admin',
                password='password',
                created_by=1
            )
            db.session.add(router)
            db.session.commit()
            router_id = router.id
        
        response = client.post(f'/api/admin/routers/{router_id}/test',
                             headers=auth_headers_admin)
        
        # نتوقع فشل الاتصال لأن الراوتر غير موجود فعلياً
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        # في بيئة الاختبار، الاتصال سيفشل
        assert data['success'] == False
    
    def test_get_router_configuration(self, client, auth_headers_admin):
        """اختبار الحصول على أوامر إعداد الراوتر"""
        # إنشاء راوتر أولاً
        with client.application.app_context():
            router = RouterConfiguration(
                name='راوتر إعداد',
                router_type='mikrotik',
                ip_address='192.168.1.1',
                username='admin',
                password='password',
                created_by=1
            )
            db.session.add(router)
            db.session.commit()
            router_id = router.id
        
        response = client.get(f'/api/admin/routers/{router_id}/configuration',
                            headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'router' in data
        assert 'configuration_commands' in data
        assert len(data['configuration_commands']) > 0
    
    def test_get_usage_report_success(self, client, auth_headers_operator):
        """اختبار الحصول على تقرير الاستخدام"""
        response = client.get('/api/admin/reports/usage?days=7', 
                            headers=auth_headers_operator)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'period' in data
        assert 'daily_usage' in data
        assert 'hourly_usage' in data
        assert data['period']['days'] == 7

