"""
اختبارات نظام الكروت
"""

import pytest
import json
from src.models.voucher import VoucherBatch, Voucher, UserSession, db

class TestVouchers:
    """اختبارات إدارة الكروت"""
    
    def test_create_batch_success(self, client, auth_headers_admin):
        """اختبار إنشاء دفعة كروت بنجاح"""
        response = client.post('/api/vouchers/batches',
                             headers=auth_headers_admin,
                             json={
                                 'name': 'دفعة جديدة',
                                 'description': 'وصف الدفعة',
                                 'voucher_count': 5,
                                 'value': 'ساعتان',
                                 'duration_minutes': 120,
                                 'data_limit_mb': 1024,
                                 'max_usage_count': 1
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'batch' in data
        assert data['batch']['name'] == 'دفعة جديدة'
        assert data['batch']['voucher_count'] == 5
        assert len(data['vouchers']) == 5
        
        # التحقق من أن الكروت تم إنشاؤها
        for voucher in data['vouchers']:
            assert voucher['code'] is not None
            assert voucher['value'] == 'ساعتان'
            assert voucher['duration_minutes'] == 120
    
    def test_create_batch_operator_permission(self, client, auth_headers_operator):
        """اختبار إنشاء دفعة كروت بصلاحية مشغل"""
        response = client.post('/api/vouchers/batches',
                             headers=auth_headers_operator,
                             json={
                                 'name': 'دفعة مشغل',
                                 'voucher_count': 3,
                                 'value': 'ساعة واحدة',
                                 'duration_minutes': 60
                             })
        
        assert response.status_code == 201
    
    def test_create_batch_user_forbidden(self, client, auth_headers_user):
        """اختبار منع المستخدم العادي من إنشاء دفعة كروت"""
        response = client.post('/api/vouchers/batches',
                             headers=auth_headers_user,
                             json={
                                 'name': 'دفعة محظورة',
                                 'voucher_count': 3,
                                 'value': 'ساعة واحدة'
                             })
        
        assert response.status_code == 403
    
    def test_create_batch_missing_fields(self, client, auth_headers_admin):
        """اختبار إنشاء دفعة كروت بحقول ناقصة"""
        response = client.post('/api/vouchers/batches',
                             headers=auth_headers_admin,
                             json={
                                 'name': 'دفعة ناقصة'
                                 # voucher_count مفقود
                             })
        
        assert response.status_code == 400
    
    def test_get_batches_success(self, client, auth_headers_operator, sample_voucher_batch):
        """اختبار الحصول على قائمة الدفعات"""
        response = client.get('/api/vouchers/batches', headers=auth_headers_operator)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'batches' in data
        assert len(data['batches']) >= 1
        assert data['batches'][0]['name'] == 'دفعة اختبار'
    
    def test_get_batch_details(self, client, auth_headers_operator, sample_voucher_batch):
        """اختبار الحصول على تفاصيل دفعة محددة"""
        batch_id = sample_voucher_batch.id
        response = client.get(f'/api/vouchers/batches/{batch_id}', 
                            headers=auth_headers_operator)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'batch' in data
        assert data['batch']['id'] == batch_id
        assert data['batch']['name'] == 'دفعة اختبار'
    
    def test_get_batch_vouchers(self, client, auth_headers_operator, sample_voucher_batch):
        """اختبار الحصول على كروت دفعة محددة"""
        batch_id = sample_voucher_batch.id
        response = client.get(f'/api/vouchers/batches/{batch_id}/vouchers',
                            headers=auth_headers_operator)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'vouchers' in data
        assert len(data['vouchers']) == 10
        
        # التحقق من بيانات الكروت
        for voucher in data['vouchers']:
            assert voucher['batch_id'] == batch_id
            assert voucher['code'].startswith('TEST')
    
    def test_check_voucher_valid(self, client, sample_voucher_batch):
        """اختبار التحقق من كرت صحيح"""
        # الحصول على كود كرت من الدفعة
        with client.application.app_context():
            voucher = Voucher.query.filter_by(batch_id=sample_voucher_batch.id).first()
            voucher_code = voucher.code
        
        response = client.post('/api/vouchers/check', json={
            'code': voucher_code
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_valid'] == True
        assert 'voucher' in data
        assert data['voucher']['code'] == voucher_code
    
    def test_check_voucher_invalid(self, client):
        """اختبار التحقق من كرت غير صحيح"""
        response = client.post('/api/vouchers/check', json={
            'code': 'INVALID123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_valid'] == False
        assert 'الكرت غير موجود' in data['validation_message']
    
    def test_redeem_voucher_success(self, client, sample_voucher_batch):
        """اختبار استخدام كرت بنجاح"""
        # الحصول على كود كرت من الدفعة
        with client.application.app_context():
            voucher = Voucher.query.filter_by(batch_id=sample_voucher_batch.id).first()
            voucher_code = voucher.code
        
        response = client.post('/api/vouchers/redeem', json={
            'code': voucher_code,
            'device_mac': '00:11:22:33:44:55',
            'device_ip': '192.168.1.100'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'session' in data
        assert 'voucher' in data
        assert data['voucher']['code'] == voucher_code
        
        # التحقق من أن الكرت تم تحديثه
        with client.application.app_context():
            updated_voucher = Voucher.query.filter_by(code=voucher_code).first()
            assert updated_voucher.is_used == True
            assert updated_voucher.usage_count == 1
    
    def test_redeem_voucher_already_used(self, client, sample_voucher_batch):
        """اختبار استخدام كرت مستخدم مسبقاً"""
        # استخدام الكرت أولاً
        with client.application.app_context():
            voucher = Voucher.query.filter_by(batch_id=sample_voucher_batch.id).first()
            voucher.is_used = True
            voucher.usage_count = voucher.max_usage_count
            db.session.commit()
            voucher_code = voucher.code
        
        response = client.post('/api/vouchers/redeem', json={
            'code': voucher_code,
            'device_mac': '00:11:22:33:44:55'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'الكرت مستخدم بالكامل' in data['message']
    
    def test_redeem_voucher_expired(self, client, sample_voucher_batch):
        """اختبار استخدام كرت منتهي الصلاحية"""
        from datetime import datetime, timedelta
        
        # تعيين تاريخ انتهاء في الماضي
        with client.application.app_context():
            voucher = Voucher.query.filter_by(batch_id=sample_voucher_batch.id).first()
            voucher.expires_at = datetime.utcnow() - timedelta(days=1)
            db.session.commit()
            voucher_code = voucher.code
        
        response = client.post('/api/vouchers/redeem', json={
            'code': voucher_code,
            'device_mac': '00:11:22:33:44:55'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'الكرت منتهي الصلاحية' in data['message']
    
    def test_activate_voucher_success(self, client, auth_headers_admin, sample_voucher_batch):
        """اختبار تفعيل كرت"""
        with client.application.app_context():
            voucher = Voucher.query.filter_by(batch_id=sample_voucher_batch.id).first()
            voucher.is_active = False
            db.session.commit()
            voucher_id = voucher.id
        
        response = client.post(f'/api/vouchers/vouchers/{voucher_id}/activate',
                             headers=auth_headers_admin)
        
        assert response.status_code == 200
        
        # التحقق من التفعيل
        with client.application.app_context():
            updated_voucher = Voucher.query.get(voucher_id)
            assert updated_voucher.is_active == True
    
    def test_deactivate_voucher_success(self, client, auth_headers_admin, sample_voucher_batch):
        """اختبار إلغاء تفعيل كرت"""
        with client.application.app_context():
            voucher = Voucher.query.filter_by(batch_id=sample_voucher_batch.id).first()
            voucher_id = voucher.id
        
        response = client.post(f'/api/vouchers/vouchers/{voucher_id}/deactivate',
                             headers=auth_headers_admin)
        
        assert response.status_code == 200
        
        # التحقق من إلغاء التفعيل
        with client.application.app_context():
            updated_voucher = Voucher.query.get(voucher_id)
            assert updated_voucher.is_active == False
    
    def test_reset_voucher_success(self, client, auth_headers_admin, sample_voucher_batch):
        """اختبار إعادة تعيين كرت"""
        # استخدام الكرت أولاً
        with client.application.app_context():
            voucher = Voucher.query.filter_by(batch_id=sample_voucher_batch.id).first()
            voucher.is_used = True
            voucher.usage_count = 1
            db.session.commit()
            voucher_id = voucher.id
        
        response = client.post(f'/api/vouchers/vouchers/{voucher_id}/reset',
                             headers=auth_headers_admin)
        
        assert response.status_code == 200
        
        # التحقق من إعادة التعيين
        with client.application.app_context():
            updated_voucher = Voucher.query.get(voucher_id)
            assert updated_voucher.is_used == False
            assert updated_voucher.usage_count == 0
    
    def test_get_sessions_success(self, client, auth_headers_operator):
        """اختبار الحصول على قائمة الجلسات"""
        response = client.get('/api/vouchers/sessions', headers=auth_headers_operator)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'sessions' in data
        assert 'pagination' in data
    
    def test_terminate_session_success(self, client, auth_headers_admin, sample_voucher_batch):
        """اختبار إنهاء جلسة"""
        # إنشاء جلسة أولاً
        with client.application.app_context():
            voucher = Voucher.query.filter_by(batch_id=sample_voucher_batch.id).first()
            session = UserSession(
                voucher_id=voucher.id,
                session_id='test-session-123',
                device_mac='00:11:22:33:44:55',
                device_ip='192.168.1.100',
                is_active=True
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id
        
        response = client.post(f'/api/vouchers/sessions/{session_id}/terminate',
                             headers=auth_headers_admin)
        
        assert response.status_code == 200
        
        # التحقق من إنهاء الجلسة
        with client.application.app_context():
            updated_session = UserSession.query.get(session_id)
            assert updated_session.is_active == False
            assert updated_session.ended_at is not None

