from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import string
import random

db = SQLAlchemy()

class Voucher(db.Model):
    """نموذج الكروت (Vouchers)"""
    __tablename__ = 'vouchers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('voucher_batches.id'), nullable=False)
    
    # معلومات الكرت
    value = db.Column(db.Float, nullable=False)  # القيمة المالية أو مدة الاستخدام
    duration_minutes = db.Column(db.Integer, nullable=True)  # مدة الاستخدام بالدقائق
    data_limit_mb = db.Column(db.Integer, nullable=True)  # حد البيانات بالميجابايت
    
    # حالة الكرت
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    max_usage_count = db.Column(db.Integer, default=1, nullable=False)  # عدد مرات الاستخدام المسموحة
    
    # تواريخ مهمة
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    first_used_at = db.Column(db.DateTime, nullable=True)
    last_used_at = db.Column(db.DateTime, nullable=True)
    
    # معلومات المستخدم
    user_mac_address = db.Column(db.String(17), nullable=True)  # MAC address للجهاز
    user_ip_address = db.Column(db.String(15), nullable=True)  # IP address للمستخدم
    
    # العلاقات
    batch = db.relationship('VoucherBatch', backref='vouchers')
    sessions = db.relationship('UserSession', backref='voucher', lazy='dynamic')
    
    def __init__(self, batch_id, value, duration_minutes=None, data_limit_mb=None, 
                 max_usage_count=1, expires_at=None):
        self.batch_id = batch_id
        self.value = value
        self.duration_minutes = duration_minutes
        self.data_limit_mb = data_limit_mb
        self.max_usage_count = max_usage_count
        self.expires_at = expires_at
        self.code = self.generate_code()
    
    def generate_code(self):
        """توليد كود فريد للكرت"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=12))
            # تأكد من عدم وجود الكود مسبقاً
            if not Voucher.query.filter_by(code=code).first():
                return code
    
    def is_valid(self):
        """التحقق من صحة الكرت"""
        if not self.is_active:
            return False, "الكرت غير مفعل"
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False, "انتهت صلاحية الكرت"
        
        if self.usage_count >= self.max_usage_count:
            return False, "تم استنفاد عدد مرات الاستخدام المسموحة"
        
        return True, "الكرت صالح للاستخدام"
    
    def use_voucher(self, mac_address=None, ip_address=None):
        """استخدام الكرت"""
        is_valid, message = self.is_valid()
        if not is_valid:
            return False, message
        
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        
        if self.usage_count == 1:
            self.first_used_at = datetime.utcnow()
        
        if mac_address:
            self.user_mac_address = mac_address
        if ip_address:
            self.user_ip_address = ip_address
        
        if self.usage_count >= self.max_usage_count:
            self.is_used = True
        
        return True, "تم استخدام الكرت بنجاح"
    
    def to_dict(self):
        """تحويل الكرت إلى قاموس"""
        return {
            'id': self.id,
            'code': self.code,
            'batch_id': self.batch_id,
            'value': self.value,
            'duration_minutes': self.duration_minutes,
            'data_limit_mb': self.data_limit_mb,
            'is_active': self.is_active,
            'is_used': self.is_used,
            'usage_count': self.usage_count,
            'max_usage_count': self.max_usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'first_used_at': self.first_used_at.isoformat() if self.first_used_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'user_mac_address': self.user_mac_address,
            'user_ip_address': self.user_ip_address
        }


class VoucherBatch(db.Model):
    """نموذج دفعات الكروت"""
    __tablename__ = 'voucher_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # معلومات الدفعة
    total_vouchers = db.Column(db.Integer, nullable=False)
    voucher_value = db.Column(db.Float, nullable=False)
    voucher_duration_minutes = db.Column(db.Integer, nullable=True)
    voucher_data_limit_mb = db.Column(db.Integer, nullable=True)
    voucher_max_usage_count = db.Column(db.Integer, default=1, nullable=False)
    
    # تواريخ مهمة
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # معلومات المنشئ
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    branch_id = db.Column(db.Integer, nullable=True)  # للفروع المختلفة
    
    # العلاقات
    creator = db.relationship('User', backref='created_batches')
    
    def __init__(self, name, total_vouchers, voucher_value, created_by,
                 description=None, voucher_duration_minutes=None, 
                 voucher_data_limit_mb=None, voucher_max_usage_count=1,
                 expires_at=None, branch_id=None):
        self.name = name
        self.description = description
        self.total_vouchers = total_vouchers
        self.voucher_value = voucher_value
        self.voucher_duration_minutes = voucher_duration_minutes
        self.voucher_data_limit_mb = voucher_data_limit_mb
        self.voucher_max_usage_count = voucher_max_usage_count
        self.expires_at = expires_at
        self.created_by = created_by
        self.branch_id = branch_id
    
    def get_usage_stats(self):
        """إحصائيات استخدام الدفعة"""
        total = len(self.vouchers)
        used = len([v for v in self.vouchers if v.is_used])
        active = len([v for v in self.vouchers if v.is_active and not v.is_used])
        inactive = len([v for v in self.vouchers if not v.is_active])
        
        return {
            'total': total,
            'used': used,
            'active': active,
            'inactive': inactive,
            'usage_percentage': (used / total * 100) if total > 0 else 0
        }
    
    def to_dict(self):
        """تحويل الدفعة إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'total_vouchers': self.total_vouchers,
            'voucher_value': self.voucher_value,
            'voucher_duration_minutes': self.voucher_duration_minutes,
            'voucher_data_limit_mb': self.voucher_data_limit_mb,
            'voucher_max_usage_count': self.voucher_max_usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_by': self.created_by,
            'branch_id': self.branch_id,
            'usage_stats': self.get_usage_stats()
        }


class UserSession(db.Model):
    """نموذج جلسات المستخدمين"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey('vouchers.id'), nullable=False)
    
    # معلومات الجلسة
    session_id = db.Column(db.String(50), unique=True, nullable=False)
    mac_address = db.Column(db.String(17), nullable=True)
    ip_address = db.Column(db.String(15), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    # إحصائيات الاستخدام
    data_uploaded_mb = db.Column(db.Float, default=0, nullable=False)
    data_downloaded_mb = db.Column(db.Float, default=0, nullable=False)
    
    # تواريخ الجلسة
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)
    last_activity_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # حالة الجلسة
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __init__(self, voucher_id, mac_address=None, ip_address=None, user_agent=None):
        self.voucher_id = voucher_id
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.session_id = str(uuid.uuid4())
    
    def get_duration_minutes(self):
        """حساب مدة الجلسة بالدقائق"""
        if self.ended_at:
            duration = self.ended_at - self.started_at
        else:
            duration = datetime.utcnow() - self.started_at
        return int(duration.total_seconds() / 60)
    
    def get_total_data_mb(self):
        """حساب إجمالي البيانات المستخدمة"""
        return self.data_uploaded_mb + self.data_downloaded_mb
    
    def end_session(self):
        """إنهاء الجلسة"""
        self.ended_at = datetime.utcnow()
        self.is_active = False
    
    def to_dict(self):
        """تحويل الجلسة إلى قاموس"""
        return {
            'id': self.id,
            'voucher_id': self.voucher_id,
            'session_id': self.session_id,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'data_uploaded_mb': self.data_uploaded_mb,
            'data_downloaded_mb': self.data_downloaded_mb,
            'total_data_mb': self.get_total_data_mb(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'duration_minutes': self.get_duration_minutes(),
            'is_active': self.is_active
        }

