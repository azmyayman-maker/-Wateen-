# Task Identification

- **Task ID:** TASK-009-FIX
- **Task Name:** Ticket 2.3 — Geospatial Matching Engine (Remediation)
- **Status:** Pending
- **Assigned Execution Agent:** OpenCode
- **Assigned Review Authority:** Kilo Code

---

## 1) Context & Objective

The initial implementation plan for the `GeoMatchingService` was flagged during review for generic error handling and missing input validation.

This task is a **remediation** to `TASK-009`. It requires refactoring the `GeoMatchingService` to implement strict coordinate validation and precise Redis error handling, ensuring robustness and stability in production.

---

## 2) Technical Specifications

### Target Files

| File                             | Action | Responsibility                                            |
| -------------------------------- | ------ | --------------------------------------------------------- |
| `visits/services/matching.py`    | MODIFY | Refactor error handling and add validation                |
| `tests/test_matching_service.py` | MODIFY | Add tests for invalid coordinates and connection failures |

### Requirements

1.  **Refined Error Handling:**
    - Catch `redis.RedisError` (not generic `Exception`) for network/logic issues.
    - Log full exception details using `logger.error()`.
    - Return safe defaults (e.g., `[]`, `None`, `False`) on failure; do **NOT** crash.

2.  **Input Validation:**
    - Implement `_validate_coordinates(lat, lng)`.
    - Raise `ValueError` for invalid ranges:
      - Latitude: must be between -90 and 90.
      - Longitude: must be between -180 and 180.
    - Call validation at the start of `update_nurse_location` and `find_candidates`.

3.  **Expanded Testing:**
    - `test_invalid_coordinates_raise_error`
    - `test_redis_connection_failure` (mocked failure returns safe default)

---

## 3) Implementation Steps

### Step 1 — Refactor `visits/services/matching.py`

Modify `GeoMatchingService` to include validation and improved error handling:

```python
"""
Geospatial matching service for nurse proximity lookups.
(Refactored for robustness)
"""
from __future__ import annotations

import logging
from typing import Any

import redis
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

GEO_KEY: str = 'nurse_geo:active_nurses'
LOCATION_TTL_SECONDS: int = 3600

class GeoMatchingService:
    def __init__(self) -> None:
        try:
            self._redis: redis.Redis = get_redis_connection('default')
        except redis.RedisError as e:
            logger.error('Failed to establish Redis connection: %s', e)
            self._redis = None

    def _is_available(self) -> bool:
        return self._redis is not None

    def _validate_coordinates(self, lat: float, lng: float) -> None:
        """
        Validate latitude and longitude ranges.
        Raises ValueError if invalid.
        """
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
        if not (-180 <= lng <= 180):
            raise ValueError(f"Invalid longitude: {lng}. Must be between -180 and 180.")

    def update_nurse_location(self, nurse_id: int, lat: float, lng: float) -> bool:
        self._validate_coordinates(lat, lng)

        if not self._is_available():
            return False

        try:
            member: str = f'nurse:{nurse_id}'
            self._redis.geoadd(GEO_KEY, (lng, lat, member))
            self._redis.expire(GEO_KEY, LOCATION_TTL_SECONDS)
            logger.debug('Updated location for nurse %s', nurse_id)
            return True
        except redis.RedisError as e:
            logger.error('Redis error updating nurse %s: %s', nurse_id, e)
            return False

    def find_candidates(
        self,
        patient_lat: float,
        patient_lng: float,
        radius_km: float = 5.0,
    ) -> list[dict[str, Any]]:
        self._validate_coordinates(patient_lat, patient_lng)

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
                withdist=True,
            )
            # ... (parsing logic remains the same) ...
            return parsed_candidates

        except redis.RedisError as e:
            logger.error('Redis error searches candidates: %s', e)
            return []

    # ... (apply similar patterns to other methods) ...
```

### Step 2 — Update Tests

Add to `tests/test_matching_service.py`:

```python
    def test_invalid_coordinates_raise_error(self, geo_service):
        with pytest.raises(ValueError, match="Invalid latitude"):
            geo_service.update_nurse_location(1, 91.0, 30.0)

        with pytest.raises(ValueError, match="Invalid longitude"):
            geo_service.find_candidates(30.0, 181.0)

    def test_redis_connection_failure_safe_return(self, geo_service):
        # Mock connection to raise RedisError
        with patch.object(geo_service._redis, 'geoadd', side_effect=redis.RedisError("Connection lost")):
            result = geo_service.update_nurse_location(1, 30.0, 31.0)
            assert result is False
```

---

## 4) Acceptance Criteria

- [ ] `_validate_coordinates` raises `ValueError` for out-of-range inputs
- [ ] Redis errors utilize `redis.RedisError` base class
- [ ] All Redis errors are logged with `logger.error`
- [ ] Service does not crash on Redis failure; returns safe defaults
- [ ] New tests pass
