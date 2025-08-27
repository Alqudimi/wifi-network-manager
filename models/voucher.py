from database import db
from datetime import datetime, timedelta
import secrets
import string

class Voucher(db.Model):
    __tablename__ = 'vouchers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    batch_id = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, used, expired, disabled
    duration_hours = db.Column(db.Integer, default=24)
    data_limit_mb = db.Column(db.Integer, nullable=True)  # Data limit in MB
    speed_limit_kbps = db.Column(db.Integer, nullable=True)  # Speed limit in KB/s
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)
    session_token = db.Column(db.String(100), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Usage tracking
    data_used_mb = db.Column(db.Float, default=0.0)  # Data used in MB
    session_start = db.Column(db.DateTime, nullable=True)
    session_end = db.Column(db.DateTime, nullable=True)
    client_mac = db.Column(db.String(17), nullable=True)  # MAC address of client
    client_ip = db.Column(db.String(15), nullable=True)   # IP address of client
    
    # QR code data
    qr_code_data = db.Column(db.Text, nullable=True)
    
    # Voucher type and pricing
    voucher_type = db.Column(db.String(20), default='standard')  # standard, premium, unlimited
    price = db.Column(db.Float, default=0.0)  # Price in local currency
    
    # Network restrictions
    allowed_networks = db.Column(db.Text, nullable=True)  # JSON array of network IDs
    
    def __init__(self, **kwargs):
        super(Voucher, self).__init__(**kwargs)
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at and self.duration_hours:
            self.expires_at = datetime.utcnow() + timedelta(days=30)  # Default 30 days to use
    
    @staticmethod
    def generate_code(length=8):
        """Generate a random voucher code"""
        characters = string.ascii_uppercase + string.digits
        # Exclude similar looking characters
        characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def is_valid(self):
        """Check if voucher is valid for use"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def mark_as_used(self):
        """Mark voucher as used"""
        self.status = 'used'
        self.used_at = datetime.utcnow()
        self.session_token = secrets.token_urlsafe(32)
    
    def generate_qr_data(self, base_url='http://localhost:5000'):
        """Generate QR code data for voucher"""
        self.qr_code_data = f"{base_url}/captive?code={self.code}"
        return self.qr_code_data
    
    def to_dict(self):
        """Convert voucher to dictionary"""
        return {
            'id': self.id,
            'code': self.code,
            'batch_id': self.batch_id,
            'status': self.status,
            'duration_hours': self.duration_hours,
            'data_limit_mb': self.data_limit_mb,
            'speed_limit_kbps': self.speed_limit_kbps,
            'data_used_mb': self.data_used_mb,
            'voucher_type': self.voucher_type,
            'price': self.price,
            'client_mac': self.client_mac,
            'client_ip': self.client_ip,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'session_start': self.session_start.isoformat() if self.session_start else None,
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'qr_code_data': self.qr_code_data
        }
    
    def __repr__(self):
        return f'<Voucher {self.code}>'
