---
ticket: "1.4"
title: "Profiles Architecture – PatientProfile & NurseProfile"
priority: high
depends_on: "1.3 (Custom User Model – COMPLETED)"
estimated_complexity: medium
---

# Ticket 1.4 — Profiles Architecture (Patient vs Nurse)

## Objective

Implement `PatientProfile` and `NurseProfile` models linked via `OneToOneField` to `CustomUser`. Add `post_save` signals to auto-create empty profiles on user registration. Register models in Django Admin. Generate and apply database migrations.

---

## Prerequisites (Already Verified)

- `CustomUser` model exists at `users/models.py` with UUID primary key and `UserRole` choices (`PATIENT`, `NURSE`, `DOCTOR`, `ADMIN`).
- PostGIS is fully configured:
  - `django.contrib.gis` in `INSTALLED_APPS` (`config/settings.py:49`)
  - DB engine is `django.contrib.gis.db.backends.postgis` (`config/settings.py:92`)
  - Docker image is `postgis/postgis:16-3.4` (`docker/docker-compose.yml:84`)
- `users/signals.py` exists as an empty placeholder (ready for implementation).
- `users/apps.py` exists but does NOT import signals yet.

---

## Step-by-Step Instructions

### Step 1: Add Profile Models to `users/models.py`

Append the following two models **after** the existing `CustomUser` class. Do NOT modify any existing code.

#### 1A. `PatientProfile` Model

```python
from django.contrib.gis.db import models as gis_models


class VerificationStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    VERIFIED = 'VERIFIED', _('Verified')
    REJECTED = 'REJECTED', _('Rejected')


class GenderChoices(models.TextChoices):
    MALE = 'MALE', _('Male')
    FEMALE = 'FEMALE', _('Female')


class PatientProfile(models.Model):
    """Profile containing patient-specific medical and personal data."""

    user = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='patient_profile',
        verbose_name=_('المستخدم'),
    )
    date_of_birth = models.DateField(
        _('تاريخ الميلاد'),
        null=True,
        blank=True,
    )
    gender = models.CharField(
        _('الجنس'),
        max_length=10,
        choices=GenderChoices.choices,
        blank=True,
        default='',
    )
    address_text = models.TextField(
        _('العنوان'),
        blank=True,
        default='',
    )
    home_location = gis_models.PointField(
        _('موقع المنزل'),
        geography=True,
        srid=4326,
        null=True,
        blank=True,
    )
    medical_notes = models.TextField(
        _('ملاحظات طبية'),
        blank=True,
        default='',
    )
    emergency_contact = models.CharField(
        _('رقم الطوارئ'),
        max_length=15,
        blank=True,
        default='',
    )
    wearables_enabled = models.BooleanField(
        _('أجهزة قابلة للارتداء'),
        default=False,
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('ملف المريض')
        verbose_name_plural = _('ملفات المرضى')
        db_table = 'users_patient_profile'

    def __str__(self) -> str:
        return f'PatientProfile({self.user.national_id})'
```

#### 1B. `NurseProfile` Model

```python
class NurseProfile(models.Model):
    """Profile containing nurse-specific professional and verification data."""

    user = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='nurse_profile',
        verbose_name=_('المستخدم'),
    )
    national_id_document = models.CharField(
        _('رقم الهوية المهنية'),
        max_length=50,
        blank=True,
        default='',
    )
    syndicate_number = models.CharField(
        _('رقم النقابة'),
        max_length=50,
        blank=True,
        default='',
    )
    syndicate_expiry = models.DateField(
        _('انتهاء عضوية النقابة'),
        null=True,
        blank=True,
    )
    specializations = models.JSONField(
        _('التخصصات'),
        default=list,
        blank=True,
    )
    rating = models.DecimalField(
        _('التقييم'),
        max_digits=3,
        decimal_places=2,
        default=5.00,
    )
    is_available = models.BooleanField(
        _('متاح'),
        default=False,
    )
    last_location = gis_models.PointField(
        _('آخر موقع'),
        geography=True,
        srid=4326,
        null=True,
        blank=True,
    )
    verification_status = models.CharField(
        _('حالة التحقق'),
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('ملف الممرض/ة')
        verbose_name_plural = _('ملفات الممرضين')
        db_table = 'users_nurse_profile'

    def __str__(self) -> str:
        return f'NurseProfile({self.user.national_id})'
```

> **IMPORTANT:** Import `gis_models` at the top of the file:
>
> ```python
> from django.contrib.gis.db import models as gis_models
> ```

---

### Step 2: Implement Post-Save Signals in `users/signals.py`

Replace the placeholder content with the following:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, UserRole, PatientProfile, NurseProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create the appropriate profile when a new user is registered.
    - PATIENT role -> PatientProfile
    - NURSE role -> NurseProfile
    Uses get_or_create to be idempotent and safe for re-runs.
    """
    if created:
        if instance.role == UserRole.PATIENT:
            PatientProfile.objects.get_or_create(user=instance)
        elif instance.role == UserRole.NURSE:
            NurseProfile.objects.get_or_create(user=instance)
```

---

### Step 3: Connect Signals in `users/apps.py`

Update `users/apps.py` to import the signals module when the app is ready:

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('المستخدمون')

    def ready(self):
        import users.signals  # noqa: F401
```

---

### Step 4: Register Profile Models in `users/admin.py`

Add the following admin registrations to `users/admin.py`. Append after the existing `CustomUserAdmin` class. Do NOT modify existing admin code.

```python
from .models import PatientProfile, NurseProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'wearables_enabled', 'created_at')
    list_filter = ('gender', 'wearables_enabled')
    search_fields = ('user__national_id', 'user__phone_number', 'emergency_contact')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'syndicate_number', 'rating', 'is_available', 'verification_status', 'created_at')
    list_filter = ('is_available', 'verification_status')
    search_fields = ('user__national_id', 'user__phone_number', 'syndicate_number')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)
```

---

### Step 5: Generate and Apply Migrations

Run inside the Docker container:

```bash
python manage.py makemigrations users
python manage.py migrate
```

Verify that the migration creates two new tables: `users_patient_profile` and `users_nurse_profile`.

---

### Step 6: Write Tests in `users/tests.py`

Append the following test classes to the existing `users/tests.py`. Do NOT modify existing tests.

```python
from users.models import PatientProfile, NurseProfile, UserRole


class TestPatientProfileSignal(TestCase):
    """Verify post_save signal creates PatientProfile for PATIENT users."""

    def test_patient_profile_auto_created(self):
        user = User.objects.create_user(
            national_id='29901011234800',
            phone_number='01012345800',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.assertTrue(
            PatientProfile.objects.filter(user=user).exists(),
            'PatientProfile was not auto-created for PATIENT user',
        )

    def test_nurse_does_not_get_patient_profile(self):
        user = User.objects.create_user(
            national_id='29901011234801',
            phone_number='01012345801',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        self.assertFalse(
            PatientProfile.objects.filter(user=user).exists(),
            'PatientProfile should NOT be created for NURSE user',
        )


class TestNurseProfileSignal(TestCase):
    """Verify post_save signal creates NurseProfile for NURSE users."""

    def test_nurse_profile_auto_created(self):
        user = User.objects.create_user(
            national_id='29901011234802',
            phone_number='01012345802',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        self.assertTrue(
            NurseProfile.objects.filter(user=user).exists(),
            'NurseProfile was not auto-created for NURSE user',
        )

    def test_patient_does_not_get_nurse_profile(self):
        user = User.objects.create_user(
            national_id='29901011234803',
            phone_number='01012345803',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.assertFalse(
            NurseProfile.objects.filter(user=user).exists(),
            'NurseProfile should NOT be created for PATIENT user',
        )

    def test_nurse_profile_default_values(self):
        user = User.objects.create_user(
            national_id='29901011234804',
            phone_number='01012345804',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        profile = NurseProfile.objects.get(user=user)
        self.assertEqual(profile.rating, 5.00)
        self.assertFalse(profile.is_available)
        self.assertEqual(profile.verification_status, 'PENDING')
        self.assertEqual(profile.specializations, [])


class TestProfileModelStr(TestCase):
    """Verify __str__ representations of profile models."""

    def test_patient_profile_str(self):
        user = User.objects.create_user(
            national_id='29901011234805',
            phone_number='01012345805',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        profile = PatientProfile.objects.get(user=user)
        self.assertEqual(str(profile), 'PatientProfile(29901011234805)')

    def test_nurse_profile_str(self):
        user = User.objects.create_user(
            national_id='29901011234806',
            phone_number='01012345806',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        profile = NurseProfile.objects.get(user=user)
        self.assertEqual(str(profile), 'NurseProfile(29901011234806)')
```

---

## Verification Checklist

Run each command inside the Docker container (`docker exec -it wateen_web bash`):

1. **Migrations exist:**

   ```bash
   python manage.py showmigrations users
   ```

   Expect to see a new migration file (e.g., `0002_patientprofile_nurseprofile`).

2. **All tests pass:**

   ```bash
   python manage.py test users -v2
   ```

   All existing + new tests must pass with 0 failures.

3. **Admin site accessible:**
   Navigate to `/admin/` and confirm `PatientProfile` and `NurseProfile` are listed under the Users section.

---

## Files Modified

| File                | Action | Description                                                                 |
| ------------------- | ------ | --------------------------------------------------------------------------- |
| `users/models.py`   | MODIFY | Add `PatientProfile`, `NurseProfile`, `VerificationStatus`, `GenderChoices` |
| `users/signals.py`  | MODIFY | Implement `create_user_profile` post_save signal                            |
| `users/apps.py`     | MODIFY | Add `ready()` method to import signals                                      |
| `users/admin.py`    | MODIFY | Register `PatientProfileAdmin`, `NurseProfileAdmin`                         |
| `users/tests.py`    | MODIFY | Add signal & model tests                                                    |
| `users/migrations/` | NEW    | Auto-generated migration file                                               |

---

## Constraints

- **DO NOT** modify any existing model, admin, or test code — only append new code.
- **DO NOT** rename existing database tables.
- Use `primary_key=True` on the `user` OneToOneField (shares PK with CustomUser UUID).
- All `PointField` must use `geography=True, srid=4326`.
- Use `get_or_create` in signals for idempotency.
- Follow the established Arabic verbose_name pattern from `CustomUser`.
