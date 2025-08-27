import socket
import paramiko
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

class RouterManager:
    """Base class for router management"""
    
    def __init__(self, router):
        self.router = router
        self.connection = None
    
    def connect(self):
        """Connect to router - to be implemented by subclasses"""
        raise NotImplementedError
    
    def disconnect(self):
        """Disconnect from router"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def test_connection(self):
        """Test connection to router"""
        try:
            # Simple ping test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.router.ip_address, self.router.get_api_port()))
            sock.close()
            return result == 0
        except Exception:
            return False

class MikroTikManager(RouterManager):
    """MikroTik RouterOS management"""
    
    def connect(self):
        """Connect to MikroTik router via API"""
        try:
            import librouteros
            self.connection = librouteros.connect(
                host=self.router.ip_address,
                username=self.router.username,
                password=self.router.password,
                port=self.router.get_api_port()
            )
            return True
        except Exception as e:
            print(f"MikroTik connection error: {e}")
            return False
    
    def add_hotspot_user(self, username, password, profile='default'):
        """Add hotspot user"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            # Add user to hotspot
            self.connection.path('/ip/hotspot/user').add(
                name=username,
                password=password,
                profile=profile
            )
            return True
        except Exception as e:
            print(f"Error adding hotspot user: {e}")
            return False
    
    def remove_hotspot_user(self, username):
        """Remove hotspot user"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            # Find and remove user
            users = self.connection.path('/ip/hotspot/user').select('name', 'id')
            for user in users:
                if user['name'] == username:
                    self.connection.path('/ip/hotspot/user').remove(user['id'])
                    return True
            return False
        except Exception as e:
            print(f"Error removing hotspot user: {e}")
            return False

class UbiquitiManager(RouterManager):
    """Ubiquiti UniFi management"""
    
    def __init__(self, router):
        super().__init__(router)
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for local controllers
        self.base_url = f"https://{router.ip_address}:{router.get_api_port()}"
    
    def connect(self):
        """Connect to UniFi controller"""
        try:
            # Login to UniFi controller
            login_data = {
                'username': self.router.username,
                'password': self.router.password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"UniFi connection error: {e}")
            return False
    
    def add_guest_user(self, username, password, duration_minutes=1440):
        """Add guest user"""
        try:
            if not self.connect():
                return False
            
            # Get site info (usually 'default')
            sites_response = self.session.get(f"{self.base_url}/api/self/sites")
            if sites_response.status_code != 200:
                return False
            
            sites = sites_response.json()
            site_name = sites['data'][0]['name'] if sites['data'] else 'default'
            
            # Create guest user
            user_data = {
                'name': username,
                'password': password,
                'duration': duration_minutes,
                'quota': 0,  # Unlimited data
                'up': 0,     # Unlimited upload
                'down': 0    # Unlimited download
            }
            
            response = self.session.post(
                f"{self.base_url}/api/s/{site_name}/cmd/hotspot",
                json={'cmd': 'create-voucher', **user_data}
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error adding guest user: {e}")
            return False

class CiscoManager(RouterManager):
    """Cisco router management via SSH"""
    
    def connect(self):
        """Connect to Cisco router via SSH"""
        try:
            self.connection = paramiko.SSHClient()
            self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.connection.connect(
                hostname=self.router.ip_address,
                port=self.router.get_api_port(),
                username=self.router.username,
                password=self.router.password,
                timeout=10
            )
            return True
        except Exception as e:
            print(f"Cisco connection error: {e}")
            return False
    
    def execute_command(self, command):
        """Execute command on Cisco router"""
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            stdin, stdout, stderr = self.connection.exec_command(command)
            return stdout.read().decode('utf-8')
        except Exception as e:
            print(f"Error executing command: {e}")
            return None

def get_router_manager(router):
    """Factory function to get appropriate router manager"""
    managers = {
        'MikroTik': MikroTikManager,
        'Ubiquiti': UbiquitiManager,
        'Cisco': CiscoManager
    }
    
    manager_class = managers.get(router.brand)
    if not manager_class:
        raise ValueError(f"Unsupported router brand: {router.brand}")
    
    return manager_class(router)

def test_router_connection(router):
    """Test connection to router"""
    try:
        manager = get_router_manager(router)
        return manager.test_connection()
    except Exception as e:
        print(f"Error testing router connection: {e}")
        return False
