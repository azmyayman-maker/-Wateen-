# تقرير التذكرة 3.3: واجهات المريض والممرض — Ticket 3.3 Report

# Patient & Nurse Dashboards (Core Medical UI)

---

## البيانات الأساسية — Ticket Metadata

| الحقل             | القيمة                                               |
| ----------------- | ---------------------------------------------------- |
| **رقم التذكرة**   | 3.3                                                  |
| **العنوان**       | Patient & Nurse Dashboards (Complete Implementation) |
| **الحالة**        | ✅ مكتمل — Completed                                 |
| **تاريخ البدء**   | 2026-02-20                                           |
| **تاريخ الإغلاق** | 2026-02-22                                           |
| **المنفذ**        | Antigravity                                          |
| **الفرع**         | `main`                                               |
| **المرجع**        | MIP.md — Phase 3 (Frontend Development)              |

---

## الملخص التنفيذي — Executive Summary

التذكرة 3.3 تُغلق متطلبات الواجهة الأساسية لكل من المريض والممرض ضمن منصة وتين الصحية. تم تنفيذ الكود بمعايير إنتاجية عالية باستخدام React/Next.js 14 مع التزام صارم بنظام التصميم UI/UX Pro Max ودعم كامل للعربية (RTL).

**واجهة المريض (The Calm Oasis)** تركز على خفض القلق الطبي عبر التصميم الزجاجي المتدرج (Glassmorphism)، الرسوم المتحركة الفيزيائية، والطباعة الواضحة. بينما **واجهة الممرض (The Tactical Pulse)** مصممة للبيئات عالية الضغط مع تباين حاد، مفتاح حالة تكتيكي، وقائمة طلبات واردة فورية.

### معايير القبول (Acceptance Criteria):

| المعيار                                   | الحالة                                |
| ----------------------------------------- | ------------------------------------- |
| Patient Screen: Service list displayed    | ✅ 6 خدمات مع أيقونات وأسعار          |
| Patient Screen: Current booking + History | ✅ حالة فارغة + 5 زيارات مختلفة       |
| Nurse Screen: Availability toggle         | ✅ مرتبط بمحاكاة API + `localStorage` |
| Nurse Screen: Incoming requests list      | ✅ 3 طلبات مع قبول/رفض                |
| Nurse: Toggle status reflected in Backend | ✅ محاكاة API مع إشعار Toast          |
| i18n: Arabic & English translations       | ✅ 23 مفتاح ترجمة جديد                |

---

## سجل الملفات المُعدَّلة — File Manifest

### ملفات الواجهات (Dashboard Components)

| الملف                                           | الغرض                                                                  | حجم التغيير |
| ----------------------------------------------- | ---------------------------------------------------------------------- | ----------- |
| `frontend/src/app/(dashboard)/patient/page.tsx` | واجهة المريض الرئيسية — شبكة الخدمات، سجل الزيارات، حالة الحجز الفارغة | تعديل جوهري |
| `frontend/src/app/(dashboard)/nurse/page.tsx`   | واجهة الممرض — قائمة الطلبات الواردة، ربط مفتاح الحالة بـ Mock API     | تعديل جوهري |

### ملفات الترجمة (i18n)

| الملف                            | الغرض                                   | عدد المفاتيح المضافة |
| -------------------------------- | --------------------------------------- | -------------------- |
| `frontend/src/lib/i18n/types.ts` | إضافة أنواع TypeScript للمفاتيح الجديدة | +23 مفتاح            |
| `frontend/src/lib/i18n/en.ts`    | الترجمة الإنجليزية                      | +23 قيمة             |
| `frontend/src/lib/i18n/ar.ts`    | الترجمة العربية                         | +23 قيمة             |

---

## التفاصيل التقنية — Technical Details

### 1. واجهة المريض — Patient Dashboard (`patient/page.tsx`)

#### أ. شبكة الخدمات المتاحة (Services Grid)

تم تنفيذ 6 بطاقات خدمة تفاعلية بتصميم زجاجي متدرج:

| الخدمة                      | الأيقونة         | السعر (EGP) | اللون            |
| --------------------------- | ---------------- | ----------- | ---------------- |
| حقن (Injection)             | `Syringe`        | 150         | Teal `#16615F`   |
| عناية جروح (Wound Care)     | `Scissors`       | 200         | Orange `#FD8839` |
| محاليل وريدية (IV Drip)     | `Stethoscope`    | 250         | Green `#79B253`  |
| قياسات حيوية (Vitals Check) | `Activity`       | 100         | Teal `#16615F`   |
| علاج طبيعي (Physiotherapy)  | `Dumbbell`       | 300         | Orange `#FD8839` |
| رعاية مسنين (Elderly Care)  | `HeartHandshake` | 350         | Red `#F32D17`    |

**المميزات التقنية:**

- تأثير `whileHover` مع `scale: 1.03` و `y: -3` عبر `framer-motion`
- توهج سفلي (Bottom Glow) عند المرور باللون المطابق لكل خدمة
- حدود شفافة `border-white/10` تتحول لـ `border-white/20` عند التفاعل
- خلفية متدرجة فريدة لكل بطاقة: `linear-gradient(160deg, rgba(color,0.12), rgba(11,17,32,0.85))`

#### ب. سجل الزيارات المتمايز (Differentiated Visit History)

5 زيارات تجريبية (Mock) بحالات مختلفة:

| الزيارة       | الممرض       | التاريخ     | السعر   | الحالة       | التقييم    |
| ------------- | ------------ | ----------- | ------- | ------------ | ---------- |
| Injection     | Sara Ahmed   | 18 Feb 2026 | 165 EGP | ✅ Completed | ⭐⭐⭐⭐⭐ |
| Wound Care    | Mona Ali     | 14 Feb 2026 | 220 EGP | ⭐ Rated     | ⭐⭐⭐⭐   |
| Vitals Check  | Amira Khaled | 10 Feb 2026 | 100 EGP | ✅ Completed | ⭐⭐⭐⭐⭐ |
| IV Drip       | Fatma Hassan | 5 Feb 2026  | 275 EGP | ❌ Cancelled | —          |
| Physiotherapy | Nour Ibrahim | 1 Feb 2026  | 310 EGP | ⭐ Rated     | ⭐⭐⭐⭐⭐ |

**شارات الحالة (Status Badges):**

- **مكتمل (Completed):** `CheckCircle2` — أخضر `#79B253`
- **ملغي (Cancelled):** `X` — أحمر `red-400`
- **تم التقييم (Rated):** `Star` — برتقالي `#FD8839`

#### ج. حالة الحجز الفارغة (Empty Booking State)

عندما لا يوجد حجز نشط (`hasActiveBooking === false`):

- حدود متقطعة `border-dashed border-slate-700`
- أيقونة `CalendarCheck` بلون رمادي
- عنوان ووصف توجيهي لإرشاد المريض

---

### 2. واجهة الممرض — Nurse Dashboard (`nurse/page.tsx`)

#### أ. قائمة الطلبات الواردة (Incoming Requests Queue)

3 طلبات تجريبية تظهر فقط عند تفعيل الحالة (`isOnline === true`):

| رقم الطلب | المريض        | الخدمة           | المسافة | السعر   | الوقت     |
| --------- | ------------- | ---------------- | ------- | ------- | --------- |
| REQ-7201  | Mahmoud Saeed | IV Drip & Vitals | 2.1 km  | 180 EGP | 2 min ago |
| REQ-7198  | Heba Mostafa  | Injection        | 3.4 km  | 160 EGP | 5 min ago |
| REQ-7195  | Karim Adel    | Elderly Care     | 1.8 km  | 350 EGP | 8 min ago |

**المميزات التقنية:**

- حركة دخول انسيابية: `initial={{ opacity: 0, x: isRTL ? -30 : 30 }}` (تدعم RTL)
- حركة خروج عند القبول/الرفض: `exit={{ opacity: 0, x: isRTL ? 30 : -30, height: 0 }}`
- `AnimatePresence` متداخل لحركة سلسة لكل بطاقة
- زر **قبول** (Accept): خلفية تيل `#16615F` مع ظل متوهج
- زر **رفض** (Decline): خلفية رمادية `slate-800`
- عداد طلبات في العنوان يتحدث تلقائياً
- **حالة فارغة** عند قبول/رفض جميع الطلبات

#### ب. مفتاح الحالة المتصل بالخادم (Mock API Toggle)

**الآلية الكاملة:**

```
1. النقر على Toggle → setIsToggling(true)
2. عرض Toast "جاري الاتصال..." + Spinner (Loader2)
3. محاكاة API: setTimeout(800ms)
4. تحديث الحالة: setIsOnline(nextState)
5. حفظ في localStorage: wateen_nurse_online = true/false
6. عرض Toast "متصل بنظام الإرسال" / "غير متصل بنظام الإرسال"
7. إخفاء Toast بعد 2.5 ثانية
```

**التخزين المحلي (Persistence):**

- المفتاح: `wateen_nurse_online`
- يُقرأ عند تحميل الصفحة (`useEffect`) لاستعادة الحالة السابقة
- يبقى بعد إغلاق المتصفح وإعادة فتحه

**الإشعارات (Toast Notifications):**

- تظهر في أعلى الصفحة (`fixed top-6 left-1/2`)
- تصميم زجاجي معتم `bg-slate-900/95 backdrop-blur-xl`
- حركة دخول/خروج عبر `AnimatePresence`

---

### 3. تحديثات الترجمة — i18n Updates

#### المفاتيح المضافة للمريض (Patient Keys):

| المفتاح               | الإنجليزية                  | العربية         |
| --------------------- | --------------------------- | --------------- |
| `servicesTitle`       | Available Services          | الخدمات المتاحة |
| `serviceInjection`    | Injection                   | حقن             |
| `serviceWoundCare`    | Wound Care                  | عناية جروح      |
| `serviceIVDrip`       | IV Drip                     | محاليل وريدية   |
| `serviceVitals`       | Vitals Check                | قياسات حيوية    |
| `servicePhysio`       | Physiotherapy               | علاج طبيعي      |
| `serviceElderly`      | Elderly Care                | رعاية مسنين     |
| `noActiveBooking`     | No Active Bookings          | لا يوجد حجز نشط |
| `noActiveBookingDesc` | When you request a nurse... | عند طلب ممرض... |
| `visitCompleted`      | Completed                   | مكتملة          |
| `visitCancelled`      | Cancelled                   | ملغية           |
| `visitRated`          | Rated                       | تم التقييم      |

#### المفاتيح المضافة للممرض (Nurse Keys):

| المفتاح              | الإنجليزية                     | العربية                  |
| -------------------- | ------------------------------ | ------------------------ |
| `incomingRequests`   | Incoming Requests              | الطلبات الواردة          |
| `noRequests`         | No Incoming Requests           | لا توجد طلبات واردة      |
| `noRequestsDesc`     | New requests will show here... | ستظهر الطلبات الجديدة... |
| `acceptRequest`      | Accept                         | قبول                     |
| `declineRequest`     | Decline                        | رفض                      |
| `connectingStatus`   | Connecting...                  | جاري الاتصال...          |
| `connectedStatus`    | Connected to dispatch          | متصل بنظام الإرسال       |
| `disconnectedStatus` | Disconnected from dispatch     | غير متصل بنظام الإرسال   |
| `awayDistance`       | away                           | بعيد                     |
| `estimatedPrice`     | Est.                           | تقديري                   |
| `timeAgo`            | ago                            | منذ                      |

---

## المكتبات والتبعيات — Dependencies Used

| المكتبة         | الإصدار | الاستخدام                                                                |
| --------------- | ------- | ------------------------------------------------------------------------ |
| `next`          | 14.2.3  | إطار React الأساسي                                                       |
| `react`         | 18.x    | مكتبة واجهة المستخدم                                                     |
| `framer-motion` | latest  | الرسوم المتحركة الفيزيائية (`AnimatePresence`, `whileHover`, `layout`)   |
| `lucide-react`  | latest  | الأيقونات (`Syringe`, `Scissors`, `Stethoscope`, `HeartHandshake`, etc.) |
| `tailwindcss`   | v4      | التنسيق (Utility-first CSS)                                              |

---

## قيود التصميم والامتثال — Design Constraints & Compliance

| القيد                      | الامتثال                                                                    |
| -------------------------- | --------------------------------------------------------------------------- |
| اتجاه RTL صارم             | ✅ `dir={isRTL ? 'rtl' : 'ltr'}` مع `{isRTL ? 'font-arabic' : 'font-sans'}` |
| ألوان العلامة التجارية فقط | ✅ Teal `#16615F` / Green `#79B253` / Red `#F32D17` / Orange `#FD8839`      |
| خلفية مظلمة (Dark Mode)    | ✅ `bg-slate-950 text-slate-50`                                             |
| بيانات تجريبية (Mock Data) | ✅ لا يوجد اتصال بخادم حقيقي                                                |
| حركات سلسة 60fps           | ✅ `framer-motion` مع `spring` physics                                      |
| دعم ثنائي اللغة            | ✅ 23 مفتاح ترجمة بالعربية والإنجليزية                                      |

---

## التحقق والاختبار — Verification Results

| الاختبار                                  | النتيجة                       |
| ----------------------------------------- | ----------------------------- |
| `npm run build` — TypeScript Compilation  | ✅ `Compiled successfully`    |
| `npm run build` — Linting & Type Validity | ✅ Pass                       |
| واجهة المريض — شبكة الخدمات تعمل          | ✅ 6 بطاقات مع أيقونات وأسعار |
| واجهة المريض — سجل الزيارات المتمايز      | ✅ 5 سجلات بحالات ملونة       |
| واجهة المريض — حالة فارغة للحجز           | ✅ تظهر دون حجز نشط           |
| واجهة الممرض — قائمة الطلبات              | ✅ 3 طلبات مع قبول/رفض        |
| واجهة الممرض — حفظ الحالة في localStorage | ✅ تبقى بعد إعادة التحميل     |
| واجهة الممرض — إشعار Toast                | ✅ يظهر عند تبديل الحالة      |
| واجهة الممرض — حالة فارغة للطلبات         | ✅ تظهر بعد قبول/رفض الكل     |
| اختبار متصفح (Patient)                    | ✅ تم التقاط لقطة شاشة        |
| اختبار متصفح (Nurse)                      | ✅ تم التقاط لقطة شاشة        |

---

## ملاحظات للمراحل القادمة — Notes for Future Phases

1. **ربط حقيقي بالخادم:** مفتاح الحالة جاهز للاستبدال بـ API call حقيقي (الهيكل موجود بالفعل في `handleToggle`)
2. **WebSocket للطلبات:** قائمة الطلبات الواردة مصممة لتقبل بيانات حية عبر WebSocket مستقبلاً
3. **نظام الحجز:** حالة `hasActiveBooking` جاهزة للربط بنظام حجز حقيقي
4. **دفع الإشعارات:** Toast notifications يمكن تطويرها لتصبح Push Notifications في Phase 5

---

> **تم إغلاق التذكرة 3.3 بنجاح — 22 فبراير 2026**
