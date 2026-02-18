# Research: Pricing Engine Remediation

**Date**: 2026-02-18
**Feature**: 002-pricing-engine-remediation

## Research Tasks

### 1. PostGIS Spatial Queries for Distance Calculation

**Decision**: Use Django's `django.contrib.gis.db.models.functions.Distance` with PostGIS geography lookups.

**Rationale**: 
- Project already uses PostGIS (django.contrib.gis)
- `Distance` function calculates accurate geodetic distance in meters
- Geography type accounts for Earth's curvature
- More accurate than haversine formula for distance-based queries

**Alternatives Considered**:
- Haversine formula in Python (existing implementation in `pricing.py`) - less efficient for database queries
- Redis GEO commands (already used in `matching.py`) - doesn't filter by availability/verification status in DB

**Implementation Pattern**:
```python
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

def find_nearest_available_nurse(lat: float, lng: float) -> NurseProfile | None:
    point = Point(lng, lat, srid=4326)
    return NurseProfile.objects.filter(
        is_available=True,
        verification_status='VERIFIED',
        last_location__isnull=False
    ).annotate(
        distance=Distance('last_location', point)
    ).order_by('distance').first()
```

### 2. Django Timezone Handling

**Decision**: Use `django.utils.timezone.now()` and `timezone.localtime()` with `pytz.timezone('Africa/Cairo')`.

**Rationale**:
- Django's `timezone.now()` returns timezone-aware datetime when `USE_TZ=True`
- `timezone.localtime()` converts to configured timezone (should be Cairo)
- Avoids naive datetime issues that cause incorrect pricing

**Alternatives Considered**:
- `datetime.now()` - returns naive datetime (current bug)
- `datetime.utcnow()` - still naive, requires manual timezone conversion

**Implementation Pattern**:
```python
from django.utils import timezone
from pytz import timezone as pytz_tz

CAIRO_TZ = pytz_tz('Africa/Cairo')

def get_current_time_in_cairo():
    return timezone.localtime(timezone.now(), CAIRO_TZ)
```

### 3. Transaction.on_commit for Async Logging

**Decision**: Use `django.db.transaction.on_commit()` to defer logging until after transaction commits.

**Rationale**:
- Ensures logging doesn't block the response
- Guarantees logging only happens if transaction succeeds
- Simpler than Celery for this use case (no additional infrastructure)

**Alternatives Considered**:
- Celery task - overkill for simple logging, requires broker
- Threading - doesn't guarantee execution if process dies
- Signals (post_save) - still synchronous

**Implementation Pattern**:
```python
from django.db import transaction

def log_estimate_request(...):
    def do_log():
        EstimateLog.objects.create(...)
    
    transaction.on_commit(do_log)
```

### 4. NurseProfile Filtering

**Decision**: Filter by `is_available=True` AND `verification_status='VERIFIED'` in all nurse lookup queries.

**Rationale**:
- Existing `NurseProfile` model has both fields
- `verification_status` uses `VerificationStatus.VERIFIED` enum
- Both conditions required for nurse to be dispatchable

**Implementation Pattern**:
```python
from users.models import NurseProfile, VerificationStatus

NurseProfile.objects.filter(
    is_available=True,
    verification_status=VerificationStatus.VERIFIED,
    last_location__isnull=False
)
```

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Django | 5.2 | Framework |
| django.contrib.gis | Built-in | PostGIS integration |
| pytz | Latest | Cairo timezone handling |
| psycopg2 | Latest | PostgreSQL adapter |

## No NEEDS CLARIFICATION Items

All technical decisions resolved based on existing codebase analysis.
