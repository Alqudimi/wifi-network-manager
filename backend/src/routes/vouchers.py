from flask import Blueprint, request, jsonify, send_file
from src.models.voucher import Voucher, VoucherBatch, UserSession, db
from src.utils.auth import token_required, operator_required, admin_required, rate_limit
from src.utils.voucher_generator import VoucherGenerator
from datetime import datetime, timedelta
import os
import tempfile

vouchers_bp = Blueprint('vouchers', __name__)
voucher_gen = VoucherGenerator()

@vouchers_bp.route('/batches', methods=['POST'])
@operator_required
def create_batch(current_user):
    """إنشاء دفعة جديدة من الكروت"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'total_vouchers', 'voucher_value']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'الحقل {field} مطلوب'}), 400
        
        name = data['name'].strip()
        total_vouchers = int(data['total_vouchers'])
        voucher_value = float(data['voucher_value'])
        
        # التحقق من صحة البيانات
        if total_vouchers <= 0 or total_vouchers > 10000:
            return jsonify({'message': 'عدد الكروت يجب أن يكون بين 1 و 10000'}), 400
        
        if voucher_value <= 0:
            return jsonify({'message': 'قيمة الكرت يجب أن تكون أكبر من صفر'}), 400
        
        # البيانات الاختيارية
        description = data.get('description', '').strip()
        voucher_duration_minutes = data.get('voucher_duration_minutes')
        voucher_data_limit_mb = data.get('voucher_data_limit_mb')
        voucher_max_usage_count = int(data.get('voucher_max_usage_count', 1))
        branch_id = data.get('branch_id')
        
        # تاريخ الانتهاء
        expires_at = None
        if data.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'تنسيق تاريخ الانتهاء غير صحيح'}), 400
        
        # إنشاء الدفعة
        batch, vouchers = voucher_gen.create_batch(
            name=name,
            total_vouchers=total_vouchers,
            voucher_value=voucher_value,
            created_by=current_user.id,
            description=description,
            voucher_duration_minutes=voucher_duration_minutes,
            voucher_data_limit_mb=voucher_data_limit_mb,
            voucher_max_usage_count=voucher_max_usage_count,
            expires_at=expires_at,
            branch_id=branch_id
        )
        
        return jsonify({
            'message': 'تم إنشاء الدفعة بنجاح',
            'batch': batch.to_dict(),
            'vouchers_count': len(vouchers)
        }), 201
    
    except ValueError as e:
        return jsonify({'message': 'بيانات غير صحيحة'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/batches', methods=['GET'])
@operator_required
def get_batches(current_user):
    """الحصول على قائمة الدفعات"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # فلترة حسب الفرع إذا لم يكن المستخدم مدير
        query = VoucherBatch.query
        if not current_user.is_admin() and current_user.branch_id:
            query = query.filter_by(branch_id=current_user.branch_id)
        
        # فلترة حسب التاريخ
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            query = query.filter(VoucherBatch.created_at >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            query = query.filter(VoucherBatch.created_at <= end_date)
        
        # البحث بالاسم
        if request.args.get('search'):
            search_term = f"%{request.args.get('search')}%"
            query = query.filter(VoucherBatch.name.like(search_term))
        
        # ترتيب النتائج
        query = query.order_by(VoucherBatch.created_at.desc())
        
        # تطبيق التصفح
        batches = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'batches': [batch.to_dict() for batch in batches.items],
            'pagination': {
                'page': page,
                'pages': batches.pages,
                'per_page': per_page,
                'total': batches.total,
                'has_next': batches.has_next,
                'has_prev': batches.has_prev
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/batches/<int:batch_id>', methods=['GET'])
@operator_required
def get_batch(current_user, batch_id):
    """الحصول على تفاصيل دفعة معينة"""
    try:
        batch = VoucherBatch.query.get_or_404(batch_id)
        
        # التحقق من الصلاحيات
        if not current_user.is_admin() and current_user.branch_id != batch.branch_id:
            return jsonify({'message': 'غير مسموح بالوصول لهذه الدفعة'}), 403
        
        return jsonify({
            'batch': batch.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/batches/<int:batch_id>/vouchers', methods=['GET'])
@operator_required
def get_batch_vouchers(current_user, batch_id):
    """الحصول على كروت دفعة معينة"""
    try:
        batch = VoucherBatch.query.get_or_404(batch_id)
        
        # التحقق من الصلاحيات
        if not current_user.is_admin() and current_user.branch_id != batch.branch_id:
            return jsonify({'message': 'غير مسموح بالوصول لهذه الدفعة'}), 403
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # فلترة الكروت
        query = Voucher.query.filter_by(batch_id=batch_id)
        
        # فلترة حسب الحالة
        if request.args.get('status'):
            status = request.args.get('status')
            if status == 'active':
                query = query.filter_by(is_active=True, is_used=False)
            elif status == 'used':
                query = query.filter_by(is_used=True)
            elif status == 'inactive':
                query = query.filter_by(is_active=False)
        
        # البحث بالكود
        if request.args.get('search'):
            search_term = f"%{request.args.get('search')}%"
            query = query.filter(Voucher.code.like(search_term))
        
        # ترتيب النتائج
        query = query.order_by(Voucher.created_at.desc())
        
        # تطبيق التصفح
        vouchers = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'vouchers': [voucher.to_dict() for voucher in vouchers.items],
            'pagination': {
                'page': page,
                'pages': vouchers.pages,
                'per_page': per_page,
                'total': vouchers.total,
                'has_next': vouchers.has_next,
                'has_prev': vouchers.has_prev
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/batches/<int:batch_id>/print', methods=['POST'])
@operator_required
def print_batch(current_user, batch_id):
    """طباعة بطاقات دفعة معينة"""
    try:
        batch = VoucherBatch.query.get_or_404(batch_id)
        
        # التحقق من الصلاحيات
        if not current_user.is_admin() and current_user.branch_id != batch.branch_id:
            return jsonify({'message': 'غير مسموح بالوصول لهذه الدفعة'}), 403
        
        vouchers = Voucher.query.filter_by(batch_id=batch_id).all()
        
        if not vouchers:
            return jsonify({'message': 'لا توجد كروت في هذه الدفعة'}), 404
        
        # إنشاء ملف PDF مؤقت
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # إنشاء البطاقات
        voucher_gen.create_voucher_card_pdf(
            vouchers=vouchers,
            output_path=pdf_path,
            company_name=request.json.get('company_name', 'شبكة Wi-Fi'),
            terms_text=request.json.get('terms_text')
        )
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'vouchers_batch_{batch_id}.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/batches/<int:batch_id>/export', methods=['POST'])
@operator_required
def export_batch(current_user, batch_id):
    """تصدير كروت دفعة معينة إلى CSV"""
    try:
        batch = VoucherBatch.query.get_or_404(batch_id)
        
        # التحقق من الصلاحيات
        if not current_user.is_admin() and current_user.branch_id != batch.branch_id:
            return jsonify({'message': 'غير مسموح بالوصول لهذه الدفعة'}), 403
        
        vouchers = Voucher.query.filter_by(batch_id=batch_id).all()
        
        if not vouchers:
            return jsonify({'message': 'لا توجد كروت في هذه الدفعة'}), 404
        
        # إنشاء ملف CSV مؤقت
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            csv_path = tmp_file.name
        
        # تصدير الكروت
        voucher_gen.export_vouchers_csv(vouchers, csv_path)
        
        return send_file(
            csv_path,
            as_attachment=True,
            download_name=f'vouchers_batch_{batch_id}.csv',
            mimetype='text/csv'
        )
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/redeem', methods=['POST'])
@rate_limit(max_requests=20, window_seconds=60)  # 20 محاولة كل دقيقة
def redeem_voucher():
    """استبدال/استخدام كرت"""
    try:
        data = request.get_json()
        
        if not data.get('code'):
            return jsonify({'message': 'كود الكرت مطلوب'}), 400
        
        code = data['code'].strip().upper()
        mac_address = data.get('mac_address')
        ip_address = data.get('ip_address')
        user_agent = request.headers.get('User-Agent')
        
        # البحث عن الكرت
        voucher = Voucher.query.filter_by(code=code).first()
        
        if not voucher:
            return jsonify({'message': 'الكرت غير موجود'}), 404
        
        # التحقق من صحة الكرت
        is_valid, message = voucher.is_valid()
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # استخدام الكرت
        success, result_message = voucher.use_voucher(mac_address, ip_address)
        
        if not success:
            return jsonify({'message': result_message}), 400
        
        # إنشاء جلسة جديدة
        session = UserSession(
            voucher_id=voucher.id,
            mac_address=mac_address,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'تم استخدام الكرت بنجاح',
            'voucher': voucher.to_dict(),
            'session': session.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/check', methods=['POST'])
@rate_limit(max_requests=50, window_seconds=60)  # 50 استعلام كل دقيقة
def check_voucher():
    """التحقق من حالة كرت"""
    try:
        data = request.get_json()
        
        if not data.get('code'):
            return jsonify({'message': 'كود الكرت مطلوب'}), 400
        
        code = data['code'].strip().upper()
        
        # البحث عن الكرت
        voucher = Voucher.query.filter_by(code=code).first()
        
        if not voucher:
            return jsonify({'message': 'الكرت غير موجود'}), 404
        
        # التحقق من صحة الكرت
        is_valid, message = voucher.is_valid()
        
        # الحصول على الجلسات النشطة
        active_sessions = UserSession.query.filter_by(
            voucher_id=voucher.id,
            is_active=True
        ).all()
        
        return jsonify({
            'voucher': voucher.to_dict(),
            'is_valid': is_valid,
            'validation_message': message,
            'active_sessions': [session.to_dict() for session in active_sessions]
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/vouchers/<int:voucher_id>/activate', methods=['POST'])
@operator_required
def activate_voucher(current_user, voucher_id):
    """تفعيل كرت"""
    try:
        voucher = Voucher.query.get_or_404(voucher_id)
        
        # التحقق من الصلاحيات
        if not current_user.is_admin() and current_user.branch_id != voucher.batch.branch_id:
            return jsonify({'message': 'غير مسموح بالوصول لهذا الكرت'}), 403
        
        voucher.is_active = True
        db.session.commit()
        
        return jsonify({
            'message': 'تم تفعيل الكرت بنجاح',
            'voucher': voucher.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/vouchers/<int:voucher_id>/deactivate', methods=['POST'])
@operator_required
def deactivate_voucher(current_user, voucher_id):
    """إلغاء تفعيل كرت"""
    try:
        voucher = Voucher.query.get_or_404(voucher_id)
        
        # التحقق من الصلاحيات
        if not current_user.is_admin() and current_user.branch_id != voucher.batch.branch_id:
            return jsonify({'message': 'غير مسموح بالوصول لهذا الكرت'}), 403
        
        voucher.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'تم إلغاء تفعيل الكرت بنجاح',
            'voucher': voucher.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/vouchers/<int:voucher_id>/reset', methods=['POST'])
@operator_required
def reset_voucher(current_user, voucher_id):
    """إعادة تعيين كرت"""
    try:
        voucher = Voucher.query.get_or_404(voucher_id)
        
        # التحقق من الصلاحيات
        if not current_user.is_admin() and current_user.branch_id != voucher.batch.branch_id:
            return jsonify({'message': 'غير مسموح بالوصول لهذا الكرت'}), 403
        
        # إعادة تعيين الكرت
        voucher.is_used = False
        voucher.usage_count = 0
        voucher.first_used_at = None
        voucher.last_used_at = None
        voucher.user_mac_address = None
        voucher.user_ip_address = None
        
        # إنهاء جميع الجلسات النشطة
        active_sessions = UserSession.query.filter_by(
            voucher_id=voucher.id,
            is_active=True
        ).all()
        
        for session in active_sessions:
            session.end_session()
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم إعادة تعيين الكرت بنجاح',
            'voucher': voucher.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/sessions', methods=['GET'])
@operator_required
def get_sessions(current_user):
    """الحصول على قائمة الجلسات"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # بناء الاستعلام
        query = UserSession.query
        
        # فلترة حسب الفرع إذا لم يكن المستخدم مدير
        if not current_user.is_admin() and current_user.branch_id:
            query = query.join(Voucher).join(VoucherBatch).filter(
                VoucherBatch.branch_id == current_user.branch_id
            )
        
        # فلترة حسب الحالة
        if request.args.get('active_only') == 'true':
            query = query.filter_by(is_active=True)
        
        # فلترة حسب التاريخ
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            query = query.filter(UserSession.started_at >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            query = query.filter(UserSession.started_at <= end_date)
        
        # ترتيب النتائج
        query = query.order_by(UserSession.started_at.desc())
        
        # تطبيق التصفح
        sessions = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions.items],
            'pagination': {
                'page': page,
                'pages': sessions.pages,
                'per_page': per_page,
                'total': sessions.total,
                'has_next': sessions.has_next,
                'has_prev': sessions.has_prev
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500


@vouchers_bp.route('/sessions/<int:session_id>/terminate', methods=['POST'])
@operator_required
def terminate_session(current_user, session_id):
    """إنهاء جلسة"""
    try:
        session = UserSession.query.get_or_404(session_id)
        
        # التحقق من الصلاحيات
        if not current_user.is_admin():
            voucher = session.voucher
            if current_user.branch_id != voucher.batch.branch_id:
                return jsonify({'message': 'غير مسموح بالوصول لهذه الجلسة'}), 403
        
        session.end_session()
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنهاء الجلسة بنجاح',
            'session': session.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'حدث خطأ في الخادم'}), 500

