import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
import os
from datetime import datetime
from src.models.voucher import Voucher, VoucherBatch, db

class VoucherGenerator:
    """مولد الكروت والبطاقات"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 20 * mm
        self.card_width = 85 * mm  # عرض البطاقة
        self.card_height = 54 * mm  # ارتفاع البطاقة (حجم بطاقة ائتمان)
        self.cards_per_row = 2
        self.cards_per_column = 5
        self.cards_per_page = self.cards_per_row * self.cards_per_column
    
    def create_batch(self, name, total_vouchers, voucher_value, created_by,
                    description=None, voucher_duration_minutes=None, 
                    voucher_data_limit_mb=None, voucher_max_usage_count=1,
                    expires_at=None, branch_id=None):
        """إنشاء دفعة جديدة من الكروت"""
        
        # إنشاء الدفعة
        batch = VoucherBatch(
            name=name,
            description=description,
            total_vouchers=total_vouchers,
            voucher_value=voucher_value,
            voucher_duration_minutes=voucher_duration_minutes,
            voucher_data_limit_mb=voucher_data_limit_mb,
            voucher_max_usage_count=voucher_max_usage_count,
            expires_at=expires_at,
            created_by=created_by,
            branch_id=branch_id
        )
        
        db.session.add(batch)
        db.session.flush()  # للحصول على ID الدفعة
        
        # إنشاء الكروت
        vouchers = []
        for i in range(total_vouchers):
            voucher = Voucher(
                batch_id=batch.id,
                value=voucher_value,
                duration_minutes=voucher_duration_minutes,
                data_limit_mb=voucher_data_limit_mb,
                max_usage_count=voucher_max_usage_count,
                expires_at=expires_at
            )
            vouchers.append(voucher)
            db.session.add(voucher)
        
        db.session.commit()
        
        return batch, vouchers
    
    def generate_qr_code(self, data, size=10):
        """توليد رمز QR"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    
    def create_voucher_card_pdf(self, vouchers, output_path, company_name="شبكة Wi-Fi",
                               company_logo=None, terms_text=None):
        """إنشاء ملف PDF للبطاقات"""
        
        # إنشاء مجلد الإخراج إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # حساب المواضع
        start_x = self.margin
        start_y = self.page_height - self.margin - self.card_height
        
        card_count = 0
        
        for voucher in vouchers:
            # حساب موضع البطاقة الحالية
            row = card_count // self.cards_per_row
            col = card_count % self.cards_per_row
            
            x = start_x + col * (self.card_width + 10 * mm)
            y = start_y - row * (self.card_height + 10 * mm)
            
            # رسم البطاقة
            self._draw_voucher_card(c, voucher, x, y, company_name, company_logo, terms_text)
            
            card_count += 1
            
            # إذا امتلأت الصفحة، ابدأ صفحة جديدة
            if card_count % self.cards_per_page == 0:
                c.showPage()
                card_count = 0
        
        c.save()
        return output_path
    
    def _draw_voucher_card(self, canvas, voucher, x, y, company_name, company_logo, terms_text):
        """رسم بطاقة واحدة"""
        
        # رسم حدود البطاقة
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1)
        canvas.rect(x, y, self.card_width, self.card_height)
        
        # خلفية البطاقة
        canvas.setFillColor(colors.lightblue)
        canvas.rect(x + 1, y + 1, self.card_width - 2, self.card_height - 2, fill=1, stroke=0)
        
        # إعادة تعيين اللون للنص
        canvas.setFillColor(colors.black)
        
        # عنوان الشركة
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawCentredText(x + self.card_width/2, y + self.card_height - 10*mm, company_name)
        
        # كود الكرت
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawCentredText(x + self.card_width/2, y + self.card_height - 20*mm, f"الكود: {voucher.code}")
        
        # القيمة والمدة
        canvas.setFont("Helvetica", 10)
        if voucher.duration_minutes:
            duration_text = f"المدة: {voucher.duration_minutes} دقيقة"
            canvas.drawCentredText(x + self.card_width/2, y + self.card_height - 28*mm, duration_text)
        
        if voucher.value:
            value_text = f"القيمة: {voucher.value}"
            canvas.drawCentredText(x + self.card_width/2, y + self.card_height - 35*mm, value_text)
        
        # رمز QR
        qr_data = f"WIFI:{voucher.code}:{voucher.value}:{voucher.duration_minutes}"
        qr_img = self.generate_qr_code(qr_data, size=3)
        
        # حفظ QR كصورة مؤقتة
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # رسم QR على البطاقة
        qr_size = 15 * mm
        qr_x = x + self.card_width - qr_size - 5*mm
        qr_y = y + 5*mm
        
        canvas.drawInlineImage(qr_buffer, qr_x, qr_y, qr_size, qr_size)
        
        # تاريخ الانتهاء
        if voucher.expires_at:
            expire_text = f"ينتهي: {voucher.expires_at.strftime('%Y-%m-%d')}"
            canvas.setFont("Helvetica", 8)
            canvas.drawString(x + 5*mm, y + 5*mm, expire_text)
        
        # رقم تسلسلي
        canvas.setFont("Helvetica", 6)
        canvas.drawString(x + 5*mm, y + 2*mm, f"#{voucher.id}")
    
    def export_vouchers_csv(self, vouchers, output_path):
        """تصدير الكروت إلى ملف CSV"""
        import csv
        
        # إنشاء مجلد الإخراج إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'code', 'batch_id', 'value', 'duration_minutes', 
                'data_limit_mb', 'max_usage_count', 'is_active', 'is_used',
                'created_at', 'expires_at'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for voucher in vouchers:
                writer.writerow({
                    'id': voucher.id,
                    'code': voucher.code,
                    'batch_id': voucher.batch_id,
                    'value': voucher.value,
                    'duration_minutes': voucher.duration_minutes,
                    'data_limit_mb': voucher.data_limit_mb,
                    'max_usage_count': voucher.max_usage_count,
                    'is_active': voucher.is_active,
                    'is_used': voucher.is_used,
                    'created_at': voucher.created_at.isoformat() if voucher.created_at else '',
                    'expires_at': voucher.expires_at.isoformat() if voucher.expires_at else ''
                })
        
        return output_path
    
    def create_batch_report_pdf(self, batch, output_path):
        """إنشاء تقرير PDF للدفعة"""
        
        # إنشاء مجلد الإخراج إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # عنوان التقرير
        title = Paragraph(f"تقرير الدفعة: {batch.name}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # معلومات الدفعة
        batch_info = [
            ['اسم الدفعة:', batch.name],
            ['الوصف:', batch.description or 'غير محدد'],
            ['إجمالي الكروت:', str(batch.total_vouchers)],
            ['قيمة الكرت:', str(batch.voucher_value)],
            ['مدة الكرت (دقيقة):', str(batch.voucher_duration_minutes) if batch.voucher_duration_minutes else 'غير محدد'],
            ['حد البيانات (MB):', str(batch.voucher_data_limit_mb) if batch.voucher_data_limit_mb else 'غير محدد'],
            ['تاريخ الإنشاء:', batch.created_at.strftime('%Y-%m-%d %H:%M')],
            ['تاريخ الانتهاء:', batch.expires_at.strftime('%Y-%m-%d') if batch.expires_at else 'غير محدد']
        ]
        
        batch_table = Table(batch_info, colWidths=[4*mm*10, 6*mm*10])
        batch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(batch_table)
        story.append(Spacer(1, 20))
        
        # إحصائيات الاستخدام
        stats = batch.get_usage_stats()
        stats_title = Paragraph("إحصائيات الاستخدام", styles['Heading2'])
        story.append(stats_title)
        
        stats_data = [
            ['إجمالي الكروت:', str(stats['total'])],
            ['الكروت المستخدمة:', str(stats['used'])],
            ['الكروت النشطة:', str(stats['active'])],
            ['الكروت غير النشطة:', str(stats['inactive'])],
            ['نسبة الاستخدام:', f"{stats['usage_percentage']:.1f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[4*mm*10, 6*mm*10])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        
        doc.build(story)
        return output_path
    
    def get_batch_by_id(self, batch_id):
        """الحصول على دفعة بواسطة المعرف"""
        return VoucherBatch.query.get(batch_id)
    
    def get_vouchers_by_batch(self, batch_id):
        """الحصول على كروت دفعة معينة"""
        return Voucher.query.filter_by(batch_id=batch_id).all()
    
    def activate_vouchers(self, voucher_ids):
        """تفعيل كروت محددة"""
        vouchers = Voucher.query.filter(Voucher.id.in_(voucher_ids)).all()
        for voucher in vouchers:
            voucher.is_active = True
        db.session.commit()
        return len(vouchers)
    
    def deactivate_vouchers(self, voucher_ids):
        """إلغاء تفعيل كروت محددة"""
        vouchers = Voucher.query.filter(Voucher.id.in_(voucher_ids)).all()
        for voucher in vouchers:
            voucher.is_active = False
        db.session.commit()
        return len(vouchers)
    
    def reset_vouchers(self, voucher_ids):
        """إعادة تعيين كروت محددة"""
        vouchers = Voucher.query.filter(Voucher.id.in_(voucher_ids)).all()
        for voucher in vouchers:
            voucher.is_used = False
            voucher.usage_count = 0
            voucher.first_used_at = None
            voucher.last_used_at = None
            voucher.user_mac_address = None
            voucher.user_ip_address = None
        db.session.commit()
        return len(vouchers)

