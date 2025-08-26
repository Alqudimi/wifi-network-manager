from flask import Blueprint, request, jsonify
from src.models.user import User, db
from src.models.voucher import VoucherBatch, Voucher, UserSession
from src.models.network import NetworkSettings, RouterConfiguration
from src.utils.auth import admin_required, operator_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    """الحصول على قائمة المستخدمين"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # بناء الاستعلام
        query = User.query
        
        # فلترة حسب الدور
        if request.args.get('role'):
            query = query.filter_by(role=request.args.get('role'))
        
        # فلترة حسب الحالة
        if request.args.get('is_active'):
            is_active = request.args.get('is_active').lower() == 'true'
            query = query.filter_by(is_active=is_active)
        
        # البحث
        if request.args.get('search'):
            search_term = f"%{request.args.get('search')}%"
            query = query.filter(
                (User.username.like(search_term)) |
                (User.email.like(search_term)) |
                (User.full_name.like(search_term))
            )
        
        # ترتيب النتائج
        query = query.order_by(User.created_at.desc())
        
        # تطبيق التصفح
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'pages': users.pages,
                'per_page': per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user(current_user):
    """إنشاء مستخدم جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'الحقل {field} مطلوب'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data['role']
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        branch_id = data.get('branch_id')
        
        # التحقق من صحة الدور
        valid_roles = ['admin', 'operator', 'user']
        if role not in valid_roles:
            return jsonify({'message': 'الدور غير صحيح'}), 400
        
        # التحقق من عدم وجود المستخدم مسبقاً
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'اسم المستخدم موجود مسبقاً'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'البريد الإلكتروني موجود مسبقاً'}), 409
        
        # إنشاء المستخدم الجديد
        user = User(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            role=role,
            branch_id=branch_id
        )
        
        # تفعيل المستخدم افتراضياً
        user.is_active = True
        user.is_verified = True
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء المستخدم بنجاح',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(current_user, user_id):
    """تحديث مستخدم"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # الحقول القابلة للتحديث
        updatable_fields = ['full_name', 'phone', 'role', 'is_active', 'is_verified', 'branch_id']
        
        for field in updatable_fields:
            if field in data:
                if field == 'role':
                    valid_roles = ['admin', 'operator', 'user']
                    if data[field] not in valid_roles:
                        return jsonify({'message': 'الدور غير صحيح'}), 400
                
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث المستخدم بنجاح',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    """حذف مستخدم"""
    try:
        if user_id == current_user.id:
            return jsonify({'message': 'لا يمكن حذف حسابك الخاص'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # تعطيل المستخدم بدلاً من حذفه (للحفاظ على البيانات المرتبطة)
        user.is_active = False
        user.username = f"deleted_{user.id}_{user.username}"
        user.email = f"deleted_{user.id}_{user.email}"
        
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المستخدم بنجاح'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/dashboard/stats', methods=['GET'])
@operator_required
def get_dashboard_stats(current_user):
    """الحصول على إحصائيات لوحة التحكم"""
    try:
        # فترة الإحصائيات (افتراضياً آخر 30 يوم)
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # إحصائيات عامة
        total_users = User.query.filter_by(is_active=True).count()
        total_batches = VoucherBatch.query.count()
        total_vouchers = Voucher.query.count()
        active_vouchers = Voucher.query.filter_by(is_active=True, is_used=False).count()
        used_vouchers = Voucher.query.filter_by(is_used=True).count()
        
        # إحصائيات الجلسات
        total_sessions = UserSession.query.count()
        active_sessions = UserSession.query.filter_by(is_active=True).count()
        
        # إحصائيات الفترة المحددة
        recent_sessions = UserSession.query.filter(
            UserSession.started_at >= start_date
        ).count()
        
        recent_vouchers_used = Voucher.query.filter(
            and_(
                Voucher.first_used_at >= start_date,
                Voucher.is_used == True
            )
        ).count()
        
        # إحصائيات يومية للرسم البياني
        daily_stats = db.session.query(
            func.date(UserSession.started_at).label('date'),
            func.count(UserSession.id).label('sessions_count')
        ).filter(
            UserSession.started_at >= start_date
        ).group_by(
            func.date(UserSession.started_at)
        ).order_by('date').all()
        
        # إحصائيات الدفعات الأكثر استخداماً
        popular_batches = db.session.query(
            VoucherBatch.name,
            VoucherBatch.id,
            func.count(Voucher.id).label('total_vouchers'),
            func.sum(func.cast(Voucher.is_used, db.Integer)).label('used_vouchers')
        ).join(Voucher).group_by(
            VoucherBatch.id, VoucherBatch.name
        ).order_by(
            func.sum(func.cast(Voucher.is_used, db.Integer)).desc()
        ).limit(10).all()
        
        return jsonify({
            'general_stats': {
                'total_users': total_users,
                'total_batches': total_batches,
                'total_vouchers': total_vouchers,
                'active_vouchers': active_vouchers,
                'used_vouchers': used_vouchers,
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'voucher_usage_percentage': (used_vouchers / total_vouchers * 100) if total_vouchers > 0 else 0
            },
            'period_stats': {
                'days': days,
                'recent_sessions': recent_sessions,
                'recent_vouchers_used': recent_vouchers_used
            },
            'daily_stats': [
                {
                    'date': stat.date.isoformat(),
                    'sessions_count': stat.sessions_count
                } for stat in daily_stats
            ],
            'popular_batches': [
                {
                    'batch_name': batch.name,
                    'batch_id': batch.id,
                    'total_vouchers': batch.total_vouchers,
                    'used_vouchers': batch.used_vouchers,
                    'usage_percentage': (batch.used_vouchers / batch.total_vouchers * 100) if batch.total_vouchers > 0 else 0
                } for batch in popular_batches
            ]
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/network-settings', methods=['GET'])
@operator_required
def get_network_settings(current_user):
    """الحصول على إعدادات الشبكة"""
    try:
        settings = NetworkSettings.query.filter_by(is_active=True).all()
        
        return jsonify({
            'settings': [setting.to_dict() for setting in settings]
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/network-settings', methods=['POST'])
@admin_required
def create_network_settings(current_user):
    """إنشاء إعدادات شبكة جديدة"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('name'):
            return jsonify({'message': 'اسم الإعدادات مطلوب'}), 400
        
        # إنشاء الإعدادات الجديدة
        settings = NetworkSettings(
            name=data['name'],
            created_by=current_user.id,
            **{k: v for k, v in data.items() if k != 'name' and hasattr(NetworkSettings, k)}
        )
        
        db.session.add(settings)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء إعدادات الشبكة بنجاح',
            'settings': settings.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/network-settings/<int:settings_id>', methods=['PUT'])
@admin_required
def update_network_settings(current_user, settings_id):
    """تحديث إعدادات الشبكة"""
    try:
        settings = NetworkSettings.query.get_or_404(settings_id)
        data = request.get_json()
        
        # الحقول القابلة للتحديث
        updatable_fields = [
            'name', 'description', 'radius_server_ip', 'radius_server_port',
            'radius_secret', 'radius_nas_ip', 'radius_nas_port',
            'captive_portal_url', 'redirect_url', 'success_url',
            'network_name', 'network_ip_range', 'gateway_ip',
            'dns_primary', 'dns_secondary', 'session_timeout',
            'idle_timeout', 'max_concurrent_sessions', 'is_active', 'is_default'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(settings, field, data[field])
        
        # إذا تم تعيين هذه الإعدادات كافتراضية، إلغاء الافتراضية من الأخرى
        if data.get('is_default'):
            NetworkSettings.query.filter(
                NetworkSettings.id != settings_id
            ).update({'is_default': False})
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث إعدادات الشبكة بنجاح',
            'settings': settings.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/routers', methods=['GET'])
@operator_required
def get_routers(current_user):
    """الحصول على قائمة الراوترات"""
    try:
        routers = RouterConfiguration.query.filter_by(is_active=True).all()
        
        return jsonify({
            'routers': [router.to_dict() for router in routers]
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/routers', methods=['POST'])
@admin_required
def create_router(current_user):
    """إضافة راوتر جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'router_type', 'ip_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'الحقل {field} مطلوب'}), 400
        
        # التحقق من نوع الراوتر
        valid_types = ['mikrotik', 'ubiquiti', 'cisco', 'openwrt']
        if data['router_type'] not in valid_types:
            return jsonify({'message': 'نوع الراوتر غير صحيح'}), 400
        
        # إنشاء الراوتر الجديد
        router = RouterConfiguration(
            name=data['name'],
            router_type=data['router_type'],
            ip_address=data['ip_address'],
            created_by=current_user.id,
            **{k: v for k, v in data.items() if k not in ['name', 'router_type', 'ip_address'] and hasattr(RouterConfiguration, k)}
        )
        
        db.session.add(router)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة الراوتر بنجاح',
            'router': router.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/routers/<int:router_id>/test', methods=['POST'])
@admin_required
def test_router_connection(current_user, router_id):
    """اختبار الاتصال بالراوتر"""
    try:
        router = RouterConfiguration.query.get_or_404(router_id)
        
        # اختبار الاتصال
        success = router.test_connection()
        
        db.session.commit()
        
        return jsonify({
            'success': success,
            'message': 'تم اختبار الاتصال بنجاح' if success else 'فشل في الاتصال',
            'last_test': router.last_connection_test.isoformat() if router.last_connection_test else None
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/routers/<int:router_id>/configuration', methods=['GET'])
@admin_required
def get_router_configuration(current_user, router_id):
    """الحصول على أوامر إعداد الراوتر"""
    try:
        router = RouterConfiguration.query.get_or_404(router_id)
        
        commands = router.get_configuration_commands()
        
        return jsonify({
            'router': router.to_dict(include_sensitive=True),
            'configuration_commands': commands
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@admin_bp.route('/reports/usage', methods=['GET'])
@operator_required
def get_usage_report(current_user):
    """تقرير الاستخدام"""
    try:
        # فترة التقرير
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # إحصائيات الاستخدام حسب اليوم
        daily_usage = db.session.query(
            func.date(UserSession.started_at).label('date'),
            func.count(UserSession.id).label('sessions'),
            func.sum(UserSession.data_uploaded_mb + UserSession.data_downloaded_mb).label('total_data_mb'),
            func.avg(
                func.extract('epoch', UserSession.ended_at - UserSession.started_at) / 60
            ).label('avg_duration_minutes')
        ).filter(
            UserSession.started_at >= start_date
        ).group_by(
            func.date(UserSession.started_at)
        ).order_by('date').all()
        
        # أكثر الأوقات استخداماً
        hourly_usage = db.session.query(
            func.extract('hour', UserSession.started_at).label('hour'),
            func.count(UserSession.id).label('sessions')
        ).filter(
            UserSession.started_at >= start_date
        ).group_by(
            func.extract('hour', UserSession.started_at)
        ).order_by('hour').all()
        
        return jsonify({
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat()
            },
            'daily_usage': [
                {
                    'date': usage.date.isoformat(),
                    'sessions': usage.sessions,
                    'total_data_mb': float(usage.total_data_mb or 0),
                    'avg_duration_minutes': float(usage.avg_duration_minutes or 0)
                } for usage in daily_usage
            ],
            'hourly_usage': [
                {
                    'hour': int(usage.hour),
                    'sessions': usage.sessions
                } for usage in hourly_usage
            ]
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500

