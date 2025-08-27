# WiFi Network Manager System

## Overview

This is a comprehensive WiFi network management system built with Flask that enables administrators to connect to and completely manage WPA/WPA2-Personal networks. The system provides full network control including creating time and data-limited vouchers for users, managing network access, and performing complete network operations. It features a web-based dashboard for managing WiFi vouchers, networks, routers, and users with Arabic RTL interface support.

The application is designed for network administrators who need complete control over their WiFi network infrastructure with advanced voucher management, real-time monitoring, and multi-router support including MikroTik, Ubiquiti, and Cisco devices.

## Recent Changes (August 26, 2025)

✓ Enhanced voucher model with advanced features (speed limits, data tracking, pricing)
✓ Added comprehensive network control panel for complete network management  
✓ Implemented real-time network monitoring and client tracking
✓ Created advanced voucher batch creation with multiple configuration options
✓ Added router management with connection testing and multi-brand support
✓ Integrated PostgreSQL database for production-ready data storage
✓ Developed Arabic RTL interface for better user experience

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with modular blueprint structure
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy for database operations
- **Authentication**: JWT-based authentication with role-based access control (admin, operator, user)
- **API Design**: RESTful API endpoints organized in separate blueprint modules
- **Security**: Password hashing using Werkzeug, CORS support, and CSRF protection

### Frontend Architecture
- **Templates**: Jinja2 templating engine with Arabic/RTL support
- **UI Framework**: Custom CSS with responsive design and dark/light theme support
- **JavaScript**: Vanilla ES6 JavaScript with class-based modular architecture
- **Icons**: Feather icons for consistent iconography
- **Real-time Updates**: AJAX-based dynamic content loading

### Database Design
- **Users**: Authentication and role management (admin, operator, user roles)
- **Vouchers**: WiFi access codes with expiration, usage tracking, and QR code generation
- **Networks**: WiFi network configurations with captive portal settings
- **Routers**: Multi-brand router management (MikroTik, Ubiquiti, Cisco)

### Router Integration
- **Multi-vendor Support**: Abstracted router management for different brands
- **API Protocols**: SSH for Cisco, API for MikroTik, HTTPS for Ubiquiti
- **Connection Management**: Health monitoring and automatic reconnection
- **Configuration Sync**: Automated voucher and network configuration deployment

### Authentication System
- **JWT Tokens**: 24-hour expiration with secure token generation
- **Role-based Access**: Hierarchical permissions (admin > operator > user)
- **Session Management**: Server-side session tracking with logout functionality
- **Captive Portal**: Guest authentication flow with voucher redemption

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and HTTP server
- **SQLAlchemy**: Database ORM and migration support
- **PyJWT**: JSON Web Token implementation for authentication
- **Werkzeug**: Password hashing and security utilities

### Database Options
- **SQLite**: Default development database (configurable)
- **PostgreSQL**: Production database support via DATABASE_URL
- **Redis**: Optional session storage and caching

### Router Management APIs
- **librouteros**: MikroTik RouterOS API client
- **paramiko**: SSH client for Cisco router management
- **requests**: HTTP client for Ubiquiti and web-based router APIs

### Utility Libraries
- **qrcode**: QR code generation for voucher distribution
- **Pillow**: Image processing for QR code creation
- **python-dateutil**: Date and time manipulation

### Frontend Libraries
- **Feather Icons**: SVG icon library
- **Google Fonts**: Inter font family for typography
- **Custom CSS**: Responsive grid system and component library

### Development Tools
- **Flask-Migrate**: Database schema migration management
- **Flask-CORS**: Cross-Origin Resource Sharing support

### Configuration Management
- **Environment Variables**: DATABASE_URL, JWT_SECRET_KEY, REDIS_URL
- **Config Classes**: Centralized configuration with environment-specific overrides