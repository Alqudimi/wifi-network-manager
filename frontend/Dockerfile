# استخدام Node.js كصورة أساسية
FROM node:20-alpine

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملفات package
COPY package*.json ./
COPY pnpm-lock.yaml ./

# تثبيت pnpm وتثبيت التبعيات
RUN npm install -g pnpm
RUN pnpm install

# نسخ كود التطبيق
COPY . .

# بناء التطبيق
RUN pnpm run build

# استخدام nginx لخدمة الملفات الثابتة
FROM nginx:alpine

# نسخ الملفات المبنية إلى nginx
COPY --from=0 /app/dist /usr/share/nginx/html

# نسخ إعدادات nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# تعيين المنفذ
EXPOSE 80

# تشغيل nginx
CMD ["nginx", "-g", "daemon off;"]

