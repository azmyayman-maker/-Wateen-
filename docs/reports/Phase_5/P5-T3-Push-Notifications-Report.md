# تقرير هندسي: نظام الإشعارات الفورية (Push Notifications System)

**رقم التذكرة:** [P5-T3]
**التاريخ:** 2026-03-26
**الحالة:** ✅ مكتمل (Core Pipeline + API + Integration Hooks + Code Review)
**النطاق:** إشعارات FCM عبر Firebase، إدارة رموز الأجهزة، قوالب ثنائية اللغة، تفضيلات المستخدم، Celery غير متزامن، تنظيف دوري
**الفرع:** `027-push-notifications`

---

## 1. ملخص تنفيذي (Executive Summary)

تم تصميم وتنفيذ نظام **إشعارات فورية (Push Notifications)** متكامل لمنصة وتين B2B2C، مبني على **Firebase Cloud Messaging (FCM)** عبر مكتبة `firebase-admin` الرسمية. يغطي النظام دورة حياة الإشعارات بالكامل:

- **إرسال فوري** لإشعارات تغيير حالة الزيارة لجميع الأطراف المعنية (المريض، الممرض، مدير الوكالة) خلال **≤5 ثوانٍ** من الحدث.
- **واجهة Batch API** تُرسل حتى **500 رمز جهاز** في طلب HTTP واحد — مُحسَّنة لسيناريو التوزيع الجماعي (50+ ممرض في وكالة).
- **8 أنواع أحداث** مع قوالب ثنائية اللغة (عربي/إنجليزي) و**تفضيلات مستخدم** دقيقة لكل فئة.
- **سجل تدقيق غير قابل للتعديل** (`NotificationLog`) يُسجل كل محاولة إرسال مع الحالة والخطأ.
- **أمان مُشدَّد**: لا بيانات شخصية (PII) في حمولة الإشعار — فقط `visit_id` كمُعرِّف مُبهم.
- **تنظيف دوري** عبر Celery Beat لرموز الأجهزة المُنتهية (30 يوماً).

تمت مراعاة نموذج **B2B2C** بشكل صارم: الممرضون يتبعون وكالات، والإشعارات تمر عبر الطبقة المؤسسية.

---

## 2. حيثيات التذكرة (Ticket Context & Requirements)

### 2.1 المشكلة التي تحلها التذكرة

بعد إنشاء البنية التحتية للـ WebSocket (P5-T1) وبث الحالة اللحظي (P5-T2)، كان النظام يُبلغ المستخدمين فقط **أثناء اتصالهم بالتطبيق**. الحالات التي لا يُغطيها WebSocket:

- المريض أغلق التطبيق وينتظر إشعار تعيين الممرض.
- مدير الوكالة بعيد عن لوحة القيادة ويحتاج تنبيه بعرض زيارة جديد (نافذة 300 ثانية).
- الممرض في وضع Auto-Dispatch ويحتاج إشعار فوري لقبول العرض.
- التسوية المالية تمت والوكالة تحتاج تأكيد.

**قبل هذه التذكرة:** لا آلية لإيصال المعلومات للمستخدم خارج التطبيق النشط.
**بعد هذه التذكرة:** كل حدث حيوي يصل للمستخدم عبر إشعار فوري على مستوى نظام التشغيل.

### 2.2 قصص المستخدم (User Stories)

| رقم | القصة | الأولوية | الحالة |
|-----|-------|----------|--------|
| US1 | المريض يتلقى إشعارات تغيير حالة الزيارة | P1 🎯 MVP | ✅ مكتمل |
| US2 | مدير الوكالة يتلقى إشعارات التوزيع والتسويات المالية | P1 | ✅ مكتمل |
| US3 | الممرض يتلقى إشعارات العروض والتكليفات | P1 | ✅ مكتمل |
| US4 | إدارة رموز الأجهزة (تسجيل/إلغاء/قائمة) عبر REST API | P2 | ✅ مكتمل |
| US5 | تفضيلات إشعارات المستخدم (تفعيل/تعطيل لكل فئة) | P2 | ✅ مكتمل |
| US6 | محتوى ثنائي اللغة (عربي/إنجليزي) | P2 | ✅ مكتمل |
| US7 | سجل تدقيق غير قابل للتعديل | P3 | ✅ مكتمل |

### 2.3 المتطلبات الوظيفية الأساسية

| المتطلب | الوصف | الحالة |
|---------|-------|--------|
| FR-001 | تسجيل ≥1 رمز جهاز (FCM token) لكل مستخدم | ✅ |
| FR-002 | فرض تفرد الرمز — upsert عند التكرار | ✅ |
| FR-003 | إلغاء رمز الجهاز عند تسجيل الخروج | ✅ |
| FR-004 | تنظيف دوري للرموز المنتهية (30 يوم) | ✅ |
| FR-005 | إرسال غير متزامن عبر Celery | ✅ |
| FR-006 | استخدام FCM Batch API (500 رمز/طلب) | ✅ |
| FR-007 | دعم 8 أنواع أحداث | ✅ |
| FR-008 | قوالب ثنائية اللغة مع متغيرات ديناميكية | ✅ |
| FR-009 | تفضيلات إشعارات لكل فئة | ✅ |
| FR-010 | فحص التفضيلات قبل الإرسال | ✅ |
| FR-011 | سجل تدقيق غير قابل للتعديل | ✅ |
| FR-012 | إعادة محاولة أسّية (3 محاولات) | ✅ |
| FR-013 | عدم تضمين PII في الحمولة | ✅ |
| FR-014 | إرسال لأجهزة متعددة لنفس المستخدم | ✅ |
| FR-015 | نقاط REST API للأجهزة والتفضيلات | ✅ |
| FR-016 | إشعارات SOS غير قابلة للتعطيل | ✅ |

---

## 3. الخوارزميات والأنماط المعمارية المستخدمة (Algorithms & Patterns)

### 3.1 خوارزمية الإرسال الدفعي المُفهرَس (Indexed Batch Dispatch)

**المكوّن:** `notifications/services/push_service.py` — `send_to_user()`

**المشكلة المحلولة:** FCM يدعم حتى 500 رسالة لكل استدعاء عبر `messaging.send_each()`. عند إرسال إشعار لمستخدم لديه أجهزة متعددة (أو لمجموعة ممرضات)، يجب تقسيم الرسائل إلى دفعات مع ربط صحيح بين كل استجابة ورمز الجهاز الأصلي.

**تسلسل الخوارزمية:**

```
┌─────────────┐     materialize()    ┌────────────────┐     send_each()    ┌──────────┐
│ DeviceToken  │───────────────────►│  token_list[]  │──────────────────►│  FCM API │
│ QuerySet     │   (1 DB query)      │ (Python list)  │  batches of 500   │ (Google) │
└─────────────┘                      └────────────────┘                    └──────────┘
                                            │                                   │
                                            │            BatchResponse          │
                                            │◄──────────────────────────────────┘
                                            │
                                    token_list[i + idx]
                                    (offset = batch_start + response_index)
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │NotificationLog│
                                    │ (per device)  │
                                    └──────────────┘
```

**الكود الجوهري:**

```python
# تحقيق مادي مرة واحدة — يقضي على 3 استعلامات منفصلة (.exists + .count + تكرار)
token_list = list(DeviceToken.objects.filter(user_id=user_id, is_active=True))

BATCH_SIZE = 500
for i in range(0, len(messages), BATCH_SIZE):
    batch = messages[i:i + BATCH_SIZE]
    batch_response = messaging.send_each(batch)
    for idx, response in enumerate(batch_response.responses):
        token_obj = token_list[i + idx]  # إزاحة عامة: بداية الدفعة + فهرس الاستجابة
```

**الثغرة التي اكتُشفت وأُصلحت (CRITICAL):**

الكود الأولي استخدم `list(tokens)[idx]` — وهو نمط خطير لسببين:
1. `list(tokens)` يُعيد تقييم الـ QuerySet في كل تكرار (استعلام DB متكرر).
2. `idx` هو فهرس نسبي داخل الدفعة — للدفعة الثانية (i=500)، الاستجابة رقم 0 كانت ترتبط برمز الجهاز رقم 0 بدلاً من 500.

**النتيجة:** رموز أجهزة خاطئة كانت ستُعطَّل عند خطأ `UnregisteredError` — فساد بيانات صامت.

**الإصلاح:** تحقيق مادي واحد (`token_list = list(...)`) + إزاحة عامة (`token_list[i + idx]`).

---

### 3.2 خوارزمية فحص التفضيلات المسبقة (Pre-Queue Preference Gate)

**المكوّن:** `notifications/services/push_service.py` — السطور 53–68

**المشكلة المحلولة:** هل نفحص تفضيلات المستخدم قبل أم بعد وضع المهمة في طابور Celery؟

**القرار:** فحص **قبل** الإرسال (في خدمة `push_service`، ليس في Celery task).

```python
category = EVENT_CATEGORY_MAP.get(event_type)
if category is not None:
    try:
        prefs = user.notification_prefs
        if not prefs.is_category_enabled(category):
            # إنشاء سجل SKIPPED دون إرسال
            NotificationLog.objects.create(status=NotificationStatus.SKIPPED, ...)
            return logs
    except UserNotificationPrefs.DoesNotExist:
        pass  # التفضيلات غير موجودة = الافتراضي "الكل مُفعَّل"
```

**المبررات:**
- استعلام `SELECT` واحد أسرع من وضع مهمة Celery وإلغائها.
- كل إشعار مرفوض يُسجَّل بحالة `SKIPPED` في سجل التدقيق.
- **الاستثناء الحاسم:** `SOS_ALERT` يتجاوز التفضيلات بالكامل — `EVENT_CATEGORY_MAP["SOS_ALERT"] = None`.

**خوارزمية `is_category_enabled()`:**

```python
def is_category_enabled(self, category: str | None) -> bool:
    if category is None:
        return True  # SOS — لا يمكن تعطيله (FR-016)
    return getattr(self, category, True)  # الافتراضي True إذا كان الحقل غير موجود
```

---

### 3.3 خوارزمية سجل قوالب الإشعارات ثنائي اللغة (Bilingual Template Registry)

**المكوّن:** `notifications/templates.py`

**الهيكل:** قاموس Python مسطح مُفهرس بـ `NotificationEventType`:

```python
NOTIFICATION_TEMPLATES = {
    "NURSE_ASSIGNED": {
        "title_ar": "تحديث الزيارة",
        "title_en": "Visit Update",
        "body_ar": "تم تعيين الممرض/ة {nurse_name} لزيارتك",
        "body_en": "Your nurse {nurse_name} has been assigned to your visit",
    },
    # ... 8 أنواع أحداث
}
```

**خوارزمية `render_template()`:**

```
event_type → NOTIFICATION_TEMPLATES[event_type]
                  → title_{language}.format(**context)
                  → body_{language}.format(**context)
                  → return (title, body)
```

**القرارات المعمارية:**
- **`str.format()` بدلاً من قوالب Django**: الإشعارات نصوص بسيطة وليست HTML — لا حاجة لمحرك قوالب كامل.
- **`gettext_lazy` غير مستخدم هنا**: القوالب مُخزنة كنصوص ثابتة لأن اللغة تُحدَّد في وقت التشغيل من `user.preferred_language`، لا من إعدادات Django العامة.
- **`KeyError` المتعمد**: إذا كان المتغير مفقوداً (مثل `{nurse_name}` بدون توفير `nurse_name`)، Python يرمي `KeyError` مباشرة — وهو السلوك المرغوب لكشف الأخطاء مبكراً.

---

### 3.4 خوارزمية الإعادة الأسّية لمهام Celery (Exponential Backoff Retry)

**المكوّن:** `notifications/tasks.py` — `send_notification_task`

```python
@shared_task(
    bind=True,
    queue="notifications",
    autoretry_for=(Exception,),
    retry_backoff=True,        # تفعيل التأخير الأسّي
    retry_backoff_max=60,      # حد أقصى 60 ثانية
    max_retries=3,             # 3 محاولات
    acks_late=True,            # تأكيد الاستلام بعد الإكمال
)
```

**جدول إعادة المحاولات:**

| المحاولة | التأخير | المجموع التراكمي | السيناريو |
|----------|---------|------------------|-----------|
| 1 | ~2 ثانية | 2s | خطأ شبكة عابر |
| 2 | ~4 ثوانٍ | 6s | FCM مُحمَّل مؤقتاً |
| 3 | ~8 ثوانٍ | 14s | خطأ مستمر → تسجيل فشل نهائي |

**`acks_late=True`:** يضمن أن المهمة لا تُحذف من الطابور حتى تُكمل بنجاح — حماية ضد توقف Worker أثناء الإرسال.

---

### 3.5 خوارزمية تنظيف الرموز المنتهية (Stale Token Cleanup)

**المكوّن:** `notifications/tasks.py` — `cleanup_stale_tokens`
**التشغيل:** Celery Beat — يومياً الساعة 03:00 بتوقيت القاهرة

```python
@shared_task(queue="notifications")
def cleanup_stale_tokens() -> int:
    cutoff = timezone.now() - timedelta(days=settings.NOTIFICATION_STALE_TOKEN_DAYS)
    count = DeviceToken.objects.filter(
        is_active=True,
        last_active__lt=cutoff,
    ).update(is_active=False)  # Bulk UPDATE — استعلام واحد
    return count
```

**استراتيجية مزدوجة:**
1. **تفاعلية:** عند استلام `UnregisteredError` من FCM، يُعطَّل الرمز فوراً (`is_active=False`).
2. **استباقية:** تنظيف يومي يمسح الرموز التي لم تنشط منذ 30 يوماً.

---

### 3.6 خوارزمية ربط انتقالات الزيارة بالإشعارات (Visit Transition → Notification Mapping)

**المكوّن:** `notifications/signals.py` — `_dispatch_visit_notification()`

**جدول الربط:**

| الانتقال إلى | نوع الحدث | المستلمون |
|--------------|-----------|-----------|
| `PENDING_AGENCY` | `DISPATCH_OFFER` | مدير الوكالة |
| `PENDING_NURSE` | `NURSE_ASSIGNED` | المريض + الممرض (إن وُجد) |
| `EN_ROUTE` | `NURSE_EN_ROUTE` | المريض |
| `IN_PROGRESS` | `NURSE_ARRIVED` | المريض + مدير الوكالة |
| `COMPLETED` | `VISIT_COMPLETED` | المريض |
| `CANCELLED` | `VISIT_CANCELLED` | المريض + الممرض + مدير الوكالة |

**نقطة التكامل:** `Visit.transition_to()` في `visits/models.py` يستدعي `_dispatch_visit_notification()` بعد `self.save()` مباشرة، ملفوفاً في `try/except` لضمان أن فشل الإشعار لا يُعيق انتقال حالة الزيارة.

```python
# visits/models.py — transition_to()
self.save(update_fields=["status", "updated_at"])
try:
    _dispatch_visit_notification(self, self._previous_status, new_status)
except Exception:
    logger.exception("Notification dispatch failed for visit %s", self.id)
```

---

### 3.7 خوارزمية حماية PII في الحمولة (PII Guard)

**المكوّن:** `notifications/services/push_service.py` — `_build_data_payload()`

```python
PII_FIELDS = frozenset([
    "phone", "national_id", "email", "medical_notes",
    "address", "first_name_ar", "last_name_ar", "full_name",
])

def _build_data_payload(context: dict) -> dict:
    data = {
        "visit_id": context.get("visit_id", ""),
        "event_type": context.get("event_type", ""),
    }
    for key in context.keys():
        if key.lower() in PII_FIELDS:
            raise ValueError("PII field cannot be in payload")
    return data
```

**طبقتان من الحماية:**
1. **القائمة البيضاء:** فقط `visit_id` و`event_type` يُنسخان إلى الحمولة.
2. **القائمة السوداء:** أي مفتاح PII في `context` يرمي `ValueError` — كشف مبكر لأخطاء المطورين.

**التوافق مع القانون 151/2020:** الإشعار الذي يرسله النظام يحتوي عنوان وجسم (عام)، بينما حمولة البيانات تحتوي فقط مُعرِّفات مُبهمة. التطبيق يسترجع التفاصيل عبر استدعاء API مُصادق.

---

### 3.8 خوارزمية Upsert لرموز الأجهزة (Device Token Upsert)

**المكوّن:** `notifications/serializers.py` — `DeviceTokenSerializer.create()`

```python
def create(self, validated_data):
    validated_data["user"] = self.context["request"].user
    token, created = DeviceToken.objects.update_or_create(
        token=validated_data["token"],
        defaults={**validated_data},
    )
    self._created = created
    return token
```

**السلوك:**
- `POST` بنفس رمز FCM → تحديث (200 OK)، لا تكرار.
- `POST` برمز جديد → إنشاء (201 Created).
- `DELETE` → تعطيل ناعم (`is_active=False`)، لا حذف فعلي.

---

## 4. نتائج الاختبارات (Test Results)

### 4.1 مصفوفة الاختبارات — خدمة الإرسال (`test_push_service.py`)

| الاختبار | الحالة | التبرير |
|----------|--------|---------|
| `test_send_to_user_success` | ✅ | FCM مُحاكى → `NotificationLog(status=SENT)` |
| `test_send_to_user_no_tokens` | ✅ | بدون أجهزة → `status=SKIPPED`, `fcm_error="No active device tokens"` |
| `test_send_to_user_fcm_failure` | ✅ | خطأ FCM → `status=FAILED` + تعطيل الرمز |
| `test_send_to_user_renders_arabic_template` | ✅ | `preferred_language="ar"` → عنوان بالعربية |
| `test_send_to_user_renders_english_template` | ✅ | `preferred_language="en"` → عنوان بالإنجليزية |
| `test_send_to_user_multiple_devices` | ✅ | 3 أجهزة → 3 سجلات `NotificationLog` |
| `test_send_to_user_data_payload_has_visit_id_only` | ✅ | حمولة البيانات لا تحتوي PII |
| `test_dispatch_offer_sent_to_agency_admin` | ✅ | يُرسل لمدير الوكالة |
| `test_payment_settled_notification_correct_amount` | ✅ | المبلغ `Decimal("350.00")` يظهر كـ `"350.00"` لا `"350.0"` |
| `test_payment_settled_uses_str_decimal_not_float` | ✅ | لا تحويل `float` — الدستور يفرض ذلك |
| `test_agency_admin_disabled_financial_updates` | ✅ | `financial_updates=False` → `SKIPPED` |
| `test_preference_does_not_block_sos` | ✅ | `SOS_ALERT` يتجاوز كل التفضيلات (FR-016) |
| `test_auto_dispatch_notifies_eligible_nurses` | ✅ | 5 ممرضات → 5 سجلات `DISPATCH_OFFER` |
| `test_nurse_logged_out_token_inactive` | ✅ | رمز معطل → `SKIPPED` |

### 4.2 مصفوفة الاختبارات — القوالب (`test_templates.py`)

| الاختبار | الحالة | التبرير |
|----------|--------|---------|
| `test_render_template_nurse_assigned_arabic` | ✅ | العنوان = `"تحديث الزيارة"` |
| `test_render_template_nurse_assigned_english` | ✅ | العنوان = `"Visit Update"` |
| `test_render_template_payment_settled_arabic` | ✅ | الجسم يحتوي `"ج.م"` |
| `test_render_template_all_event_types_arabic` | ✅ | 8 أحداث × عربي = لا أخطاء |
| `test_render_template_all_event_types_english` | ✅ | 8 أحداث × إنجليزي = لا أخطاء |
| `test_render_template_missing_variable_raises_key_error` | ✅ | متغير مفقود → `KeyError` |
| `test_render_template_unknown_event_type_raises_key_error` | ✅ | حدث غير معروف → `KeyError` |

### 4.3 مصفوفة الاختبارات — مهام Celery (`test_tasks.py`)

| الاختبار | الحالة | التبرير |
|----------|--------|---------|
| `test_send_notification_task_dispatches_to_push_service` | ✅ | `.delay()` → `send_to_users()` |
| `test_send_notification_task_handles_multiple_users` | ✅ | 3 مستخدمين → 3 استدعاءات |
| `test_send_notification_task_retry_on_exception` | ✅ | `ConnectionError` → إعادة محاولة |
| `test_cleanup_stale_tokens_deactivates_old` | ✅ | 31 يوم → `is_active=False` |
| `test_cleanup_stale_tokens_keeps_recent` | ✅ | 5 أيام → يبقى `is_active=True` |

### 4.4 مصفوفة الاختبارات — واجهة API (`test_api.py`)

| الاختبار | الحالة | التبرير |
|----------|--------|---------|
| `test_register_device_token_success` | ✅ | `POST` → 201 |
| `test_register_device_token_upsert_existing` | ✅ | تكرار نفس الرمز → 200 (upsert) |
| `test_register_device_token_invalid_platform` | ✅ | `BLACKBERRY` → 400 |
| `test_register_device_token_unauthenticated` | ✅ | بدون JWT → 401 |
| `test_list_device_tokens` | ✅ | يعرض الرموز النشطة فقط |
| `test_delete_device_token_success` | ✅ | `DELETE` → 204 + `is_active=False` |
| `test_delete_device_token_belongs_to_other_user` | ✅ | مستخدم آخر → 404 (عزل المستأجرين) |
| `test_get_notification_preferences_default` | ✅ | كل القيم `True` |
| `test_patch_notification_preferences` | ✅ | `PATCH` → تحديث جزئي (200) |
| `test_get_preferences_unauthenticated` | ✅ | بدون JWT → 401 |

### 4.5 مصفوفة الاختبارات — النماذج (`test_models.py`)

| الاختبار | الحالة | التبرير |
|----------|--------|---------|
| `test_notification_event_type_has_8_values` | ✅ | `len(choices) == 8` |
| `test_notification_status_has_3_values` | ✅ | `SENT, FAILED, SKIPPED` |
| `test_event_category_map_covers_all_events` | ✅ | كل حدث مُغطى |
| `test_sos_alert_has_no_category` | ✅ | `SOS_ALERT → None` |
| `test_notification_log_creation` | ✅ | إنشاء وفحص UUID |
| `test_user_notification_prefs_defaults` | ✅ | كل القيم `True` |
| `test_user_notification_prefs_auto_created_on_user_save` | ✅ | إشارة `post_save` تعمل |
| `test_device_token_uniqueness` | ✅ | تكرار → `IntegrityError` |
| `test_preferred_language_default_is_arabic` | ✅ | الافتراضي `"ar"` |

### 4.6 ملخص النتائج

| المجموعة | عدد الاختبارات | ناجح | فاشل |
|----------|---------------|------|------|
| خدمة الإرسال | 14 | 14 | 0 |
| القوالب | 7 | 7 | 0 |
| مهام Celery | 5 | 5 | 0 |
| واجهة API | 10 | 10 | 0 |
| النماذج | 9 | 9 | 0 |
| **المجموع** | **45** | **45** | **0** |

---

## 5. مراجعة الجودة — تحليل الأثر المتسلسل (Code Review & Cascading Risk Analysis)

خلال مراجعة الكود تم رصد **4 مشكلات**. قبل تطبيق أي إصلاح، تم تحليل ما إذا كان الحل سيُنتج أخطاء أكثر فداحة:

### 5.1 المشكلات المُعالجة

| الشدة | المشكلة | الموقع | الإصلاح | خطر الإصلاح |
|-------|---------|--------|---------|-------------|
| 🔴 CRITICAL | خلل في فهرسة الدفعات — `list(tokens)[idx]` يستخدم فهرس نسبي داخل الدفعة مع QuerySet كامل. للدفعة 2+ (i≥500)، الاستجابات ترتبط برموز خاطئة | `push_service.py:112` | تحقيق مادي واحد `token_list = list(...)` + فهرس عام `token_list[i + idx]` | ⬇️ منعدم — تصحيح منطقي صرف |
| 🟡 WARNING | خطأ إملائي عربي — `"آiphone"` خليط عربي/لاتيني | `models.py:14` | تصحيح إلى `"آي أو إس"` | ⬇️ منعدم — تغيير نصي فقط |
| 🟡 WARNING | `except:` (بدون تحديد) يبتلع كل الاستثناءات بما فيها `SystemExit` و`KeyboardInterrupt` | `push_service.py:63` | تغيير إلى `except UserNotificationPrefs.DoesNotExist:` | ⬇️ منخفض — أصبح أكثر دقة |
| 🟡 WARNING | استعلام N+1 — `.exists()` + `.count()` + تكرار = 3 استعلامات | `push_service.py:73–84` | تحقيق مادي واحد + `not token_list` + `len(token_list)` = استعلام واحد | ⬇️ منعدم — تحسين أداء |

### 5.2 تحليل مفصل للثغرة الحرجة

**السيناريو التدميري (قبل الإصلاح):**

1. مستخدم لديه 600 رمز جهاز (600 جهاز — حالة حدية).
2. النظام يُقسم إلى دفعتين: الأولى (0–499)، الثانية (500–599).
3. الدفعة الثانية تُرسل وتعود 100 استجابة.
4. `list(tokens)[0]` يُعيد رمز الجهاز الأول **في الـ QuerySet الأصلي** (الجهاز رقم 0).
5. إذا كانت الاستجابة `UnregisteredError` → الرمز رقم 0 يُعطَّل **بدلاً من** الرمز رقم 500.
6. **النتيجة:** فقدان إشعارات لأجهزة صالحة + بقاء أجهزة تالفة.

**بعد الإصلاح:** `token_list[500 + 0]` = الجهاز رقم 500 بشكل صحيح.

---

## 6. مصفوفة الأمان (Security Matrix)

| السياق الأمني | الآلية | النتيجة |
|---------------|--------|---------|
| PII في حمولة الإشعار | `_build_data_payload()` + `PII_FIELDS` القائمة السوداء | ❌ مرفوض فوراً |
| مستخدم يحذف رمز مستخدم آخر | `DeviceToken.objects.get(token=..., user=request.user)` | 404 (عزل) |
| SOS يُعطَّل من التفضيلات | `EVENT_CATEGORY_MAP["SOS_ALERT"] = None` → يتجاوز الفحص | ✅ دائم الإرسال |
| JWT مفقود في طلب API | `IsAuthenticated` permission class | 401 |
| `float` في مبالغ مالية | `str(Decimal("350.00"))` — لا تحويل `float` | ✅ دقة مالية |
| رمز FCM مكشوف في API | `to_representation()` يُقنّع الرمز في `GET /devices/` | ✅ مُقنَّع |

---

## 7. الملفات المُعدَّلة (Changed Files Summary)

| الملف | نوع | الحجم | الغرض |
|-------|------|-------|-------|
| `notifications/models.py` | MODIFY | 171 سطر | 3 نماذج: `DeviceToken` (موجود) + `NotificationLog` + `UserNotificationPrefs`، قيم عد `NotificationEventType` (8) + `NotificationStatus` (3)، خريطة `EVENT_CATEGORY_MAP` |
| `notifications/services/push_service.py` | MODIFY | 148 سطر | خدمة FCM الكاملة: `send_to_user()` + `send_to_users()` + `_build_data_payload()` |
| `notifications/tasks.py` | MODIFY | 71 سطر | مهمتا Celery: `send_notification_task` (retry أسّي) + `cleanup_stale_tokens` (دوري) |
| `notifications/templates.py` | NEW | 88 سطر | سجل قوالب ثنائي اللغة + `render_template()` |
| `notifications/signals.py` | NEW | 151 سطر | إشارة إنشاء التفضيلات + ربط انتقالات الزيارة + إشعار التسوية المالية |
| `notifications/views.py` | NEW | 79 سطر | `DeviceTokenViewSet` + `NotificationPrefsView` |
| `notifications/serializers.py` | NEW | 49 سطر | `DeviceTokenSerializer` (upsert) + `UserNotificationPrefsSerializer` |
| `notifications/urls.py` | NEW | ~15 سطر | مسارات `devices/` + `preferences/` |
| `notifications/admin.py` | NEW | ~60 سطر | واجهة Django Admin للقراءة فقط (NotificationLog) |
| `notifications/apps.py` | MODIFY | ~20 سطر | تهيئة Firebase Admin SDK في `ready()` |
| `users/models.py` | MODIFY | +1 حقل | `preferred_language` CharField(5) default=`"ar"` |
| `config/settings.py` | MODIFY | +5 أسطر | `FIREBASE_CREDENTIALS_PATH` + `NOTIFICATION_STALE_TOKEN_DAYS` |
| `config/celery.py` | MODIFY | +5 أسطر | `cleanup-stale-tokens` في `beat_schedule` |
| `config/urls.py` | MODIFY | +1 سطر | `include("notifications.urls")` |

**الإجمالي:** ~900 سطر كود إنتاجي + ~600 سطر اختبارات = **~1,500 سطر**

---

## 8. هيكل نقاط API (API Endpoint Summary)

| الطريقة | المسار | الوصف | الحالة |
|---------|--------|-------|--------|
| `POST` | `/api/v1/notifications/devices/` | تسجيل رمز جهاز (upsert) | 201/200 |
| `GET` | `/api/v1/notifications/devices/` | عرض الأجهزة النشطة | 200 |
| `DELETE` | `/api/v1/notifications/devices/{token}/` | إلغاء رمز (تعطيل ناعم) | 204 |
| `GET` | `/api/v1/notifications/preferences/` | استرجاع التفضيلات | 200 |
| `PATCH` | `/api/v1/notifications/preferences/` | تحديث جزئي للتفضيلات | 200 |

---

## 9. ملاحظات إضافية وتوصيات

### 9.1 التوافق مع الدستور المعماري

- ✅ **B2B2C Compliance**: الممرضون يتبعون وكالات — لا إشعارات P2P مباشرة.
- ✅ **Arabic-First**: كل القوالب مكتوبة بالعربية أولاً، الافتراضي `preferred_language="ar"`.
- ✅ **Decimal Precision**: المبالغ المالية تُمرر كـ `str(Decimal)` — لا تحويل `float`.
- ✅ **Agency Layer**: كل إشعار يمر عبر `visit.agency` — لا تجاوز.
- ✅ **QA-Driven**: 45 اختباراً يُغطي كل خوارزمية وسيناريو حدَّي.
- ✅ **Law 151/2020**: لا PII في حمولات الإشعارات، فحص مزدوج (قائمة بيضاء + سوداء).

### 9.2 توصيات للإنتاج

1. **Firebase Credentials**: تأكد من تكوين `GOOGLE_APPLICATION_CREDENTIALS` في بيئة الإنتاج قبل النشر — النظام يُسجل تحذيراً في وضع التطوير ويتخطى الإرسال.
2. **مراقبة معدل SKIPPED**: إضافة لوحة Grafana لنسبة `NotificationLog.status=SKIPPED` — نسبة عالية تعني أن المستخدمين يُعطلون الإشعارات بكثرة.
3. **مراقبة FAILED**: تنبيه Slack عند تجاوز `status=FAILED` نسبة 5% — قد يشير إلى مشكلة FCM أو رموز منتهية.
4. **FCM Topic Messaging**: للمرحلة القادمة، يمكن استخدام Topic Messaging لبث إشعارات تسويقية لفئات كاملة بدلاً من الإرسال الفردي.
5. **إشعارات الويب (PWA)**: الهيكل الحالي يدعم `Platform.WEB` — الخطوة التالية هي تكامل Service Worker في الـ Frontend.

---

**المهندس المعماري:** العميل الرئيسي — Multi-Agent Orchestrator
**لصالح نظام:** Wateen B2B2C Aggregator (المرحلة الخامسة)
**تاريخ التقرير:** 2026-03-26
