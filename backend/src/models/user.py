from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """نموذج المستخدمين والإداريين"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # معلومات شخصية
    full_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # أدوار ومستويات الوصول
    role = db.Column(db.String(20), default='user', nullable=False)  # admin, operator, user
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # معلومات إضافية
    branch_id = db.Column(db.Integer, nullable=True)  # للفروع المختلفة
    permissions = db.Column(db.Text, nullable=True)  # JSON string للصلاحيات المخصصة
    
    # تواريخ مهمة
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, username, email, password, full_name=None, phone=None, 
                 role='user', branch_id=None):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.phone = phone
        self.role = role
        self.branch_id = branch_id
        self.set_password(password)
    
    def set_password(self, password):
        """تشفير وحفظ كلمة المرور"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def update_last_login(self):
        """تحديث وقت آخر تسجيل دخول"""
        self.last_login_at = datetime.utcnow()
    
    def has_permission(self, permission):
        """التحقق من وجود صلاحية معينة"""
        if self.role == 'admin':
            return True
        
        if self.permissions:
            import json
            try:
                perms = json.loads(self.permissions)
                return permission in perms
            except:
                return False
        
        return False
    
    def is_admin(self):
        """التحقق من كون المستخدم مدير"""
        return self.role == 'admin'
    
    def is_operator(self):
        """التحقق من كون المستخدم مشغل"""
        return self.role in ['admin', 'operator']
    
    def to_dict(self, include_sensitive=False):
        """تحويل المستخدم إلى قاموس"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'branch_id': self.branch_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
        
        if include_sensitive:
            data['permissions'] = self.permissions
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'

