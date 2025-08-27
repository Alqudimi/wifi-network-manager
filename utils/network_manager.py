"""
Network Management Utilities
Handles advanced network operations, monitoring, and router integration
"""

import subprocess
import socket
import struct
import json
from datetime import datetime, timedelta
from models.router import Router
from models.voucher import Voucher
from utils.router_manager import get_router_manager
import threading
import time

class NetworkMonitor:
    """Monitor network usage and manage active connections"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.active_sessions = {}
    
    def start_monitoring(self):
        """Start network monitoring in background"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._update_session_data()
                self._check_session_expiry()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"Network monitor error: {e}")
                time.sleep(60)
    
    def _update_session_data(self):
        """Update data usage for active sessions"""
        from database import db
        
        # Get active vouchers
        active_vouchers = Voucher.query.filter_by(status='used').filter(
            Voucher.session_end > datetime.utcnow()
        ).all()
        
        for voucher in active_vouchers:
            if voucher.client_ip:
                try:
                    # Simulate data usage calculation (in real implementation, 
                    # this would interface with router APIs or network monitoring tools)
                    data_used = self._get_client_data_usage(voucher.client_ip)
                    if data_used > voucher.data_used_mb:
                        voucher.data_used_mb = data_used
                        
                        # Check if data limit exceeded
                        if voucher.data_limit_mb and data_used >= voucher.data_limit_mb:
                            self._disconnect_voucher(voucher)
                            voucher.status = 'expired'
                            voucher.session_end = datetime.utcnow()
                
                except Exception as e:
                    print(f"Error updating data for voucher {voucher.code}: {e}")
        
        db.session.commit()
    
    def _check_session_expiry(self):
        """Check for expired sessions and disconnect them"""
        from database import db
        
        expired_vouchers = Voucher.query.filter_by(status='used').filter(
            Voucher.session_end <= datetime.utcnow()
        ).all()
        
        for voucher in expired_vouchers:
            try:
                self._disconnect_voucher(voucher)
                voucher.status = 'expired'
                print(f"Disconnected expired voucher: {voucher.code}")
            except Exception as e:
                print(f"Error disconnecting voucher {voucher.code}: {e}")
        
        db.session.commit()
    
    def _get_client_data_usage(self, client_ip):
        """Get data usage for specific client IP (simplified simulation)"""
        # In a real implementation, this would query router/firewall logs
        # or use SNMP to get actual usage statistics
        import random
        base_usage = random.uniform(0.1, 5.0)  # Simulate 0.1-5 MB usage per check
        return base_usage
    
    def _disconnect_voucher(self, voucher):
        """Disconnect voucher from all routers"""
        routers = Router.query.filter_by(is_active=True).all()
        
        for router in routers:
            try:
                manager = get_router_manager(router)
                if manager.connect():
                    if router.brand == 'MikroTik':
                        manager.remove_hotspot_user(voucher.code)
                    # Add other router types as needed
                manager.disconnect()
            except Exception as e:
                print(f"Error disconnecting from router {router.name}: {e}")

class NetworkConfiguration:
    """Handle network configuration and router setup"""
    
    @staticmethod
    def scan_network_devices():
        """Scan network for potential router devices"""
        devices = []
        
        try:
            # Get local network range
            local_ip = NetworkConfiguration.get_local_ip()
            network = NetworkConfiguration.get_network_range(local_ip)
            
            # Simple ping sweep (in production, use proper network discovery)
            for i in range(1, 255):
                ip = f"{network}.{i}"
                if NetworkConfiguration.ping_host(ip):
                    device_info = NetworkConfiguration.identify_device(ip)
                    if device_info:
                        devices.append(device_info)
        
        except Exception as e:
            print(f"Network scan error: {e}")
        
        return devices
    
    @staticmethod
    def get_local_ip():
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "192.168.1.100"  # Fallback
    
    @staticmethod
    def get_network_range(ip):
        """Get network range from IP (assumes /24)"""
        return ".".join(ip.split(".")[:-1])
    
    @staticmethod
    def ping_host(ip):
        """Check if host is reachable"""
        try:
            # Use system ping command
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def identify_device(ip):
        """Try to identify device type and capabilities"""
        device_info = {
            'ip': ip,
            'hostname': None,
            'mac': None,
            'vendor': None,
            'possible_router': False,
            'open_ports': []
        }
        
        try:
            # Try to get hostname
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                device_info['hostname'] = hostname
            except:
                pass
            
            # Check common router ports
            router_ports = [80, 443, 22, 23, 8728, 8080, 8443]
            for port in router_ports:
                if NetworkConfiguration.check_port(ip, port):
                    device_info['open_ports'].append(port)
            
            # Determine if likely a router
            if any(port in device_info['open_ports'] for port in [8728, 8443, 80]):
                device_info['possible_router'] = True
            
            # Try to identify vendor from hostname or other clues
            if device_info['hostname']:
                hostname_lower = device_info['hostname'].lower()
                if 'mikrotik' in hostname_lower or 'routerboard' in hostname_lower:
                    device_info['vendor'] = 'MikroTik'
                elif 'ubiquiti' in hostname_lower or 'unifi' in hostname_lower:
                    device_info['vendor'] = 'Ubiquiti'
                elif 'cisco' in hostname_lower:
                    device_info['vendor'] = 'Cisco'
        
        except Exception as e:
            print(f"Device identification error for {ip}: {e}")
        
        return device_info if device_info['possible_router'] else None
    
    @staticmethod
    def check_port(ip, port):
        """Check if specific port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

class VoucherManager:
    """Advanced voucher management and generation"""
    
    @staticmethod
    def generate_bulk_vouchers(config):
        """Generate vouchers in bulk with advanced options"""
        from database import db
        
        vouchers = []
        batch_id = f"BATCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        for i in range(config['quantity']):
            voucher = Voucher()
            voucher.batch_id = batch_id
            voucher.duration_hours = config.get('duration_hours', 24)
            voucher.data_limit_mb = config.get('data_limit_mb')
            voucher.speed_limit_kbps = config.get('speed_limit_kbps')
            voucher.voucher_type = config.get('voucher_type', 'standard')
            voucher.price = config.get('price', 0)
            voucher.created_by = config.get('created_by')
            
            # Custom expiration
            if config.get('voucher_expires_days'):
                voucher.expires_at = datetime.utcnow() + timedelta(
                    days=config['voucher_expires_days']
                )
            
            # Network restrictions
            if config.get('allowed_networks'):
                voucher.allowed_networks = json.dumps(config['allowed_networks'])
            
            # Generate QR code
            base_url = config.get('base_url', 'http://localhost:5000')
            voucher.generate_qr_data(base_url)
            
            db.session.add(voucher)
            vouchers.append(voucher)
        
        db.session.commit()
        return vouchers, batch_id
    
    @staticmethod
    def export_vouchers(vouchers, format='csv'):
        """Export vouchers in various formats"""
        if format == 'csv':
            return VoucherManager._export_csv(vouchers)
        elif format == 'json':
            return VoucherManager._export_json(vouchers)
        elif format == 'pdf':
            return VoucherManager._export_pdf(vouchers)
        else:
            raise ValueError("Unsupported export format")
    
    @staticmethod
    def _export_csv(vouchers):
        """Export vouchers as CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'كود الكارت', 'نوع الكارت', 'مدة الاتصال (ساعات)', 
            'حد البيانات (MB)', 'حد السرعة (KB/s)', 'السعر', 
            'تاريخ الإنشاء', 'تاريخ الانتهاء'
        ])
        
        # Data
        for voucher in vouchers:
            writer.writerow([
                voucher.code,
                voucher.voucher_type,
                voucher.duration_hours,
                voucher.data_limit_mb or 'غير محدود',
                voucher.speed_limit_kbps or 'غير محدود',
                voucher.price,
                voucher.created_at.strftime('%Y-%m-%d %H:%M') if voucher.created_at else '',
                voucher.expires_at.strftime('%Y-%m-%d %H:%M') if voucher.expires_at else ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def _export_json(vouchers):
        """Export vouchers as JSON"""
        return json.dumps([voucher.to_dict() for voucher in vouchers], 
                         ensure_ascii=False, indent=2)
    
    @staticmethod
    def _export_pdf(vouchers):
        """Export vouchers as PDF (requires reportlab)"""
        # This would require reportlab library
        # For now, return a placeholder
        return "PDF export requires reportlab library"

# Global network monitor instance
network_monitor = NetworkMonitor()

def start_network_monitoring():
    """Start the network monitoring service"""
    network_monitor.start_monitoring()

def stop_network_monitoring():
    """Stop the network monitoring service"""
    network_monitor.stop_monitoring()