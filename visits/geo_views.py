from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import connection
from visits.services.geo_service import get_redis_client
import requests
import logging
from django.core.cache import cache
from users.permissions import IsSuperAdmin
from users.models import AgencyProfile

logger = logging.getLogger(__name__)

class GeoDiagnosticsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        diagnostics = {
            "spatial_index_status": self._check_spatial_indexes(),
            "redis_cache_metrics": self._get_redis_metrics(),
            "nominatim_health": self._check_nominatim(),
            "db_engine": connection.settings_dict.get('ENGINE')
        }
        
        # Calculate hit rate if possible
        hits = diagnostics["redis_cache_metrics"].get("cache_hits", 0)
        misses = diagnostics["redis_cache_metrics"].get("cache_misses", 0)
        total = hits + misses
        diagnostics["cache_hit_rate"] = f"{(hits/total)*100:.1f}%" if total > 0 else "0%"

        return Response(diagnostics)

    def _check_spatial_indexes(self):
        try:
            with connection.cursor() as cursor:
                # Check for GIST indexes on AgencyProfile
                cursor.execute(f"""
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = '{AgencyProfile._meta.db_table}' AND indexdef LIKE '%gist%';
                """)
                indexes = [row[0] for row in cursor.fetchall()]
                return {
                    "status": "HEALTHY" if indexes else "WARNING",
                    "gist_indexes": indexes
                }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def _get_redis_metrics(self):
        client = get_redis_client()
        if not client:
            return {"status": "DOWN"}
        
        try:
            return {
                "status": "UP",
                "cache_hits": int(client.get("geo:metrics:cache_hit") or 0),
                "cache_misses": int(client.get("geo:metrics:cache_miss") or 0)
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def _check_nominatim(self):
        cache_key = "geo:diagnostics:nominatim_health"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            # We don't want to spam, just a quick health check or last known status
            # For now, we simulate a check to the root which is usually allowed
            headers = {'User-Agent': 'WateenBackend/1.0 (contact@wateen.sa)'}
            response = requests.get("https://nominatim.openstreetmap.org/status.php", headers=headers, timeout=5)
            result = {
                "status": "UP" if response.status_code == 200 else "DEGRADED",
                "http_code": response.status_code
            }
            cache.set(cache_key, result, timeout=60)
            return result
        except Exception as e:
            return {"status": "DOWN", "message": str(e)}
