import contextlib
import json

from django_redis import get_redis_connection

CACHE_TTL = 10  # 10s Heatbeat Cache
LOCK_TIMEOUT = 5

class CacheShield:
    @staticmethod
    def get_agency_metrics(agency_id):
        redis_conn = get_redis_connection("default")
        cache_key = f"cache_agency_metrics_{agency_id}"
        cached_data = redis_conn.get(cache_key)

        if cached_data:
            return json.loads(cached_data)
        return None

    @staticmethod
    def set_agency_metrics(agency_id, payload_dict):
        redis_conn = get_redis_connection("default")
        cache_key = f"cache_agency_metrics_{agency_id}"
        redis_conn.setex(cache_key, CACHE_TTL, json.dumps(payload_dict))

    @staticmethod
    @contextlib.contextmanager
    def lock_agency(agency_id):
        """
        Mutex to prevent DB Meltdown. Only the first consumer calculates metrics.
        """
        redis_conn = get_redis_connection("default")
        lock_key = f"lock_agency_metrics_{agency_id}"

        lock_acquired = redis_conn.set(lock_key, "LOCKED", nx=True, ex=LOCK_TIMEOUT)

        try:
            yield lock_acquired
        finally:
            if lock_acquired:
                redis_conn.delete(lock_key)
