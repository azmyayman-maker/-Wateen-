# Task Identification

- **Task ID:** TASK-009
- **Task Name:** Ticket 2.3 — Geospatial Matching Engine
- **Status:** Pending
- **Assigned Execution Agent:** OpenCode
- **Assigned Review Authority:** Kilo Code

---

## 1) Context & Objective

Wateen's dispatching system needs to find nearby nurses in real-time when a patient requests a visit. This requires a geospatial service using Redis `GEOADD`/`GEOSEARCH`/`GEOPOS` commands for sub-millisecond nurse proximity lookups.

The existing `visits/services.py` handles visit creation. This task introduces a **`GeoMatchingService`** class in a new `visits/services/matching.py` module, converting the existing single-file `services.py` into a package.

After completion, the system will:

- Store and update nurse GPS coordinates in a Redis geospatial index
- Find nearby nurses within a configurable radius (default 5km)
- Query individual nurse locations
- Expire inactive nurse locations after 1 hour
- Handle Redis connection failures gracefully without crashing

---

## 2) Technical Specifications

### Target Files

| File                             | Action | Responsibility                               |
| -------------------------------- | ------ | -------------------------------------------- |
| `requirements/base.txt`          | MODIFY | Add `django-redis==5.4.0`                    |
| `requirements/dev.txt`           | MODIFY | Add `fakeredis[lua]==2.21.0`                 |
| `config/settings.py`             | MODIFY | Add `CACHES` configuration with django-redis |
| `visits/services.py`             | DELETE | Replaced by package structure                |
| `visits/services/__init__.py`    | NEW    | Re-export `create_visit_request`             |
| `visits/services/matching.py`    | NEW    | `GeoMatchingService` class                   |
| `visits/services/visit.py`       | NEW    | Move existing `create_visit_request` here    |
| `tests/test_matching_service.py` | NEW    | Pytest tests with `fakeredis`                |

### Architecture Rules

- Service lives in the `visits` app (closest to dispatch domain)
- Service class must NOT import Django models — it is Redis-only
- All methods must have strict type hints (PEP 484 / 604)
- All Redis errors must be caught and logged, never raised to caller
- Key naming convention: `nurse_geo:active_nurses`
- The existing `create_visit_request` import path must remain backward compatible

### Technology Stack

| Component      | Version                        |
| -------------- | ------------------------------ |
| Python         | 3.11                           |
| Django         | 5.0.2                          |
| redis (Python) | 5.0.1 (already installed)      |
| django-redis   | 5.4.0 (NEW)                    |
| fakeredis      | 2.21.0 (NEW, dev only)         |
| Redis Server   | 7 (Alpine) — already in Docker |

---

## 3) Implementation Steps

### Step 1 — Add Dependencies

**1a.** Add to `requirements/base.txt` under the "Cache & Message Broker" section, after `redis==5.0.1`:

```
# Django cache backend for Redis
django-redis==5.4.0
```

**1b.** Add to `requirements/dev.txt` under the "Testing" section:

```
# Fake Redis for testing geospatial operations
fakeredis[lua]==2.21.0
```

---

### Step 2 — Configure Django Cache in `config/settings.py`

Add the following `CACHES` configuration block after the `CHANNEL_LAYERS` block (after line 96):

```python
# Cache configuration (Redis backend via django-redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{os.environ.get("REDIS_HOST", "redis")}:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'wateen',
    },
}
```

> **NOTE:** This uses Redis database `1` (not `0` which is used by `CHANNEL_LAYERS`). This isolates cache data from channel layer data.

---

### Step 3 — Convert `visits/services.py` to a Package

**3a.** Create directory `visits/services/`

**3b.** Create `visits/services/visit.py` with the exact contents of the current `visits/services.py`:

```python
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from visits.models import Visit, VisitStatus


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

> **CRITICAL:** The import path changes from `from .models import Visit, VisitStatus` to `from visits.models import Visit, VisitStatus` (absolute import, since it's now inside a sub-package).

**3c.** Create `visits/services/__init__.py` to maintain backward compatibility:

```python
"""
Services package for the visits app.

Re-exports all service functions for backward compatibility.
"""

from visits.services.visit import create_visit_request

__all__ = ['create_visit_request']
```

**3d.** Delete the file `visits/services.py`.

> **VERIFICATION:** After this step, the existing import `from .services import create_visit_request` in any file (e.g., `visits/views.py`) must continue to work. Verify by checking `visits/views.py` for any imports from `services`.

---

### Step 4 — Create `visits/services/matching.py`

Create the `GeoMatchingService` class:

```python
"""
Geospatial matching service for nurse proximity lookups.

Uses Redis GEOADD/GEOSEARCH/GEOPOS for sub-millisecond geospatial queries.
This is the core engine that powers the nurse dispatching system.
"""

from __future__ import annotations

import logging
from typing import Any

import redis
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

# Redis key for the geospatial sorted set
GEO_KEY: str = 'nurse_geo:active_nurses'

# Default TTL for nurse location data (seconds)
LOCATION_TTL_SECONDS: int = 3600  # 1 hour


class GeoMatchingService:
    """
    Service for managing nurse geospatial data in Redis.

    Provides methods to store, query, and manage nurse GPS coordinates
    using Redis geospatial commands (GEOADD, GEOSEARCH, GEOPOS, ZREM).

    All methods handle Redis connection errors gracefully — failures are
    logged but never raised to the caller.
    """

    def __init__(self) -> None:
        """Initialize the service with a raw Redis connection."""
        try:
            self._redis: redis.Redis = get_redis_connection('default')
        except Exception:
            logger.exception('Failed to establish Redis connection for GeoMatchingService')
            self._redis = None  # type: ignore[assignment]

    def _is_available(self) -> bool:
        """Check if Redis connection is available."""
        return self._redis is not None

    def update_nurse_location(self, nurse_id: int, lat: float, lng: float) -> bool:
        """
        Store or update a nurse's GPS coordinates in the geospatial index.

        Uses GEOADD to insert/update the nurse's position, then refreshes
        the TTL on the geo key to auto-expire inactive data.

        Args:
            nurse_id: Unique identifier of the nurse.
            lat: Latitude (-90 to 90).
            lng: Longitude (-180 to 180).

        Returns:
            True if the location was stored successfully, False otherwise.
        """
        if not self._is_available():
            return False

        try:
            member: str = f'nurse:{nurse_id}'
            self._redis.geoadd(GEO_KEY, (lng, lat, member))
            self._redis.expire(GEO_KEY, LOCATION_TTL_SECONDS)
            logger.debug(
                'Updated location for nurse %s: lat=%.6f, lng=%.6f',
                nurse_id, lat, lng,
            )
            return True
        except (redis.ConnectionError, redis.TimeoutError):
            logger.exception('Redis error updating nurse %s location', nurse_id)
            return False

    def find_candidates(
        self,
        patient_lat: float,
        patient_lng: float,
        radius_km: float = 5.0,
    ) -> list[dict[str, Any]]:
        """
        Find nurse IDs within a given radius of the patient's location.

        Uses Redis GEOSEARCH to perform a radius search, returning results
        sorted by distance (ascending).

        Args:
            patient_lat: Patient's latitude.
            patient_lng: Patient's longitude.
            radius_km: Search radius in kilometers (default: 5.0).

        Returns:
            List of dicts with keys 'nurse_id' (int) and 'distance_km' (float),
            sorted by distance ascending. Empty list on error or no results.
        """
        if not self._is_available():
            return []

        try:
            results = self._redis.geosearch(
                name=GEO_KEY,
                longitude=patient_lng,
                latitude=patient_lat,
                radius=radius_km,
                unit='km',
                sort='ASC',
                withcoord=False,
                withdist=True,
            )

            candidates: list[dict[str, Any]] = []
            for member, distance in results:
                member_str = member.decode() if isinstance(member, bytes) else member
                # Extract nurse_id from "nurse:<id>" format
                try:
                    nurse_id = int(member_str.split(':')[1])
                except (IndexError, ValueError):
                    logger.warning('Invalid geo member format: %s', member_str)
                    continue

                candidates.append({
                    'nurse_id': nurse_id,
                    'distance_km': round(float(distance), 3),
                })

            logger.debug(
                'Found %d candidates within %.1f km of (%.6f, %.6f)',
                len(candidates), radius_km, patient_lat, patient_lng,
            )
            return candidates

        except (redis.ConnectionError, redis.TimeoutError):
            logger.exception(
                'Redis error searching candidates near (%.6f, %.6f)',
                patient_lat, patient_lng,
            )
            return []

    def get_nurse_location(self, nurse_id: int) -> tuple[float, float] | None:
        """
        Get the current coordinates of a specific nurse.

        Args:
            nurse_id: Unique identifier of the nurse.

        Returns:
            Tuple of (latitude, longitude) or None if nurse not found or error.
        """
        if not self._is_available():
            return None

        try:
            member: str = f'nurse:{nurse_id}'
            positions = self._redis.geopos(GEO_KEY, member)

            if not positions or positions[0] is None:
                return None

            lng, lat = positions[0]
            return (float(lat), float(lng))

        except (redis.ConnectionError, redis.TimeoutError):
            logger.exception('Redis error getting nurse %s location', nurse_id)
            return None

    def remove_nurse(self, nurse_id: int) -> bool:
        """
        Remove a nurse from the geospatial index.

        Args:
            nurse_id: Unique identifier of the nurse.

        Returns:
            True if the nurse was removed, False otherwise.
        """
        if not self._is_available():
            return False

        try:
            member: str = f'nurse:{nurse_id}'
            removed: int = self._redis.zrem(GEO_KEY, member)
            if removed:
                logger.debug('Removed nurse %s from geo index', nurse_id)
            return bool(removed)
        except (redis.ConnectionError, redis.TimeoutError):
            logger.exception('Redis error removing nurse %s', nurse_id)
            return False
```

---

### Step 5 — Create `tests/test_matching_service.py`

Create the test file using `pytest` and `fakeredis`:

```python
"""
Tests for the GeoMatchingService.

Uses fakeredis to provide an in-memory Redis instance for testing
geospatial operations without requiring a running Redis server.
"""

import pytest
from unittest.mock import patch, MagicMock

import fakeredis

from visits.services.matching import GeoMatchingService, GEO_KEY


@pytest.fixture
def fake_redis():
    """Create a fakeredis instance for testing."""
    server = fakeredis.FakeServer()
    return fakeredis.FakeRedis(server=server)


@pytest.fixture
def geo_service(fake_redis):
    """Create a GeoMatchingService with a mocked Redis connection."""
    with patch('visits.services.matching.get_redis_connection', return_value=fake_redis):
        service = GeoMatchingService()
    return service


class TestUpdateNurseLocation:
    """Tests for GeoMatchingService.update_nurse_location()."""

    def test_update_location_returns_true(self, geo_service):
        result = geo_service.update_nurse_location(nurse_id=1, lat=30.0444, lng=31.2357)
        assert result is True

    def test_update_location_stores_coordinates(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=30.0444, lng=31.2357)
        location = geo_service.get_nurse_location(nurse_id=1)
        assert location is not None
        lat, lng = location
        assert abs(lat - 30.0444) < 0.001
        assert abs(lng - 31.2357) < 0.001

    def test_update_location_overwrites_previous(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=30.0000, lng=31.0000)
        geo_service.update_nurse_location(nurse_id=1, lat=30.1000, lng=31.1000)
        location = geo_service.get_nurse_location(nurse_id=1)
        assert location is not None
        lat, lng = location
        assert abs(lat - 30.1000) < 0.001
        assert abs(lng - 31.1000) < 0.001


class TestFindCandidates:
    """Tests for GeoMatchingService.find_candidates()."""

    def test_nurse_within_radius_is_found(self, geo_service):
        # Place nurse ~0.1km from patient
        geo_service.update_nurse_location(nurse_id=1, lat=30.0444, lng=31.2357)
        candidates = geo_service.find_candidates(
            patient_lat=30.0450, patient_lng=31.2360, radius_km=5.0
        )
        assert len(candidates) == 1
        assert candidates[0]['nurse_id'] == 1
        assert candidates[0]['distance_km'] < 5.0

    def test_nurse_outside_radius_not_found(self, geo_service):
        # Place nurse ~100km away
        geo_service.update_nurse_location(nurse_id=1, lat=31.0000, lng=32.0000)
        candidates = geo_service.find_candidates(
            patient_lat=30.0444, patient_lng=31.2357, radius_km=5.0
        )
        assert len(candidates) == 0

    def test_multiple_nurses_sorted_by_distance(self, geo_service):
        # Nurse 1: very close
        geo_service.update_nurse_location(nurse_id=1, lat=30.0445, lng=31.2358)
        # Nurse 2: farther but within radius
        geo_service.update_nurse_location(nurse_id=2, lat=30.0500, lng=31.2400)
        # Nurse 3: outside radius
        geo_service.update_nurse_location(nurse_id=3, lat=31.0000, lng=32.0000)

        candidates = geo_service.find_candidates(
            patient_lat=30.0444, patient_lng=31.2357, radius_km=5.0
        )
        assert len(candidates) == 2
        assert candidates[0]['nurse_id'] == 1  # Closest first
        assert candidates[1]['nurse_id'] == 2
        assert candidates[0]['distance_km'] <= candidates[1]['distance_km']

    def test_empty_index_returns_empty_list(self, geo_service):
        candidates = geo_service.find_candidates(
            patient_lat=30.0444, patient_lng=31.2357, radius_km=5.0
        )
        assert candidates == []


class TestGetNurseLocation:
    """Tests for GeoMatchingService.get_nurse_location()."""

    def test_returns_coordinates_for_known_nurse(self, geo_service):
        geo_service.update_nurse_location(nurse_id=42, lat=30.0444, lng=31.2357)
        location = geo_service.get_nurse_location(nurse_id=42)
        assert location is not None
        lat, lng = location
        assert abs(lat - 30.0444) < 0.001
        assert abs(lng - 31.2357) < 0.001

    def test_returns_none_for_unknown_nurse(self, geo_service):
        location = geo_service.get_nurse_location(nurse_id=999)
        assert location is None


class TestRemoveNurse:
    """Tests for GeoMatchingService.remove_nurse()."""

    def test_remove_existing_nurse(self, geo_service):
        geo_service.update_nurse_location(nurse_id=1, lat=30.0444, lng=31.2357)
        result = geo_service.remove_nurse(nurse_id=1)
        assert result is True
        assert geo_service.get_nurse_location(nurse_id=1) is None

    def test_remove_nonexistent_nurse_returns_false(self, geo_service):
        result = geo_service.remove_nurse(nurse_id=999)
        assert result is False


class TestRedisErrorHandling:
    """Tests for graceful Redis error handling."""

    def test_update_returns_false_when_redis_unavailable(self):
        with patch('visits.services.matching.get_redis_connection', side_effect=Exception('Connection refused')):
            service = GeoMatchingService()
        result = service.update_nurse_location(nurse_id=1, lat=30.0, lng=31.0)
        assert result is False

    def test_find_returns_empty_when_redis_unavailable(self):
        with patch('visits.services.matching.get_redis_connection', side_effect=Exception('Connection refused')):
            service = GeoMatchingService()
        result = service.find_candidates(patient_lat=30.0, patient_lng=31.0)
        assert result == []

    def test_get_location_returns_none_when_redis_unavailable(self):
        with patch('visits.services.matching.get_redis_connection', side_effect=Exception('Connection refused')):
            service = GeoMatchingService()
        result = service.get_nurse_location(nurse_id=1)
        assert result is None

    def test_remove_returns_false_when_redis_unavailable(self):
        with patch('visits.services.matching.get_redis_connection', side_effect=Exception('Connection refused')):
            service = GeoMatchingService()
        result = service.remove_nurse(nurse_id=1)
        assert result is False
```

---

## 4) Definition of Done (DoD)

### Functional Validation

- [ ] `GeoMatchingService` instantiates without error when Redis is available
- [ ] `update_nurse_location()` stores coordinates retrievable by `get_nurse_location()`
- [ ] `find_candidates()` returns nurses within radius, sorted by distance
- [ ] `find_candidates()` excludes nurses outside the radius
- [ ] `get_nurse_location()` returns `None` for non-existent nurses
- [ ] `remove_nurse()` removes a nurse from the geo index
- [ ] All methods return safe defaults when Redis is unavailable
- [ ] `from visits.services import create_visit_request` continues to work (backward compatibility)
- [ ] All tests pass: `python -m pytest tests/test_matching_service.py -v`

### Architectural Compliance

- [ ] `GeoMatchingService` is in `visits/services/matching.py`
- [ ] Service does NOT import any Django models
- [ ] All public methods have complete type hints
- [ ] All Redis errors are caught and logged via `logging.getLogger(__name__)`
- [ ] Redis key uses `nurse_geo:` prefix
- [ ] TTL refreshed on `update_nurse_location` (1 hour default)
- [ ] Module-level docstrings on all new files

### Standards Compliance

- [ ] No hardcoded Redis connection strings
- [ ] PEP 8 / project naming conventions followed
- [ ] Egyptian Arabic not required in this module (internal service, not user-facing)
- [ ] `requirements/base.txt` and `requirements/dev.txt` updated with pinned versions

---

## 5) Acceptance Authority

The Reviewer (Kilo Code) must validate:

1. **Correctness** — All tests pass, geospatial math is accurate
2. **Backward Compatibility** — Existing `create_visit_request` imports unbroken
3. **Error Resilience** — Service gracefully handles Redis unavailability
4. **Type Safety** — All public methods have complete type annotations
5. **Separation of Concerns** — Service is Redis-only, no Django ORM dependencies

Failure in any category rejects the task.

---

## Final Directive

The execution agent must not deviate from this specification.
The reviewer must reject the task if any section is partially satisfied.
