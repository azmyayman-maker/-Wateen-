import logging
import json
import requests
import urllib.parse
from typing import Optional, Any

from django.core.cache import cache
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from users.models import AgencyProfile, AgencyStatus

logger = logging.getLogger(__name__)

# --- Redis Infrastructure ---

def get_redis_client():
    """
    Returns a configured raw Redis client from Django's cache framework.
    Uses thread-safe connection pooling from django-redis.
    """
    try:
        if hasattr(cache, 'client'):
            return cache.client.get_client()
        return None
    except Exception as e:
        logger.error(f"Failed to get Redis client from cache: {e}")
        return None

def track_geo_metric(metric_name: str, increment: int = 1):
    """
    Increments a geospatial metric in Redis for diagnostic purposes.
    Common metrics: 'geo:metrics:cache_hit', 'geo:metrics:cache_miss'
    """
    client = get_redis_client()
    if client:
        try:
            client.incrby(metric_name, increment)
        except Exception as e:
            logger.warning(f"Failed to update metric {metric_name}: {e}")

def get_cached_geo_data(key: str) -> Optional[Any]:
    """
    Retrieves and deserializes data from Redis.
    """
    client = get_redis_client()
    if client:
        try:
            data = client.get(key)
            if data:
                track_geo_metric("geo:metrics:cache_hit")
                return json.loads(data)
            track_geo_metric("geo:metrics:cache_miss")
        except Exception as e:
            logger.error(f"Redis get failed for key {key}: {e}")
    return None

def cache_geo_data(key: str, data: Any, timeout: int = 86400):
    """
    Serializes and stores data in Redis with a TTL (default 24h).
    """
    client = get_redis_client()
    if client:
        try:
            client.setex(key, timeout, json.dumps(data))
        except Exception as e:
            logger.error(f"Redis set failed for key {key}: {e}")

# --- Geocoding Service ---

def geocode_address(address: str) -> Optional[Point]:
    """
    Converts a text address to a GEOS Point (Lng, Lat).
    Uses Nominatim with a 24-hour Redis caching layer.
    """
    if not address:
        return None

    # 1. Check Cache
    cache_key = f"geo:geocode:{urllib.parse.quote(address)}"
    cached = get_cached_geo_data(cache_key)
    if cached:
        return Point(cached['lng'], cached['lat'], srid=4326)

    # 2. Query Nominatim
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {
            'User-Agent': 'WateenBackend/1.0 (contact@wateen.sa)'
        }
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        
        # Respect Nominatim API rate limits (1 req/sec) using non-blocking Redis limit
        client = get_redis_client()
        if client:
            limit_key = "geo:ratelimit:nominatim"
            count = client.incr(limit_key)
            if count == 1:
                client.expire(limit_key, 1)
            elif count > 1:
                logger.warning("Nominatim rate limit exceeded (1 req/s). Request dropped to avoid blocking.")
                return None
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            location = data[0]
            lat = float(location['lat'])
            lng = float(location['lon'])
            
            # 3. Store in Cache
            cache_geo_data(cache_key, {'lat': lat, 'lng': lng})
            
            return Point(lng, lat, srid=4326)
            
    except Exception as e:
        logger.error(f"Geocoding failed for {address}: {e}")
    
    return None

# --- Spatial Matching Service ---

def find_agencies_covering_point(point: Point):
    """
    Returns a queryset of verified agencies whose coverage polygon intersects the point.
    Annotates each result with 'distance_to_center' (distance from point to polygon centroid).
    """
    if not point:
        return AgencyProfile.objects.none()

    # Filter verified agencies where coverage_polygon intersects point
    # We use __intersects which maps to PostGIS ST_Intersects
    agencies = AgencyProfile.objects.filter(
        status=AgencyStatus.VERIFIED,
        coverage_polygon__intersects=point
    ).annotate(
        distance_to_center=Distance('coverage_polygon', point)
    )

    return agencies
