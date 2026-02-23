# تقرير إعداد النشر على VPS

## Wateen Project - Production Deployment Report

**تاريخ التقرير:** 2026-02-23  
**الحالة:** ✅ جاهز للنشر

---

## 📋 ملخص التغييرات

### الملفات المُنشأة حديثاً

| الملف                  | الوصف                       |
| ---------------------- | --------------------------- |
| `.env.production`      | إعدادات الإنتاج الآمنة      |
| `docker/init-db.sql`   | سكريبت تهيئة قاعدة البيانات |
| `docker/ssl/README.md` | دليل إعداد شهادات SSL       |
| `deploy.sh`            | سكريبت النشر التلقائي       |

### الملفات المُعدّلة

| الملف                       | التغييرات                                 |
| --------------------------- | ----------------------------------------- |
| `docker/docker-compose.yml` | كلمات مرور جديدة، volumes، backup service |
| `docker/nginx.conf`         | دعم SSL/HTTPS، security headers           |
| `config/settings.py`        | CORS ديناميكي من environment              |
| `.gitignore`                | حماية ملفات الإنتاج                       |

---

## 🔐 بيانات الاعتماد الجديدة (Credentials)

### ⚠️ هام: احفظ هذه البيانات في مكان آمن!

```
╔══════════════════════════════════════════════════════════════════╗
║                    PRODUCTION CREDENTIALS                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Django SECRET_KEY:                                                ║
║  wK9#mP2$vL5nQ8xR3yT6wZ1cB4fH7jK0mN3pS6vY9aD2gE5hI8jL1nO4qR7tU0x ║
║                                                                    ║
║  PostgreSQL:                                                       ║
║    Database: wateen_prod                                          ║
║    Username: wateen_admin                                         ║
║    Password: Wt$Pr0d!2026#S3cur3P@ssw0rd!Xk9#mN2                  ║
║                                                                    ║
║  Redis:                                                            ║
║    Password: R3d1s$Pr0d!2026#S3cur3K3y!Lp8#nM4                    ║
║                                                                    ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🚀 خطوات النشر

### 1. تحضير VPS

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# تثبيت Docker Compose
sudo apt install docker-compose-plugin

# استنساخ المشروع
git clone https://github.com/your-org/wateen.git
cd wateen
```

### 2. إعداد الشهادات SSL

```bash
# تشغيل سكريبت SSL
chmod +x deploy.sh
./deploy.sh ssl

# أو يدوياً:
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/*.pem docker/ssl/
```

### 3. تعديل الدومين

```bash
# تعديل ALLOWED_HOSTS في .env.production
nano .env.production

# غيّر:
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. تشغيل النشر

```bash
# تشغيل الخدمات
./deploy.sh start

# تشغيل migrations
./deploy.sh migrate

# التحقق من الحالة
./deploy.sh status
```

---

## 📊 بنية الخدمات

```
┌─────────────────────────────────────────────────────────────┐
│                        VPS Server                            │
│                                                              │
│  ┌─────────────┐                                            │
│  │   Nginx     │ :80 → redirect to HTTPS                   │
│  │   (SSL)     │ :443 → reverse proxy                      │
│  └──────┬──────┘                                            │
│         │                                                    │
│    ┌────┴────┐                                              │
│    │         │                                              │
│    ▼         ▼                                              │
│ ┌──────┐ ┌──────┐                                           │
│ │Frontend│ │Backend│                                         │
│ │Next.js │ │Django │                                         │
│ │ :3000 │ │ :8000 │                                         │
│ └──────┘ └───┬──┘                                           │
│              │                                               │
│         ┌────┴────┐                                         │
│         │         │                                         │
│         ▼         ▼                                         │
│    ┌───────┐ ┌───────┐                                      │
│    │ Redis │ │PostGIS│                                      │
│    │ :6379 │ │ :5432 │                                      │
│    └───────┘ └───────┘                                      │
│                                                              │
│  Volumes:                                                    │
│  • wateen_postgres_data (قاعدة البيانات)                    │
│  • wateen_redis_data (الكاش)                                │
│  • wateen_static_volume (الملفات الثابتة)                   │
│  • wateen_media_volume (ملفات المستخدمين)                   │
│  • wateen_backup_volume (النسخ الاحتياطية)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 الأمان

### Headers المُفعّلة

| Header                    | Value                                        |
| ------------------------- | -------------------------------------------- |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload |
| X-Frame-Options           | SAMEORIGIN                                   |
| X-Content-Type-Options    | nosniff                                      |
| X-XSS-Protection          | 1; mode=block                                |
| Referrer-Policy           | strict-origin-when-cross-origin              |
| Content-Security-Policy   | default-src 'self'                           |

### إعدادات Django للأمان

- ✅ `DEBUG = False`
- ✅ `SECURE_SSL_REDIRECT = True`
- ✅ `SESSION_COOKIE_SECURE = True`
- ✅ `CSRF_COOKIE_SECURE = True`
- ✅ `SECURE_HSTS_SECONDS = 31536000`

---

## 📝 أوامر مفيدة

```bash
# عرض السجلات
./deploy.sh logs

# إيقاف الخدمات
./deploy.sh stop

# إعادة التشغيل
./deploy.sh restart

# نسخ احتياطي
./deploy.sh backup

# حالة الخدمات
./deploy.sh status

# دخول لحاوية Django
docker exec -it wateen_web bash

# دخول لقاعدة البيانات
docker exec -it wateen_db psql -U wateen_admin -d wateen_prod

# عرض سجلات Nginx
docker logs wateen_nginx -f
```

---

## ⚠️ تحذيرات مهمة

1. **لا تشارك ملف `.env.production` أبداً**
2. **غيّر كلمات المرور قبل النشر الفعلي**
3. **فعّل جدار الحماية:**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```
4. **إعداد النسخ الاحتياطي التلقائي:**
   ```bash
   # أضف إلى crontab
   0 2 * * * /path/to/wateen/deploy.sh backup
   ```

---

## ✅ قائمة التحقق النهائية

- [x] إنشاء `.env.production` مع إعدادات آمنة
- [x] تحديث `docker-compose.yml` مع كلمات مرور جديدة
- [x] إضافة دعم SSL/HTTPS في `nginx.conf`
- [x] تحديث CORS في Django
- [x] إضافة volumes دائمة
- [x] إنشاء سكريبت النشر
- [x] حماية الملفات الحساسة في `.gitignore`
- [ ] الحصول على شهادة SSL
- [ ] تعديل الدومين في `.env.production`
- [ ] تشغيل النشر

---

**المشروع جاهز للنشر على VPS! 🚀**
