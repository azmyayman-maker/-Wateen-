# Quickstart: Pricing Engine Remediation

**Feature**: 002-pricing-engine-remediation
**Date**: 2026-02-18

## Overview

This remediation fixes 4 critical issues in the pricing engine:
1. Dynamic distance calculation (replaces hardcoded 5.0 km)
2. Nurse availability filtering (only `is_available=True` AND `verification_status=VERIFIED`)
3. Timezone-aware pricing (Cairo timezone)
4. Non-blocking logging (`transaction.on_commit`)

## Files Changed

| File | Change |
|------|--------|
| `visits/utils.py` | NEW - Add `find_nearest_available_nurse()` |
| `visits/api.py` | Modify - Use dynamic distance |
| `visits/services/matching.py` | Modify - Add availability filter |
| `visits/services/pricing.py` | Modify - Use `timezone.now()` |
| `visits/signals.py` | Modify - Use `transaction.on_commit()` |
| `visits/tests/test_pricing.py` | Modify - Add new test cases |

## Quick Implementation

### 1. Create visits/utils.py

```python
from decimal import Decimal
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from users.models import NurseProfile, VerificationStatus


def find_nearest_available_nurse(lat: float, lng: float) -> tuple[NurseProfile | None, Decimal]:
    """
    Find the nearest available verified nurse to the given coordinates.
    
    Args:
        lat: Patient latitude
        lng: Patient longitude
    
    Returns:
        Tuple of (nurse, distance_km). Returns (None, Decimal("0")) if no nurse found.
    """
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
    
    return nurse, Decimal(str(nurse.distance.km))
```

### 2. Modify visits/api.py

Replace:
```python
distance_km = Decimal("5.0")
```

With:
```python
from visits.utils import find_nearest_available_nurse

_, distance_km = find_nearest_available_nurse(
    data["latitude"], 
    data["longitude"]
)
```

### 3. Modify visits/services/matching.py

Add availability check to `find_candidates`:
```python
from users.models import NurseProfile, VerificationStatus

# After getting nurse_ids from Redis, filter by availability:
nurse_ids = [c["nurse_id"] for c in candidates]
available_nurses = NurseProfile.objects.filter(
    id__in=nurse_ids,
    is_available=True,
    verification_status=VerificationStatus.VERIFIED
).values_list('id', flat=True)
candidates = [c for c in candidates if c["nurse_id"] in available_nurses]
```

### 4. Modify visits/services/pricing.py

Replace:
```python
if request_time is None:
    request_time = datetime.now()
```

With:
```python
from django.utils import timezone

if request_time is None:
    request_time = timezone.localtime(timezone.now())
```

### 5. Modify visits/signals.py

Replace:
```python
EstimateLog.objects.create(...)
```

With:
```python
from django.db import transaction

def do_log():
    EstimateLog.objects.create(
        request_time=request_time,
        location=Point(longitude, latitude, srid=4326),
        service_type=service_type,
        price_components=price_components,
        ip_address=ip_address,
    )

transaction.on_commit(do_log)
```

## Testing

Run tests after implementation:
```bash
cd src && pytest visits/tests/test_pricing.py -v
```

## Verification Checklist

- [ ] No `5.0` hardcoded distance in codebase
- [ ] `is_available=True` filter applied in nurse queries
- [ ] `verification_status=VERIFIED` filter applied in nurse queries
- [ ] `timezone.now()` used instead of `datetime.now()`
- [ ] `transaction.on_commit()` wraps logging
- [ ] All tests pass
