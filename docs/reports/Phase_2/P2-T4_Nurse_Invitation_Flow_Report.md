# توثيق التذكرة [P2-T4]: نظام دعوات الممرضين للوكالات (Nurse Invitation Flow)

## 📌 1. نظرة عامة (Overview)

تم بناء وتطوير نظام الدعوات لتلبية نموذج العمل **B2B2C** الخاص بمنصة "وتين" (Wateen). هذا النظام يمكن مديري وكالات التمريض من دعوة ممرضين جدد للانضمام إلى وكالتهم عبر رمز مشفر (Cryptographic Token).

**القيود المحورية:**

- يُمنع تمامًا تسجيل الممرضين كعمل حر (Freelancers). يجب أن يكون كل ممرض تابعًا لوكالة (Mandatory Foreign Key).
- يمتثل النظام بشكل كامل لقانون حماية البيانات الشخصية المصري 151/2020 وتوجيهات وزارة الصحة (MoH) من خلال حماية بيانات PII ومنع استخراجها (IDOR).

---

## 🏗️ 2. هندسة قاعدة البيانات والنماذج (Models)

### نموذج `NurseInvitation`

يحتوي النموذج على الحقول الأساسية لربط الممرض بالوكالة قبل إنشائه، مع تضمين رمز مشفر للتحقق وفترة صلاحية (72 ساعة).

```python
class InvitationStatus(models.TextChoices):
    PENDING = "PENDING", _("قيد الانتظار")
    ACCEPTED = "ACCEPTED", _("مقبول")
    EXPIRED = "EXPIRED", _("منتهي الصلاحية")
    REVOKED = "REVOKED", _("ملغى")

class NurseInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(
        "AgencyProfile",
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    phone = models.CharField(_("الهاتف"), max_length=20)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    status = models.CharField(
        max_length=15,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
        db_index=True,
    )
    expires_at = models.DateTimeField(_("تاريخ الانتهاء"))
    # ...
```

---

## ⚙️ 3. الخوارزميات وآليات العمل (Algorithms)

### أ. خوارزمية تحديد معدل الطلبات (Token Bucket Rate Limiting)

تم تطبيق خوارزمية **Token Bucket** لحماية نقطة النهاية (Endpoint) الخاصة بإرسال الدعوات من إساءة الاستخدام وهجمات SMS Bombing. تم تعديلها لتصبح "ذرية بالكامل" (Fully Atomic) باستخدام `cache.incr` من Redis لتفادي أخطاء تسابق المعالجة (Race Conditions: TOCTOU).

```python
class TokenBucketRateLimiter(BaseRateLimiter):
    def is_allowed(self, key: str) -> bool:
        cache_key = self._get_cache_key(key)
        try:
            # Atomic increment — prevents TOCTOU race condition
            new_count = cache.incr(cache_key)
            if new_count == 1:
                # First request in this window — set the TTL
                cache.expire(cache_key, self.window_seconds)

            return new_count <= self.max_requests
        except Exception:
            return True # Fail-open strategy
```

### ب. خوارزمية التسجيل الذري (Atomic Registration)

عند قبول الممرض للدعوة، يتم تحويل حالة الدعوة إلى مقبولة، وإنشاء حساب المستخدم، وإنشاء ملف الممرض بشكل **ذري** لمنع حدوث شذوذ في البيانات في حالة فشل أي خطوة (Transaction Atomicity).

```python
@transaction.atomic
def accept_invitation(self, token: str, user_data: dict, profile_data: dict) -> CustomUser:
    # 1. Row-level Lock on Invitation
    invitation = NurseInvitation.objects.select_for_update().get(token=token)

    if not invitation.is_valid:
        raise InvalidTokenError(_("الدعوة غير صالحة أو منتهية الصلاحية."))

    # 2. Check Capacity limits
    self._check_agency_capacity(invitation.agency)

    # 3. Create User & Profile Atoms
    try:
        user = CustomUser.objects.create_user(**user_data)
        profile = NurseProfile.objects.create(
            user=user,
            agency=invitation.agency, # Mandatory B2B binding
            **profile_data
        )
        # 4. Invalidate Token
        invitation.status = InvitationStatus.ACCEPTED
        invitation.save()
        return user
    except IntegrityError:
        raise DuplicateUserError(_("هذا المستخدم مسجل بالفعل."))
```

---

## 📡 4. واجهات برمجة التطبيقات (API & Serializers)

- `POST /api/v1/agencies/nurses/invite/`: إرسال دعوة (تحتاج لصلاحية مدير الوكالة + يخضع للـ Rate Limiting).
- `POST /api/v1/auth/accept-invitation/`: قبول دعوة وإنشاء ملف. Endpoint عامة، محمية بواسطة `AnonRateThrottle` لـ `10/min` ضد هجمات الـ Brute-Force للـ Token.
- `GET /api/v1/agencies/invitations/`: عرض الدعوات الخاصة بوكالة بعينها فقط، لمنع (IDOR).
- `POST /api/v1/agencies/invitations/<id>/revoke/`: إلغاء الدعوة (تتحول إلى `REVOKED` لمنع التلاعب).

---

## 🖥️ 5. واجهة المستخدم (React Admin Frontend)

تم بناء لوحة تحكم مديري الوكالات عبر منصة **React Admin** ودعم كامل باللغة العربية (RTL).

- **`InvitationList.tsx`**: عرض الدعوات بشكل أنيق وجدولة البيانات، تتضمن تصفيات وتنسيق بالألوان لكل حالة (قيد الانتظار، مقبول، مُلغى، منتهي).
- **`InvitationCreate.tsx`**: نموذج إرسال الدعوة مع فحوصات لحظية على سعة الباقة (SaaS Plan Capacity) وحدود الإرسال.
- **`InvitationActions.tsx`**: حزمة أزرار ذكية تمكن المدير من "إلغاء الدعوة"، أو "إعادة إرسال"، و "نسخ الرابط".

---

## 🛡️ 6. معايير الأمان التي تم تشديدها في عملية המراجعة (QA & Security Fixes)

أثناء المراجعة التقنية والاختبار، تم اكتشاف وإصلاح الحثيثات الأمنية التالية:

### 🔴 التهديدات الحرجة (P0 Fixes)

1. **اصفرار محدودية الطلب والتسابق (Race Condition Fix - TOCTOU):**
   - **الحيثية:** كان Rate Limiter يستعلم من Cache ثم يحقن القيمة الجديدة. في الحملات المتزامنة يمر أكثر من العدد المسموح. تم استبداله بعملية `cache.incr()` ذرية تماما من Redis.
2. **منع توقف المعالجة المتزامنة (Celery Task Missing Methods):**
   - **الحيثية:** دوال إرسال الاشعارات `send_nurse_invitation` غير متصلة فعلياً. تم ربط المهام الموجهة ببنية `NotificationService` لتمرير الـ SMS.

### 🟡 التحذيرات والتعديلات المتوسطة (P1 Fixes)

3. **حماية التحديد الجغرافي والشخصي (PII Data Privacy):**
   - **الحيثية:** حماية معلومات المستفيد (قانون 151/2020 المصري).
   - **النتيجة:** تم حجب أرقام الهواتف من مسجل الأحداث `logger.info("... phone 010***4567")`.
4. **ربط العناوين الصحيحة لبيئة الإنتاج (Hardcoded URLs):**
   - **الحيثية:** في `InvitationCreate.tsx` و `InvitationActions.tsx` كانت عناوين الـ API مسماة بـ `localhost:8000`.
   - **النتيجة:** تم تغييرها إلى متغيرات البيئة `process.env.NEXT_PUBLIC_API_URL` الديناميكية التي تدعم أنظمة الإنتاج.
5. **المهام الزائدة بقاعدة البيانات:**
   - **الحيثية:** تنقيح ملف الهجرة الخاص بـ `NurseInvitation` لإزالة فهارس `Index` مكررة لتجنب تكرار الجداول في SQL.
6. **دقة كلمة المرور (Password Validation):**
   - **الحيثية:** إضافة `django.contrib.auth.password_validation` للـ Serializer لضمان حماية الحسابات.

---

## 🚦 7. ملخص الاختبارات والمراجعة (Testing Outcomes)

- **اختبار الأمان والمجال العازل (Agency Isolation):**
  مدير الوكالة (Agency A) لا يملك صلاحية عرض دعوات (Agency B) – اجتاز الاختبار (IDOR Prevented).
- **سعة הבاقة (SaaS Capacity Enforcement):**
  النظام يجمع عدد الممرضين المهيئين فعلياً مع عدد الدعوات القائمة (`PENDING`). فشل إرسال الدعوة إذا تم تجاوز الخطة المدفوعة – اجتاز الاختبار.
- **الاختبار الوظيفي لواجهة المستخدم:**
  مكون `InvitationList` يظهر الخيارات الصحيحة، ويعمل بفعالية باللغة العربية – اجتاز الاختبار.

---

_تم توليد وتدقيق هذا التقرير داخلياً — وتعديلات التذكرة جاهزة للدمج مع المنظومة الرئيسية (Merging)._
