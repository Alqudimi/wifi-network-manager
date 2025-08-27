from database import db
from datetime import datetime

class Network(db.Model):
    __tablename__ = 'networks'
    
    id = db.Column(db.Integer, primary_key=True)
    ssid = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=True)
    security_type = db.Column(db.String(50), default='WPA2-Personal')  # WPA2-Personal, WPA3, Open
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, nullable=True)
    
    # Captive portal settings
    captive_portal_enabled = db.Column(db.Boolean, default=True)
    portal_title = db.Column(db.String(200), default='WiFi Access')
    portal_message = db.Column(db.Text, default='Please enter your voucher code to access the internet')
    
    # Bandwidth settings
    max_download_mbps = db.Column(db.Integer, nullable=True)
    max_upload_mbps = db.Column(db.Integer, nullable=True)
    
    # Associated router
    router_id = db.Column(db.Integer, db.ForeignKey('routers.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert network to dictionary"""
        return {
            'id': self.id,
            'ssid': self.ssid,
            'security_type': self.security_type,
            'is_active': self.is_active,
            'description': self.description,
            'captive_portal_enabled': self.captive_portal_enabled,
            'portal_title': self.portal_title,
            'portal_message': self.portal_message,
            'max_download_mbps': self.max_download_mbps,
            'max_upload_mbps': self.max_upload_mbps,
            'router_id': self.router_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Network {self.ssid}>'
