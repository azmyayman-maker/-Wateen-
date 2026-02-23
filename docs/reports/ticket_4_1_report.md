# تقرير التذكرة 4.1: أتمتة اختبارات الـ API — Ticket 4.1 Report

# Automating API Tests (Visit Lifecycle & Pricing Engine)

---

## البيانات الأساسية — Ticket Metadata

| الحقل             | القيمة                                                  |
| ----------------- | ------------------------------------------------------- |
| **رقم التذكرة**   | 4.1                                                     |
| **العنوان**       | Automating API Tests (Visit Lifecycle & Pricing Engine) |
| **الحالة**        | ✅ مكتمل — Completed                                    |
| **تاريخ الإغلاق** | 2026-02-22                                              |
| **المنفذ**        | Antigravity & TestSprite                                |
| **الفرع**         | `main`                                                  |
| **المرجع**        | MIP.md — Phase 4 (QA & Automation)                      |

---

## الملخص التنفيذي — Executive Summary

التذكرة 4.1 تركز على ضمان مسار العمل للمحركين الأساسيين في النظام الأساسي للعمود الفقري (Backend): **دورة حياة الزيارة (Visit Lifecycle)** و **محرك التسعير (Pricing Engine)**. تم الاعتماد على إطار عمل `pytest` وإدماج أداة الذكاء الاصطناعي **TestSprite** لتحليل الشفرة المرجعية وبناء خطة الاختبار تلقائياً.

تم التغلب على عقبات متعلقة ببيئة الجغرافيا المكانية (GeoDjango و GDAL) والصراعات أثناء توليد البيانات الوهمية (Mock Data) والوصول لكود يمتلك تغطية دقيقة داخل بيئة `Docker` المعزولة تماماً (حاوية `wateen_web`). جميع الاختبارات تعمل بنجاح واجتازت مرحلة التأكيد (Assertions).

### معايير القبول (Acceptance Criteria):

| المعيار                                    | الحالة                                 |
| ------------------------------------------ | -------------------------------------- |
| Test Environment: Initialized & Configured | ✅ دمج `factory_boy` و `pytest-django` |
| Test Config: Factories for Users & Visits  | ✅ `conftest.py` بإعداد بيانات مصرية   |
| Visit Lifecycle: Testing valid transitions | ✅ 100% نجاح النقل المتسلسل للحالة     |
| Visit Lifecycle: Testing invalid states    | ✅ 100% رفض النقل الخاطئ بواسطة DB     |
| Visit Lifecycle: Webhook Payment Checkout  | ✅ 100% نجاح الدفع الوهمي برابط API    |
| Pricing Engine: Daytime normal calculation | ✅ 100% حساب سليم مع مسافة ومعدلات     |
| Pricing Engine: Nighttime premium test     | ✅ 100% حساب سليم مع المضاعف الليلي    |
| Execution: Running tests inside Docker     | ✅ تعمل بكفاءة عبر `docker compose`    |

---

## سجل الملفات المُعدَّلة — File Manifest

### ملفات الاختبار (Test Suite)

| الملف                                  | الغرض                                                                         |
| -------------------------------------- | ----------------------------------------------------------------------------- |
| `visits/tests/conftest.py`             | الإعداد الجذري للاختبارات، يتضمن `CustomUserFactory`, `PatientProfileFactory` |
| `visits/tests/test_visit_lifecycle.py` | اختبارات نقل الحالات (Transitions) واختبار رابط الدفع Webhook                 |
| `visits/tests/test_pricing_engine.py`  | اختبارات نقطة الوصول `/api/v1/visits/estimate/` أوقات اليوم والليل            |

### ملفات التطبيق (Application Fixes)

| الملف                                  | الغرض                                                                            |
| -------------------------------------- | -------------------------------------------------------------------------------- |
| `visits/api.py`                        | تصحيح خطأ 500 واستخدام `dataclasses.asdict` بدلاً من `to_dict` للـ `PriceResult` |
| `visits/tests/test_pricing_engine.py`  | إصلاح الـ `IntegrityError` الناتج عن القيود الفريدة عن طريق `update_or_create`   |
| `visits/tests/test_visit_lifecycle.py` | إصلاح مسار نقطة وصول `MockPaymentWebhookView` وإضافة سابقة `/visits/`            |

---

## التفاصيل التقنية — Technical Details

### 1. إعداد هيكل الاختبار (Test Framework Setup)

تم استخدام أدوات الجيل القادم للبيانات الوهمية والترتيبات التجريبية:

- **`pytest-django`**: لضمان العمل بسلاسة مع إعدادات وإشارات (Signals) وإطارات دجانجو.
- **`factory_boy`**: لخلق تسلسلات (Factories) مرتبطة بقاعدة البيانات مثل المستخدم والمريض والممرض والزيارة. تم استخدام `django_get_or_create` ببراعة لتجنب تكرار وإضاعة البيانات بواسطة إشارات دجانجو المتشابكة `signals.py`.
- **`Faker`**: مع إعداد مكاني لمصر عبر `Point(31.2357, 30.0444, srid=4326)` للاختبارات المكانية، والتأكد من إمكانية تعامل GeoDjango دون الحاجة لمحاكاة كاملة (Mocking) بل الاعتماد على استعلامات قواعد بيانات حقيقية داخل الحاوية.

### 2. محرك دورة حياة الزيارة (Visit Lifecycle Tests)

تم تغطية ثلاثة اختبارات أساسية للتحقق من صرامة التنفيذ:

- **`test_visit_lifecycle_transitions`**: اختبار النقل التسلسلي الصحيح `PENDING` ➔ `MATCHED` ➔ `ACCEPTED` ➔ `ON_WAY` ➔ `ARRIVED` ➔ `IN_PROGRESS` ➔ `COMPLETED` والتأكد مما إذا كانت دالة `transition_to` تعتمد البيانات بشكل صحيح بدون كوارث في واجهات (Interfaces) قاعدة البيانات.
- **`test_invalid_lifecycle_transition`**: التأكد من اعتراض الموديل عبر `ValidationError` لأي محاولة نقل غير شرعية، مثلاً النقل مباشرة من `PENDING` إلى `COMPLETED`.
- **`test_payment_webhook_completes_visit`**: اختبار واجهة الرابط المحاكي (Mock Webhook API) عن طريق دفع حمولة بصيغة JSON باستخدام مصادقة توكن (`HTTP_X_MOCK_TOKEN`) ومتابعة تغير حالة الزيارة بناءً عليها.

### 3. محرك التسعير الديناميكي (Pricing Engine Tests)

تم التثبت من دقة النقطة المرجعية الخاصة بطلب التسعير `/api/v1/visits/estimate/`:

- إنشاء وتفعيل قواعد ومضاعفات التسعير `PricingFactor` داخل قاعدة بيانات الاختبار عبر الكود بديناميكية تامة.
- **الاختبار النهاري**: إرسال طلب في الساعة 14:00 ومطالبة الخادم بإرجاع التكلفة الأساسية + رسوم المسافة بدون مضاعفات إضافية (`day_multiplier: 1.00`).
- **الاختبار الليلي**: إرسال طلب في الساعة 03:00 صباحاً وإثبات رجوع التكلفة الإضافية مدمجة بالمضاعف الليلي (`night_multiplier: 1.50`). تمت معالجة عوائق الـ Serialization الناتجة من استخدام `dataclass`.

---

## القيود التشغيلية (Docker & Dependencies)

1. تم تنفيذ جميع الاختبارات باستخدام الأمر:
   `docker compose exec web pytest visits/tests/test_visit_lifecycle.py visits/tests/test_pricing_engine.py -v`
2. **عقبة مكتبات وتطبيقات الجغرافيا (GDAL / GEOS / PostGIS):** لا يمكن تشغيل الاختبارات التي تتعامل مع الكيانات الجغرافية المُسلسلة مع Windows محلياً بدون إعدادات معقدة للغاية في متغيرات البيئة.
   **الحل المعتمد:** التشغيل الدائم عبر واجهة و حاويات `docker` حيث أن الـ `Dockerfile` الخاص بالنظام يثبت ويُعالج تلقائياً إصدارات `libgdal-dev` و `gdal-bin` وبيئات C المتوافقة.

---

> **تم إغلاق التذكرة 4.1 بنجاح — 22 فبراير 2026**
