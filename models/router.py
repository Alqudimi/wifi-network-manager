from database import db
from datetime import datetime

class Router(db.Model):
    __tablename__ = 'routers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50), nullable=False)  # MikroTik, Ubiquiti, Cisco
    model = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    api_port = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Connection status
    last_connected = db.Column(db.DateTime, nullable=True)
    connection_status = db.Column(db.String(20), default='disconnected')  # connected, disconnected, error
    
    # Router specific settings
    radius_server = db.Column(db.String(100), nullable=True)
    radius_secret = db.Column(db.String(100), nullable=True)
    
    # Networks relationship
    networks = db.relationship('Network', backref='router', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_api_port(self):
        """Get appropriate API port for router brand"""
        if self.api_port:
            return self.api_port
        
        port_mapping = {
            'MikroTik': 8728,
            'Ubiquiti': 443,
            'Cisco': 22
        }
        return port_mapping.get(self.brand, 22)
    
    def to_dict(self):
        """Convert router to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'ip_address': self.ip_address,
            'username': self.username,
            'api_port': self.get_api_port(),
            'is_active': self.is_active,
            'last_connected': self.last_connected.isoformat() if self.last_connected else None,
            'connection_status': self.connection_status,
            'radius_server': self.radius_server,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Router {self.name}>'
