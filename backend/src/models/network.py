from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class NetworkSettings(db.Model):
    """إعدادات الشبكة والـ RADIUS"""
    __tablename__ = 'network_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # إعدادات RADIUS
    radius_server_ip = db.Column(db.String(15), nullable=True)
    radius_server_port = db.Column(db.Integer, default=1812, nullable=True)
    radius_secret = db.Column(db.String(100), nullable=True)
    radius_nas_ip = db.Column(db.String(15), nullable=True)
    radius_nas_port = db.Column(db.Integer, nullable=True)
    
    # إعدادات Captive Portal
    captive_portal_url = db.Column(db.String(255), nullable=True)
    redirect_url = db.Column(db.String(255), nullable=True)
    success_url = db.Column(db.String(255), nullable=True)
    
    # إعدادات الشبكة
    network_name = db.Column(db.String(100), nullable=True)  # اسم الشبكة
    network_ip_range = db.Column(db.String(20), nullable=True)  # نطاق IP
    gateway_ip = db.Column(db.String(15), nullable=True)
    dns_primary = db.Column(db.String(15), nullable=True)
    dns_secondary = db.Column(db.String(15), nullable=True)
    
    # إعدادات الأمان
    session_timeout = db.Column(db.Integer, default=3600, nullable=False)  # بالثواني
    idle_timeout = db.Column(db.Integer, default=1800, nullable=False)  # بالثواني
    max_concurrent_sessions = db.Column(db.Integer, default=1, nullable=False)
    
    # حالة الإعدادات
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    
    # تواريخ مهمة
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # العلاقات
    creator = db.relationship('User', backref='network_settings')
    
    def __init__(self, name, created_by, description=None, **kwargs):
        self.name = name
        self.description = description
        self.created_by = created_by
        
        # تعيين الإعدادات الأخرى
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """تحويل الإعدادات إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'radius_server_ip': self.radius_server_ip,
            'radius_server_port': self.radius_server_port,
            'radius_secret': self.radius_secret,
            'radius_nas_ip': self.radius_nas_ip,
            'radius_nas_port': self.radius_nas_port,
            'captive_portal_url': self.captive_portal_url,
            'redirect_url': self.redirect_url,
            'success_url': self.success_url,
            'network_name': self.network_name,
            'network_ip_range': self.network_ip_range,
            'gateway_ip': self.gateway_ip,
            'dns_primary': self.dns_primary,
            'dns_secondary': self.dns_secondary,
            'session_timeout': self.session_timeout,
            'idle_timeout': self.idle_timeout,
            'max_concurrent_sessions': self.max_concurrent_sessions,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class RouterConfiguration(db.Model):
    """إعدادات الراوترات المختلفة"""
    __tablename__ = 'router_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    router_type = db.Column(db.String(50), nullable=False)  # mikrotik, ubiquiti, cisco, openwrt
    model = db.Column(db.String(100), nullable=True)
    
    # معلومات الاتصال
    ip_address = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(100), nullable=True)  # مشفرة
    ssh_port = db.Column(db.Integer, default=22, nullable=False)
    
    # إعدادات الشبكة المرتبطة
    network_settings_id = db.Column(db.Integer, db.ForeignKey('network_settings.id'), nullable=True)
    
    # ملفات الإعداد
    configuration_template = db.Column(db.Text, nullable=True)  # قالب الإعداد
    current_configuration = db.Column(db.Text, nullable=True)  # الإعداد الحالي
    
    # حالة الراوتر
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_connected = db.Column(db.Boolean, default=False, nullable=False)
    last_connection_test = db.Column(db.DateTime, nullable=True)
    
    # تواريخ مهمة
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # العلاقات
    network_settings = db.relationship('NetworkSettings', backref='routers')
    creator = db.relationship('User', backref='router_configurations')
    
    def __init__(self, name, router_type, ip_address, created_by, **kwargs):
        self.name = name
        self.router_type = router_type
        self.ip_address = ip_address
        self.created_by = created_by
        
        # تعيين الإعدادات الأخرى
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def test_connection(self):
        """اختبار الاتصال بالراوتر"""
        # هنا يمكن إضافة منطق اختبار الاتصال الفعلي
        # مثل ping أو SSH connection test
        self.last_connection_test = datetime.utcnow()
        # للتبسيط، نفترض أن الاتصال ناجح
        self.is_connected = True
        return True
    
    def get_configuration_commands(self):
        """الحصول على أوامر الإعداد حسب نوع الراوتر"""
        if not self.network_settings:
            return []
        
        commands = []
        
        if self.router_type == 'mikrotik':
            commands = self._get_mikrotik_commands()
        elif self.router_type == 'ubiquiti':
            commands = self._get_ubiquiti_commands()
        elif self.router_type == 'cisco':
            commands = self._get_cisco_commands()
        elif self.router_type == 'openwrt':
            commands = self._get_openwrt_commands()
        
        return commands
    
    def _get_mikrotik_commands(self):
        """أوامر إعداد MikroTik"""
        ns = self.network_settings
        return [
            f"/radius add service=login address={ns.radius_server_ip} secret={ns.radius_secret}",
            f"/radius add service=accounting address={ns.radius_server_ip} secret={ns.radius_secret}",
            f"/ip hotspot user profile set default shared-users=1 session-timeout={ns.session_timeout}",
            f"/ip hotspot profile set default login-by=http-chap,http-pap radius-accounting=yes",
            f"/ip hotspot set hotspot1 profile=default"
        ]
    
    def _get_ubiquiti_commands(self):
        """أوامر إعداد Ubiquiti"""
        ns = self.network_settings
        return [
            f"set service radius-server {ns.radius_server_ip} key {ns.radius_secret}",
            f"set service radius-server {ns.radius_server_ip} port {ns.radius_server_port}",
            f"set service captive-portal interface eth0",
            f"set service captive-portal radius-server {ns.radius_server_ip}"
        ]
    
    def _get_cisco_commands(self):
        """أوامر إعداد Cisco"""
        ns = self.network_settings
        return [
            "configure terminal",
            f"radius-server host {ns.radius_server_ip} key {ns.radius_secret}",
            f"radius-server host {ns.radius_server_ip} auth-port {ns.radius_server_port}",
            "aaa new-model",
            "aaa authentication login default group radius local",
            "exit"
        ]
    
    def _get_openwrt_commands(self):
        """أوامر إعداد OpenWrt"""
        ns = self.network_settings
        return [
            f"uci set freeradius.radius.server='{ns.radius_server_ip}'",
            f"uci set freeradius.radius.port='{ns.radius_server_port}'",
            f"uci set freeradius.radius.key='{ns.radius_secret}'",
            "uci commit freeradius",
            "/etc/init.d/freeradius restart"
        ]
    
    def to_dict(self, include_sensitive=False):
        """تحويل إعدادات الراوتر إلى قاموس"""
        data = {
            'id': self.id,
            'name': self.name,
            'router_type': self.router_type,
            'model': self.model,
            'ip_address': self.ip_address,
            'username': self.username,
            'ssh_port': self.ssh_port,
            'network_settings_id': self.network_settings_id,
            'is_active': self.is_active,
            'is_connected': self.is_connected,
            'last_connection_test': self.last_connection_test.isoformat() if self.last_connection_test else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'configuration_commands': self.get_configuration_commands()
        }
        
        if include_sensitive:
            data['password'] = self.password
            data['configuration_template'] = self.configuration_template
            data['current_configuration'] = self.current_configuration
        
        return data

