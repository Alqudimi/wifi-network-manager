# الواجهة الخلفية (Backend)

هذا المجلد يحتوي على الكود الخاص بالواجهة الخلفية لمشروع إدارة شبكات Wi-Fi.

## التقنيات المستخدمة

- **اللغة**: Python
- **الإطار**: FastAPI
- **قاعدة البيانات**: PostgreSQL
- **التخزين المؤقت**: Redis
- **المصادقة**: JWT

## الإعداد والتشغيل

1.  **المتطلبات المسبقة**:
    - Python 3.9+
    - PostgreSQL
    - Redis
    - Docker و Docker Compose (موصى به للتطوير)

2.  **الاستنساخ والتثبيت**:
    ```bash
    git clone <رابط المستودع>
    cd wifi-network-manager/backend
    pip install -r requirements.txt
    ```

3.  **إعداد المتغيرات البيئية**:
    قم بإنشاء ملف `.env` في هذا المجلد بناءً على `.env.example` واملأ المتغيرات المطلوبة.

4.  **تشغيل قاعدة البيانات**:
    تأكد من أن خادم PostgreSQL يعمل وأن لديك قاعدة بيانات معدة للمشروع.

5.  **تشغيل الخادم**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

## API Documentation

يمكن الوصول إلى وثائق API التفاعلية (Swagger UI) على المسار `/docs` بعد تشغيل الخادم (على سبيل المثال: `http://localhost:8000/docs`).

## الاختبارات

لتشغيل اختبارات الوحدة:

```bash
pytest
```

## النشر (Deployment)

يتم توفير `Dockerfile` و `docker-compose.yml` لسهولة النشر.

## المساهمة

[إرشادات المساهمة هنا]

