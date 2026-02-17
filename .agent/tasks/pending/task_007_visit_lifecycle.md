---
ticket: "2.1"
title: "Visit Model & State Machine Logic"
priority: high
depends_on: "1.4 (Profiles Architecture – COMPLETED)"
estimated_complexity: medium-high
---

# Ticket 2.1 — Visit Model & State Machine Logic

## Task Identification

- **Task ID:** TASK-007
- **Task Name:** Visit Lifecycle — Model, State Machine, Service Layer, API
- **Status:** Pending
- **Assigned Execution Agent:** OpenCode
- **Assigned Review Authority:** Kilo Code

---

## 1) Context & Objective

Implement the core Visit lifecycle for the Wateen home-nursing platform. A patient requests a visit by providing their GPS coordinates and desired service type. The system creates a `Visit` record in `PENDING` status. The visit then progresses through a strict finite-state-machine (`PENDING → MATCHED → ACCEPTED → ON_WAY → ARRIVED → IN_PROGRESS → COMPLETED`), with `CANCELLED` available from any non-terminal state.

**Functional Goal:** Allow patients to request nursing visits via a REST API endpoint, creating geographically-aware visit records with strict status lifecycle enforcement.

**Technical Problem:** Django lacks built-in state machine support. We must implement a `transition_to()` method that validates transitions against an explicit allowed-transitions map and raises `ValidationError` on illegal moves.

**System Behavior After Completion:**

- `POST /api/v1/visits/request/` creates a Visit with `PENDING` status and a PostGIS `PointField` location
- Calling `visit.transition_to('COMPLETED')` from `PENDING` raises `ValidationError`
- Calling `visit.transition_to('MATCHED')` from `PENDING` succeeds

---

## 2) Technical Specifications

### Target Files

| File                    | Status     | Responsibility                                 |
| ----------------------- | ---------- | ---------------------------------------------- |
| `visits/__init__.py`    | **NEW**    | Package init                                   |
| `visits/apps.py`        | **NEW**    | Django AppConfig                               |
| `visits/models.py`      | **NEW**    | Visit model + VisitStatus enum + state machine |
| `visits/services.py`    | **NEW**    | Business logic (create_visit_request)          |
| `visits/serializers.py` | **NEW**    | DRF input/output serializers                   |
| `visits/views.py`       | **NEW**    | Thin API view (auth + delegation)              |
| `visits/urls.py`        | **NEW**    | URL routing for visits endpoints               |
| `visits/admin.py`       | **NEW**    | Admin registration                             |
| `visits/tests.py`       | **NEW**    | Comprehensive test suite                       |
| `config/settings.py`    | **MODIFY** | Add `'visits'` to INSTALLED_APPS               |
| `config/urls.py`        | **MODIFY** | Add visits URL include                         |

### Architecture Rules

- **Strict Modular Monolith:** Business logic MUST live in `models.py` (state machine) and `services.py` (visit creation). Views MUST be thin — only authentication checks and delegation.
- **No business logic in views or serializers.**
- **ForeignKey references** use string notation: `'users.PatientProfile'`, `'users.NurseProfile'`.
- **All verbose_name strings** MUST use Egyptian Arabic with `gettext_lazy as _` (project convention).
- **UUID primary key** for the Visit model (matches CustomUser pattern).
- **PointField** MUST use `geography=True, srid=4326` (matches PatientProfile.home_location and NurseProfile.last_location).

### Technology Stack

- **Backend:** Django 5.2, Django REST Framework
- **Database:** PostgreSQL 16 + PostGIS 3.4 (via `django.contrib.gis`)
- **Auth:** JWT (SimpleJWT) — already configured
- **Container:** Docker (postgis/postgis:16-3.4)

---

## 3) Implementation Steps

### Step 1 — Create `visits` app directory structure

Create the following files:

**`visits/__init__.py`** — Empty file.

**`visits/apps.py`:**

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VisitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visits'
    verbose_name = _('الزيارات')
```

---

### Step 2 — Create `visits/models.py`

```python
import uuid

from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class VisitStatus(models.TextChoices):
    PENDING = 'PENDING', _('قيد الانتظار')
    MATCHED = 'MATCHED', _('تم المطابقة')
    ACCEPTED = 'ACCEPTED', _('مقبولة')
    ON_WAY = 'ON_WAY', _('في الطريق')
    ARRIVED = 'ARRIVED', _('وصل')
    IN_PROGRESS = 'IN_PROGRESS', _('جارية')
    COMPLETED = 'COMPLETED', _('مكتملة')
    CANCELLED = 'CANCELLED', _('ملغاة')


# Explicit allowed transitions map
ALLOWED_TRANSITIONS = {
    VisitStatus.PENDING: [VisitStatus.MATCHED, VisitStatus.CANCELLED],
    VisitStatus.MATCHED: [VisitStatus.ACCEPTED, VisitStatus.CANCELLED],
    VisitStatus.ACCEPTED: [VisitStatus.ON_WAY, VisitStatus.CANCELLED],
    VisitStatus.ON_WAY: [VisitStatus.ARRIVED, VisitStatus.CANCELLED],
    VisitStatus.ARRIVED: [VisitStatus.IN_PROGRESS, VisitStatus.CANCELLED],
    VisitStatus.IN_PROGRESS: [VisitStatus.COMPLETED, VisitStatus.CANCELLED],
    VisitStatus.COMPLETED: [],  # Terminal state
    VisitStatus.CANCELLED: [],  # Terminal state
}


class Visit(models.Model):
    """Represents a single home-nursing visit request and its lifecycle."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('المعرّف'),
    )
    patient = models.ForeignKey(
        'users.PatientProfile',
        on_delete=models.CASCADE,
        related_name='visits',
        verbose_name=_('المريض'),
    )
    nurse = models.ForeignKey(
        'users.NurseProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
        verbose_name=_('الممرض/ة'),
    )
    status = models.CharField(
        _('الحالة'),
        max_length=15,
        choices=VisitStatus.choices,
        default=VisitStatus.PENDING,
        db_index=True,
    )
    location = gis_models.PointField(
        _('موقع الزيارة'),
        geography=True,
        srid=4326,
        help_text=_('الموقع الجغرافي للمريض عند طلب الزيارة'),
    )
    service_type = models.CharField(
        _('نوع الخدمة'),
        max_length=50,
        blank=True,
        default='',
        help_text=_('نوع الخدمة التمريضية المطلوبة'),
    )
    created_at = models.DateTimeField(
        _('تاريخ الإنشاء'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _('تاريخ التحديث'),
        auto_now=True,
    )

    class Meta:
        verbose_name = _('زيارة')
        verbose_name_plural = _('الزيارات')
        db_table = 'visits_visit'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Visit({self.id!s:.8}—{self.status})'

    def transition_to(self, new_status: str) -> None:
        """
        Transition the visit to a new status.

        Validates the transition against the ALLOWED_TRANSITIONS map.
        Raises ValidationError if the transition is not allowed.
        Saves the model after a successful transition.
        """
        if new_status not in VisitStatus.values:
            raise ValidationError(
                _('الحالة "%(status)s" غير صالحة.'),
                code='invalid_status',
                params={'status': new_status},
            )

        allowed = ALLOWED_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValidationError(
                _('لا يمكن الانتقال من "%(current)s" إلى "%(new)s".'),
                code='invalid_transition',
                params={'current': self.status, 'new': new_status},
            )

        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
```

---

### Step 3 — Create `visits/services.py`

```python
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Visit, VisitStatus


def create_visit_request(patient_profile, latitude: float, longitude: float, service_type: str = '') -> Visit:
    """
    Create a new Visit request for a patient.

    Args:
        patient_profile: PatientProfile instance of the requesting patient.
        latitude: Latitude of the patient's location (-90 to 90).
        longitude: Longitude of the patient's location (-180 to 180).
        service_type: Type of nursing service requested.

    Returns:
        Visit instance with status PENDING.

    Raises:
        ValidationError: If coordinates are out of valid range.
    """
    if not (-90 <= latitude <= 90):
        raise ValidationError(
            _('خط العرض يجب أن يكون بين -90 و 90.'),
            code='invalid_latitude',
        )
    if not (-180 <= longitude <= 180):
        raise ValidationError(
            _('خط الطول يجب أن يكون بين -180 و 180.'),
            code='invalid_longitude',
        )

    location = Point(longitude, latitude, srid=4326)

    visit = Visit.objects.create(
        patient=patient_profile,
        status=VisitStatus.PENDING,
        location=location,
        service_type=service_type,
    )
    return visit
```

---

### Step 4 — Create `visits/serializers.py`

```python
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class VisitRequestSerializer(serializers.Serializer):
    """Input serializer for creating a visit request."""

    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
        help_text=_('خط العرض'),
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
        help_text=_('خط الطول'),
    )
    service_type = serializers.CharField(
        max_length=50,
        required=False,
        default='',
        help_text=_('نوع الخدمة'),
    )


class VisitResponseSerializer(serializers.Serializer):
    """Output serializer for visit data."""

    id = serializers.UUIDField(read_only=True)
    status = serializers.CharField(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    service_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def get_latitude(self, obj) -> float:
        return obj.location.y if obj.location else None

    def get_longitude(self, obj) -> float:
        return obj.location.x if obj.location else None
```

---

### Step 5 — Create `visits/views.py`

```python
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

from users.models import UserRole
from .serializers import VisitRequestSerializer, VisitResponseSerializer
from .services import create_visit_request


class VisitRequestView(APIView):
    """
    POST /api/v1/visits/request/

    Creates a new visit request for an authenticated patient.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check that the user is a patient
        if request.user.role != UserRole.PATIENT:
            return Response(
                {'detail': _('فقط المرضى يمكنهم طلب زيارة.')},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = VisitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get patient profile
        try:
            patient_profile = request.user.patient_profile
        except Exception:
            return Response(
                {'detail': _('لم يتم العثور على ملف المريض.')},
                status=status.HTTP_404_NOT_FOUND,
            )

        visit = create_visit_request(
            patient_profile=patient_profile,
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            service_type=serializer.validated_data.get('service_type', ''),
        )

        response_serializer = VisitResponseSerializer(visit)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
```

---

### Step 6 — Create `visits/urls.py`

```python
from django.urls import path

from .views import VisitRequestView

app_name = 'visits'

urlpatterns = [
    path('request/', VisitRequestView.as_view(), name='visit_request'),
]
```

---

### Step 7 — Create `visits/admin.py`

```python
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'nurse', 'status', 'service_type', 'created_at')
    list_filter = ('status', 'service_type')
    search_fields = ('patient__user__national_id', 'nurse__user__national_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    raw_id_fields = ('patient', 'nurse')
    ordering = ('-created_at',)
```

---

### Step 8 — Register `visits` app in `config/settings.py`

Add `'visits'` to the `INSTALLED_APPS` list, after `'users'`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'users',
    'visits',
]
```

---

### Step 9 — Add visits URL include in `config/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),
    path('api/v1/visits/', include('visits.urls')),
]
```

---

### Step 10 — Create `visits/tests.py`

```python
import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from rest_framework import status as http_status

from users.models import UserRole, PatientProfile, NurseProfile
from .models import Visit, VisitStatus, ALLOWED_TRANSITIONS
from .services import create_visit_request

User = get_user_model()


class TestVisitStatusTransitions(TestCase):
    """Test the state machine logic in Visit.transition_to()."""

    def setUp(self):
        self.user = User.objects.create_user(
            national_id='29901011234900',
            phone_number='01012345900',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.patient = PatientProfile.objects.get(user=self.user)
        self.visit = Visit.objects.create(
            patient=self.patient,
            status=VisitStatus.PENDING,
            location=Point(31.2357, 30.0444, srid=4326),
            service_type='general_nursing',
        )

    def test_valid_transition_pending_to_matched(self):
        self.visit.transition_to(VisitStatus.MATCHED)
        self.visit.refresh_from_db()
        self.assertEqual(self.visit.status, VisitStatus.MATCHED)

    def test_valid_transition_pending_to_cancelled(self):
        self.visit.transition_to(VisitStatus.CANCELLED)
        self.visit.refresh_from_db()
        self.assertEqual(self.visit.status, VisitStatus.CANCELLED)

    def test_valid_full_happy_path(self):
        """Test the complete happy-path lifecycle."""
        transitions = [
            VisitStatus.MATCHED,
            VisitStatus.ACCEPTED,
            VisitStatus.ON_WAY,
            VisitStatus.ARRIVED,
            VisitStatus.IN_PROGRESS,
            VisitStatus.COMPLETED,
        ]
        for new_status in transitions:
            self.visit.transition_to(new_status)
            self.visit.refresh_from_db()
            self.assertEqual(self.visit.status, new_status)

    def test_invalid_transition_pending_to_completed(self):
        with self.assertRaises(ValidationError) as ctx:
            self.visit.transition_to(VisitStatus.COMPLETED)
        self.assertEqual(ctx.exception.code, 'invalid_transition')

    def test_invalid_transition_pending_to_in_progress(self):
        with self.assertRaises(ValidationError):
            self.visit.transition_to(VisitStatus.IN_PROGRESS)

    def test_invalid_transition_from_completed(self):
        self.visit.status = VisitStatus.COMPLETED
        self.visit.save()
        with self.assertRaises(ValidationError):
            self.visit.transition_to(VisitStatus.PENDING)

    def test_invalid_transition_from_cancelled(self):
        self.visit.status = VisitStatus.CANCELLED
        self.visit.save()
        with self.assertRaises(ValidationError):
            self.visit.transition_to(VisitStatus.PENDING)

    def test_invalid_status_value(self):
        with self.assertRaises(ValidationError) as ctx:
            self.visit.transition_to('NONEXISTENT')
        self.assertEqual(ctx.exception.code, 'invalid_status')

    def test_all_transitions_in_map(self):
        """Verify every VisitStatus value has an entry in ALLOWED_TRANSITIONS."""
        for status_value in VisitStatus.values:
            self.assertIn(status_value, ALLOWED_TRANSITIONS)


class TestCreateVisitRequestService(TestCase):
    """Test the create_visit_request service function."""

    def setUp(self):
        self.user = User.objects.create_user(
            national_id='29901011234901',
            phone_number='01012345901',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.patient = PatientProfile.objects.get(user=self.user)

    def test_create_visit_success(self):
        visit = create_visit_request(
            patient_profile=self.patient,
            latitude=30.0444,
            longitude=31.2357,
            service_type='general_nursing',
        )
        self.assertEqual(visit.status, VisitStatus.PENDING)
        self.assertEqual(visit.patient, self.patient)
        self.assertIsNone(visit.nurse)
        self.assertAlmostEqual(visit.location.y, 30.0444, places=4)
        self.assertAlmostEqual(visit.location.x, 31.2357, places=4)
        self.assertEqual(visit.service_type, 'general_nursing')
        self.assertIsInstance(visit.id, uuid.UUID)

    def test_create_visit_invalid_latitude(self):
        with self.assertRaises(ValidationError) as ctx:
            create_visit_request(
                patient_profile=self.patient,
                latitude=91.0,
                longitude=31.2357,
            )
        self.assertEqual(ctx.exception.code, 'invalid_latitude')

    def test_create_visit_invalid_longitude(self):
        with self.assertRaises(ValidationError) as ctx:
            create_visit_request(
                patient_profile=self.patient,
                latitude=30.0444,
                longitude=181.0,
            )
        self.assertEqual(ctx.exception.code, 'invalid_longitude')

    def test_create_visit_default_service_type(self):
        visit = create_visit_request(
            patient_profile=self.patient,
            latitude=30.0444,
            longitude=31.2357,
        )
        self.assertEqual(visit.service_type, '')


class TestVisitRequestAPI(TestCase):
    """Test the POST /api/v1/visits/request/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        # Create patient user
        self.patient_user = User.objects.create_user(
            national_id='29901011234902',
            phone_number='01012345902',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        # Create nurse user
        self.nurse_user = User.objects.create_user(
            national_id='29901011234903',
            phone_number='01012345903',
            password='TestPass123!',
            role=UserRole.NURSE,
        )
        # Get patient token
        token_resp = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234902',
            'password': 'TestPass123!',
        }, format='json')
        self.patient_token = token_resp.data['access']

        # Get nurse token
        nurse_token_resp = self.client.post('/api/v1/auth/token/', {
            'national_id': '29901011234903',
            'password': 'TestPass123!',
        }, format='json')
        self.nurse_token = nurse_token_resp.data['access']

    def test_create_visit_request_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.post('/api/v1/visits/request/', {
            'latitude': 30.0444,
            'longitude': 31.2357,
            'service_type': 'general_nursing',
        }, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertAlmostEqual(response.data['latitude'], 30.0444, places=4)
        self.assertAlmostEqual(response.data['longitude'], 31.2357, places=4)
        self.assertIn('id', response.data)

    def test_create_visit_unauthenticated(self):
        response = self.client.post('/api/v1/visits/request/', {
            'latitude': 30.0444,
            'longitude': 31.2357,
        }, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_401_UNAUTHORIZED)

    def test_create_visit_nurse_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.nurse_token}')
        response = self.client.post('/api/v1/visits/request/', {
            'latitude': 30.0444,
            'longitude': 31.2357,
        }, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_403_FORBIDDEN)

    def test_create_visit_invalid_latitude(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.post('/api/v1/visits/request/', {
            'latitude': 95.0,
            'longitude': 31.2357,
        }, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)

    def test_create_visit_missing_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.post('/api/v1/visits/request/', {}, format='json')
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)


class TestVisitModel(TestCase):
    """Test Visit model properties and str representation."""

    def setUp(self):
        self.user = User.objects.create_user(
            national_id='29901011234904',
            phone_number='01012345904',
            password='TestPass123!',
            role=UserRole.PATIENT,
        )
        self.patient = PatientProfile.objects.get(user=self.user)

    def test_visit_str(self):
        visit = Visit.objects.create(
            patient=self.patient,
            location=Point(31.2357, 30.0444, srid=4326),
        )
        self.assertIn('PENDING', str(visit))

    def test_visit_default_status(self):
        visit = Visit.objects.create(
            patient=self.patient,
            location=Point(31.2357, 30.0444, srid=4326),
        )
        self.assertEqual(visit.status, VisitStatus.PENDING)

    def test_visit_uuid_pk(self):
        visit = Visit.objects.create(
            patient=self.patient,
            location=Point(31.2357, 30.0444, srid=4326),
        )
        self.assertIsInstance(visit.id, uuid.UUID)

    def test_visit_nurse_nullable(self):
        visit = Visit.objects.create(
            patient=self.patient,
            location=Point(31.2357, 30.0444, srid=4326),
        )
        self.assertIsNone(visit.nurse)
```

---

### Step 11 — Generate and Apply Migrations

Run inside the Docker container:

```bash
python manage.py makemigrations visits
python manage.py migrate
```

Verify the migration creates the `visits_visit` table with all expected columns.

---

## 4) Definition of Done (DoD)

### Functional Validation

- [ ] `visits/models.py` compiles without errors
- [ ] `Visit` model has all specified fields including `PointField`
- [ ] `transition_to()` correctly enforces the state machine
- [ ] `POST /api/v1/visits/request/` returns 201 with correct payload for patient
- [ ] Endpoint returns 401 for unauthenticated, 403 for non-patient
- [ ] All tests pass: `python manage.py test visits -v2`
- [ ] Migration applied successfully

### Architectural Compliance

- [ ] Business logic is in `services.py` and `models.py` only
- [ ] Views are thin — no business logic
- [ ] Arabic verbose_name used consistently
- [ ] UUID primary key used
- [ ] PointField uses `geography=True, srid=4326`

### Standards Compliance

- [ ] All new files follow project conventions
- [ ] Imports follow existing patterns
- [ ] ForeignKey uses string references
- [ ] db_table explicitly set

---

## 5) Acceptance Authority

The Reviewer (Kilo Code) must validate:

- **Correctness:** State machine enforces all transitions properly
- **Architectural integrity:** Modular monolith rules followed
- **Stability:** All tests pass, no regressions in `users` tests
- **Maintainability:** Clean, documented, extensible code

---

## Constraints

- **DO NOT** modify any existing code in the `users` app.
- **DO NOT** add any third-party state machine libraries.
- `PointField` MUST use `geography=True, srid=4326`.
- `Visit.nurse` MUST be nullable (assigned later in the matching phase).
- Use `models.SET_NULL` for the nurse FK `on_delete`.
- Use `models.CASCADE` for the patient FK `on_delete`.
- All error messages MUST be in Egyptian Arabic.

---

## Final Directive

The execution agent must not deviate from this specification.
The reviewer must reject the task if any section is partially satisfied.
