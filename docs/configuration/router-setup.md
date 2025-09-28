# 📡 إعداد أجهزة التوجيه

## MikroTik RouterOS

### الإعداد الأولي
```bash
# الاتصال بالراوتر
ssh admin@192.168.1.1

# تفعيل API
/ip service enable api
/ip service set api port=8728

# إعداد Hotspot
/ip hotspot setup
# اختر interface: bridge
# اختر IP pool: 192.168.2.2-192.168.2.254
# اختر DNS: 8.8.8.8
```

### إعداد User Profiles
```bash
# إنشاء profile للكروت
/ip hotspot user profile add name="voucher-profile" \
  rate-limit="1M/1M" \
  session-timeout="24:00:00" \
  keepalive-timeout="2m"

# إعداد Walled Garden
/ip hotspot walled-garden add dst-host=your-domain.com
/ip hotspot walled-garden add dst-host="*.your-domain.com"
```

## Ubiquiti UniFi

### إعداد Guest Network
```javascript
// إعداد شبكة الضيوف
{
  "name": "Guest Network",
  "security": "wpapsk",
  "wpa_enc": "ccmp",
  "wpa_mode": "wpa2",
  "x_passphrase": "guestpassword123",
  "guest_access": true,
  "is_guest": true
}
```

### إعداد Hotspot Portal
```json
{
  "portal_enabled": true,
  "portal_customized": true,
  "redirect_enabled": true,
  "redirect_url": "https://your-domain.com/captive",
  "auth_mode": "none"
}
```

## Cisco Configuration

### إعداد Wireless
```bash
# إعداد SSID للضيوف
configure terminal
dot11 ssid GuestNetwork
  vlan 100
  authentication open
  guest-mode
  exit

# إعداد VLAN
interface dot11radio0.100
  encapsulation dot1Q 100
  ip address 192.168.100.1 255.255.255.0
  exit
```

### إعداد Web Authentication
```bash
# تفعيل AAA
aaa new-model
aaa authentication login default local
aaa authorization network default local

# إعداد Web Auth
ip http server
ip http authentication aaa
ip http secure-server
```