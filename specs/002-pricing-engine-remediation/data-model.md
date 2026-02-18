# Data Model: Pricing Engine Remediation

**Date**: 2026-02-18
**Feature**: 002-pricing-engine-remediation

## Existing Entities (No Changes)

### NurseProfile (users/models.py)

No schema changes. Uses existing fields for filtering:

| Field | Type | Purpose |
|-------|------|---------|
| `is_available` | Boolean | Filter for available nurses |
| `verification_status` | Enum (VERIFIED, PENDING, REJECTED) | Filter for verified nurses |
| `last_location` | PointField (geography, srid=4326) | GPS coordinates for distance calculation |

**Query Pattern**:
```python
NurseProfile.objects.filter(
    is_available=True,
    verification_status=VerificationStatus.VERIFIED,
    last_location__isnull=False
)
```

### ServiceType (visits/models.py)

No changes. Used as-is for base price lookup.

### EstimateLog (visits/models.py)

No schema changes. Behavior change only (async creation via transaction.on_commit).

## New Functions

### find_nearest_available_nurse (visits/utils.py)

**Signature**:
```python
def find_nearest_available_nurse(lat: float, lng: float) -> tuple[NurseProfile | None, Decimal]
```

**Returns**:
- `(nurse, distance_km)` - nearest available verified nurse and distance in km
- `(None, Decimal("0"))` - if no nurse found

**Query**:
```python
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from decimal import Decimal

def find_nearest_available_nurse(lat: float, lng: float) -> tuple[NurseProfile | None, Decimal]:
    point = Point(lng, lat, srid=4326)
    
    nurse = NurseProfile.objects.filter(
        is_available=True,
        verification_status=VerificationStatus.VERIFIED,
        last_location__isnull=False
    ).annotate(
        distance=Distance('last_location', point)
    ).order_by('distance').first()
    
    if nurse is None:
        return None, Decimal("0")
    
    distance_km = Decimal(str(nurse.distance.km))
    return nurse, distance_km
```

## Modified Functions

### is_night_hours (visits/services/pricing.py)

**Change**: Replace `datetime.now()` with `timezone.now()` converted to Cairo timezone.

**Before**:
```python
if request_time is None:
    request_time = datetime.now()
```

**After**:
```python
from django.utils import timezone

if request_time is None:
    request_time = timezone.localtime(timezone.now())
```

### log_estimate_request (visits/signals.py)

**Change**: Wrap database creation in `transaction.on_commit()`.

**Before**:
```python
EstimateLog.objects.create(...)
```

**After**:
```python
from django.db import transaction

def do_log():
    EstimateLog.objects.create(...)

transaction.on_commit(do_log)
```

## State Transitions

No state transitions in this remediation. All changes are to query/calculation logic.

## Validation Rules

| Rule | Entity | Enforcement |
|------|--------|-------------|
| Nurse must be available | NurseProfile | `is_available=True` filter |
| Nurse must be verified | NurseProfile | `verification_status='VERIFIED'` filter |
| Nurse must have location | NurseProfile | `last_location__isnull=False` filter |
| Timezone-aware datetime | Pricing | Use `timezone.now()` not `datetime.now()` |
| Non-blocking logging | EstimateLog | Use `transaction.on_commit()` |
