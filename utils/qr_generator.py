import qrcode
from io import BytesIO
import base64
from PIL import Image

def generate_qr_code(data, size=10, border=4):
    """
    Generate QR code as base64 encoded image
    
    Args:
        data: The data to encode in QR code
        size: Size of each QR code box
        border: Size of border around QR code
    
    Returns:
        Base64 encoded PNG image
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        
        # Add data
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Encode to base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

def generate_voucher_qr(voucher_code, base_url='http://localhost:5000'):
    """
    Generate QR code for voucher redemption
    
    Args:
        voucher_code: The voucher code
        base_url: Base URL for the captive portal
    
    Returns:
        Base64 encoded QR code image
    """
    redemption_url = f"{base_url}/captive?code={voucher_code}"
    return generate_qr_code(redemption_url)

def generate_wifi_qr(ssid, password, security_type='WPA'):
    """
    Generate QR code for WiFi connection
    
    Args:
        ssid: WiFi network name
        password: WiFi password
        security_type: Security type (WPA, WEP, nopass)
    
    Returns:
        Base64 encoded QR code image
    """
    # WiFi QR code format: WIFI:T:WPA;S:mynetwork;P:mypass;H:false;;
    wifi_string = f"WIFI:T:{security_type};S:{ssid};P:{password};H:false;;"
    return generate_qr_code(wifi_string)
