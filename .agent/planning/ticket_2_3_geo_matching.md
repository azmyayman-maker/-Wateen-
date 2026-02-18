# Ticket 2.3 — Geospatial Matching Engine

## Objective

Implement a high-performance `GeoMatchingService` using Redis `GEOADD`/`GEOSEARCH`/`GEOPOS` for real-time nurse proximity lookups. This is the foundation for the dispatching engine — the matching logic that connects patients to nearby nurses.

---

## Prerequisites (Already Verified)

- Redis service running in Docker (host: `redis`, port: `6379`, `wateen_network`)
- `redis==5.0.1` already in `requirements/base.txt`
- `CHANNEL_LAYERS` configured in `config/settings.py` pointing to Redis
- `visits` app exists with `services.py` (contains `create_visit_request`)
- `Visit` model with `PointField` and state machine in `visits/models.py`
- `pytest.ini` configured with `DJANGO_SETTINGS_MODULE = config.settings`

---

## Proposed Changes

### Dependencies

#### [MODIFY] `requirements/base.txt`

Add under "Cache & Message Broker" section:

- `django-redis==5.4.0` — Django cache backend for Redis
- `fakeredis[lua]==2.21.0` — Add to `requirements/dev.txt` for testing

### Configuration

#### [MODIFY] `config/settings.py`

Add `CACHES` configuration using `django-redis` with dedicated key prefix:

```python
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

### Service Implementation

#### [NEW] `visits/services/` — Convert from single file to package

- Rename existing `visits/services.py` → `visits/services/__init__.py` (re-export `create_visit_request`)
- Create `visits/services/matching.py` — `GeoMatchingService` class

#### [NEW] `visits/services/matching.py`

`GeoMatchingService` class with:

- `__init__()` — Gets raw Redis connection from `django-redis` cache
- `update_nurse_location(nurse_id: int, lat: float, lng: float) -> bool` — `GEOADD` + key TTL refresh (1 hour)
- `find_candidates(patient_lat: float, patient_lng: float, radius_km: float = 5.0) -> list[dict]` — `GEOSEARCH` returning sorted list of `{nurse_id, distance_km}`
- `get_nurse_location(nurse_id: int) -> tuple[float, float] | None` — `GEOPOS` with None fallback
- `remove_nurse(nurse_id: int) -> bool` — `ZREM` to remove nurse from geo set
- All methods handle `redis.ConnectionError` and `redis.TimeoutError` gracefully with logging

**Redis Key:** `nurse_geo:active_nurses` (single sorted set with geospatial index)

### Testing

#### [NEW] `tests/test_matching_service.py`

Pytest-based tests using `fakeredis` to mock the Redis connection:

- `test_update_and_find_nurse_within_radius`
- `test_nurse_outside_radius_not_found`
- `test_update_location_overwrites_previous`
- `test_get_nurse_location_returns_coordinates`
- `test_get_nurse_location_returns_none_for_unknown`
- `test_remove_nurse`
- `test_redis_connection_error_handled_gracefully`

---

## Architecture Compliance

- Service lives in `visits/services/` (closest domain module)
- No business logic in views or serializers
- Raw Redis client used for geo commands (not available through Django cache API)
- Strict type hints on all public methods
- Graceful error handling — service failures don't crash the caller
- All methods are synchronous (matches existing Django patterns)

---

## Verification Plan

### Automated Tests (inside Docker)

```bash
docker exec -it wateen_web python -m pytest tests/test_matching_service.py -v
```

### Manual Verification

1. Confirm `django-redis` connects correctly:

   ```bash
   docker exec -it wateen_web python -c "from django_redis import get_redis_connection; r = get_redis_connection('default'); r.ping(); print('Redis OK')"
   ```

2. Confirm geospatial operations via Django shell:
   ```bash
   docker exec -it wateen_web python manage.py shell -c "
   from visits.services.matching import GeoMatchingService
   svc = GeoMatchingService()
   svc.update_nurse_location(1, 30.0444, 31.2357)
   print(svc.find_candidates(30.0450, 31.2360, radius_km=5))
   print(svc.get_nurse_location(1))
   "
   ```
