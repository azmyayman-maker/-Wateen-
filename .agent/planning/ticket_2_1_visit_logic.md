# Ticket 2.1 — Visit Model & State Machine Logic

## Objective

Create a new `visits` Django app implementing the Visit model with a geographic `PointField`, a strict finite-state-machine for visit status transitions, a service layer for business logic, and a DRF API endpoint (`POST /api/v1/visits/request/`) to create new visit requests.

---

## Prerequisites (Already Verified)

- `CustomUser`, `PatientProfile`, `NurseProfile` exist in `users/models.py`
- PostGIS configured: `django.contrib.gis` in `INSTALLED_APPS`, DB engine `postgis`
- Docker image `postgis/postgis:16-3.4`
- DRF + JWT auth configured in `config/settings.py`
- URL routing uses `api/v1/` prefix in `config/urls.py`

---

## Proposed Changes

### Visits App (NEW)

#### [NEW] `visits/__init__.py`

Empty init file.

#### [NEW] `visits/apps.py`

Standard Django AppConfig with `name = 'visits'`.

#### [NEW] `visits/models.py`

- **`VisitStatus`** — `TextChoices` enum: `PENDING`, `MATCHED`, `ACCEPTED`, `ON_WAY`, `ARRIVED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`.
- **`Visit`** model:
  - `id`: UUID PK (matches project convention)
  - `patient`: FK → `users.PatientProfile` (not nullable)
  - `nurse`: FK → `users.NurseProfile` (nullable)
  - `status`: CharField with `VisitStatus` choices, default `PENDING`
  - `location`: `PointField(geography=True, srid=4326)` — patient's location
  - `service_type`: CharField (future-extensible)
  - `created_at`: DateTimeField (auto_now_add)
  - `updated_at`: DateTimeField (auto_now)
  - **`transition_to(new_status)`** method with strict allowed-transitions map; raises `ValidationError` on invalid transition

**State Transition Map:**

```
PENDING    → MATCHED, CANCELLED
MATCHED    → ACCEPTED, CANCELLED
ACCEPTED   → ON_WAY, CANCELLED
ON_WAY     → ARRIVED, CANCELLED
ARRIVED    → IN_PROGRESS, CANCELLED
IN_PROGRESS→ COMPLETED, CANCELLED
COMPLETED  → (terminal)
CANCELLED  → (terminal)
```

#### [NEW] `visits/services.py`

- `create_visit_request(patient_profile, latitude, longitude, service_type)` — Creates a Visit with status `PENDING`, constructs the `Point` from lat/lng. Returns the Visit instance. Raises `ValidationError` if inputs are invalid.

#### [NEW] `visits/serializers.py`

- `VisitRequestSerializer` — Input: `latitude` (float), `longitude` (float), `service_type` (string). Validates coordinate ranges.
- `VisitResponseSerializer` — Output: `id`, `status`, `location` (lat/lng), `service_type`, `created_at`.

#### [NEW] `visits/views.py`

- `VisitRequestView` (DRF `APIView`) — `POST` handler. Requires authentication + Patient role. Delegates to `services.create_visit_request()`.

#### [NEW] `visits/urls.py`

- Route: `request/` → `VisitRequestView`

#### [NEW] `visits/admin.py`

- Register `Visit` model with list_display, list_filter, search_fields.

#### [NEW] `visits/tests.py`

- Test valid state transitions
- Test invalid state transitions raise `ValidationError`
- Test `create_visit_request` service
- Test API endpoint (auth, patient-only, invalid inputs)

---

### Config Changes

#### [MODIFY] `config/settings.py`

- Add `'visits'` to `INSTALLED_APPS`

#### [MODIFY] `config/urls.py`

- Add `path('api/v1/visits/', include('visits.urls'))`

---

## Architecture Compliance

- Business logic lives in `visits/services.py` and `visits/models.py` (state machine)
- Views are thin — only auth checks + delegation to service layer
- No business logic in serializers or views
- All fields use Arabic `verbose_name` with `gettext_lazy` (project convention)
- UUID primary key (matches `CustomUser` pattern)
- PointField uses `geography=True, srid=4326` (matches existing usage)

---

## Verification Plan

### Automated Tests (inside Docker)

```bash
docker exec -it wateen_web python manage.py test visits -v2
```

### Migration Verification

```bash
docker exec -it wateen_web python manage.py showmigrations visits
docker exec -it wateen_web python manage.py migrate
```

### Database Schema Verification (Postgres MCP)

After execution, Antigravity will use the Postgres MCP to:

1. List tables → confirm `visits_visit` exists
2. Inspect schema → confirm all columns including the geography `location` column
3. Verify foreign key constraints to `users_patient_profile` and `users_nurse_profile`
