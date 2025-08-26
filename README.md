# نظام إدارة شبكات Wi-Fi

نظام شامل لإدارة شبكات Wi-Fi ونظام الكروت (Vouchers) مع واجهة إدارية متقدمة ونظام مصادقة آمن.

## 🌟 المميزات الرئيسية

### إدارة الكروت (Vouchers)
- إنشاء دفعات كروت بأعداد كبيرة
- تخصيص مدة الاستخدام وحد البيانات لكل كرت
- طباعة الكروت بتصميم احترافي مع QR Code
- تصدير الكروت بصيغ PDF و CSV
- تتبع استخدام الكروت في الوقت الفعلي
- إعادة تعيين وإدارة الكروت المستخدمة

### إدارة المستخدمين والأدوار
- نظام أدوار متقدم (مدير، مشغل، مستخدم)
- مصادقة آمنة باستخدام JWT
- إدارة الملفات الشخصية والصلاحيات
- تتبع نشاط المستخدمين

### لوحة التحكم والتقارير
- إحصائيات شاملة في الوقت الفعلي
- تقارير الاستخدام اليومية والشهرية
- رسوم بيانية تفاعلية
- تتبع الجلسات النشطة

### إعدادات الشبكة
- إدارة إعدادات الراوترات المختلفة (MikroTik, Ubiquiti, Cisco)
- إعداد RADIUS Server
- إدارة Captive Portal
- تكوين DNS وإعدادات الشبكة

### الأمان والحماية
- تشفير كلمات المرور باستخدام bcrypt
- حماية من CSRF و XSS
- Rate Limiting لمنع الهجمات
- تسجيل العمليات والأنشطة

## 🏗️ البنية التقنية

### الواجهة الخلفية (Backend)
- **الإطار**: Flask (Python)
- **قاعدة البيانات**: PostgreSQL / SQLite
- **المصادقة**: JWT (JSON Web Tokens)
- **التخزين المؤقت**: Redis
- **API**: RESTful API مع توثيق Swagger

### الواجهة الأمامية (Frontend)
- **الإطار**: React.js
- **التصميم**: Tailwind CSS + shadcn/ui
- **الرسوم البيانية**: Recharts
- **التوجيه**: React Router
- **الحالة**: Context API + Custom Hooks

### النشر والتشغيل
- **الحاويات**: Docker + Docker Compose
- **الخادم**: Nginx (للواجهة الأمامية)
- **البيئة**: متوافق مع Linux/Windows/macOS

## 📋 متطلبات النظام

### الحد الأدنى
- **المعالج**: 2 CPU cores
- **الذاكرة**: 4GB RAM
- **التخزين**: 20GB مساحة فارغة
- **الشبكة**: اتصال إنترنت مستقر

### الموصى به
- **المعالج**: 4+ CPU cores
- **الذاكرة**: 8GB+ RAM
- **التخزين**: 50GB+ SSD
- **الشبكة**: اتصال إنترنت عالي السرعة

## 🚀 التثبيت والتشغيل

### التثبيت السريع باستخدام Docker

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd wifi-network-manager
```

2. **تشغيل النظام**
```bash
docker-compose up -d
```

3. **الوصول للنظام**
- الواجهة الأمامية: http://localhost
- API الخلفية: http://localhost:5000
- قاعدة البيانات: localhost:5432

### التثبيت اليدوي

#### الواجهة الخلفية
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

pip install -r requirements.txt
cp .env.example .env
# قم بتحرير ملف .env حسب بيئتك

python src/main.py
```

#### الواجهة الأمامية
```bash
cd frontend
npm install
# أو
pnpm install

cp .env.example .env
# قم بتحرير ملف .env حسب بيئتك

npm run dev
# أو
pnpm run dev
```

## 🔧 الإعداد والتكوين

### متغيرات البيئة

#### الواجهة الخلفية (.env)
```env
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/wifi_db
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=production
PORT=5000
```

#### الواجهة الأمامية (.env)
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### إعداد قاعدة البيانات

#### PostgreSQL (الإنتاج)
```sql
CREATE DATABASE wifi_network_db;
CREATE USER wifi_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE wifi_network_db TO wifi_user;
```

#### SQLite (التطوير)
سيتم إنشاء قاعدة البيانات تلقائياً في `backend/src/database/app.db`

## 👥 الحسابات الافتراضية

بعد التثبيت الأول، سيتم إنشاء حساب إداري افتراضي:

- **اسم المستخدم**: admin
- **كلمة المرور**: admin123
- **الدور**: مدير

⚠️ **مهم**: يرجى تغيير كلمة المرور فور تسجيل الدخول الأول.

## 🧪 تشغيل الاختبارات

### اختبارات الواجهة الخلفية
```bash
cd backend
python run_tests.py

# أو تشغيل اختبار محدد
python run_tests.py test_auth.py
```

### تغطية الاختبارات
```bash
cd backend
pytest --cov=src --cov-report=html
# ستجد التقرير في htmlcov/index.html
```

## 📚 استخدام النظام

### للمديرين
1. تسجيل الدخول بحساب المدير
2. إنشاء حسابات المشغلين
3. إعداد إعدادات الشبكة والراوترات
4. مراقبة الإحصائيات والتقارير

### للمشغلين
1. إنشاء دفعات الكروت
2. طباعة وتوزيع الكروت
3. مراقبة استخدام الكروت
4. إدارة الجلسات النشطة

### للمستخدمين النهائيين
1. زيارة صفحة استبدال الكروت: `/voucher`
2. إدخال كود الكرت
3. الاتصال بالإنترنت

## 🔗 ربط الراوترات

### MikroTik RouterOS
```bash
# تفعيل API
/ip service enable api

# إنشاء مستخدم API
/user add name=api-user password=api-password group=full

# إعداد Hotspot
/ip hotspot setup
```

### Ubiquiti UniFi
```bash
# الوصول لـ UniFi Controller
# إعداد Guest Portal
# ربط External Portal Server
```

### تفاصيل أكثر في ملف `docs/router-setup.md`

## 📖 التوثيق

- [دليل المستخدم](docs/user-guide.md)
- [دليل المطور](docs/developer-guide.md)
- [إعداد الراوترات](docs/router-setup.md)
- [API Documentation](docs/api-docs.md)
- [استكشاف الأخطاء](docs/troubleshooting.md)

## 🤝 المساهمة

نرحب بمساهماتكم! يرجى قراءة [دليل المساهمة](CONTRIBUTING.md) قبل البدء.

### خطوات المساهمة
1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 🆘 الدعم والمساعدة

### الحصول على المساعدة
- [Issues](https://github.com/your-repo/issues) - للإبلاغ عن الأخطاء
- [Discussions](https://github.com/your-repo/discussions) - للأسئلة والنقاشات
- البريد الإلكتروني: support@yourcompany.com

### الأخطاء الشائعة
راجع ملف [استكشاف الأخطاء](docs/troubleshooting.md) للحلول السريعة.

## 🔄 التحديثات

### الإصدار الحالي: v1.0.0

#### المميزات الجديدة
- نظام إدارة الكروت الكامل
- واجهة إدارية متقدمة
- دعم راوترات متعددة
- تقارير وإحصائيات شاملة

#### التحديثات القادمة
- دعم الدفع الإلكتروني
- تطبيق الهاتف المحمول
- تحليلات متقدمة
- دعم شبكات متعددة

## 🏢 معلومات الشركة

تم تطوير هذا النظام بواسطة فريق متخصص في حلول الشبكات والتكنولوجيا.

---

**© 2024 نظام إدارة شبكات Wi-Fi. جميع الحقوق محفوظة.**

