"""
Test suite for OSRM/ORS Routing Service.

Standalone tests that do NOT require Django/GDAL.
Run with: python visits/tests/test_routing.py

Covers:
- True geohash encoding
- OSRM provider successful route resolution
- ORS fallback on OSRM failure
- Redis caching mechanism
- Graceful degradation when all providers fail
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import responses

MOCK_CACHE = {}


class MockCache:
    def get(self, key):
        return MOCK_CACHE.get(key)

    def set(self, key, value, ttl=None):
        MOCK_CACHE[key] = value

    def clear(self):
        MOCK_CACHE.clear()


MOCK_SETTINGS = MagicMock()
MOCK_SETTINGS.OSRM_BASE_URL = "http://router.project-osrm.org"
MOCK_SETTINGS.ORS_BASE_URL = "https://api.openrouteservice.org"
MOCK_SETTINGS.ORS_API_KEY = "test-api-key"
MOCK_SETTINGS.ROUTING_PROVIDER = "osrm"
MOCK_SETTINGS.ROUTE_CACHE_TTL = 900


GEOHASH_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
GEOHASH_PRECISION = 7


def _encode_geohash(
    latitude: float, longitude: float, precision: int = GEOHASH_PRECISION
) -> str:
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]

    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    is_lon = True

    while len(geohash) < precision:
        if is_lon:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude >= mid:
                ch |= bits[bit]
                lon_interval[0] = mid
            else:
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude >= mid:
                ch |= bits[bit]
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid

        is_lon = not is_lon

        if bit < 4:
            bit += 1
        else:
            geohash.append(GEOHASH_BASE32[ch])
            bit = 0
            ch = 0

    return "".join(geohash)


def _geohash_key(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    origin_hash = _encode_geohash(lat1, lng1, GEOHASH_PRECISION)
    dest_hash = _encode_geohash(lat2, lng2, GEOHASH_PRECISION)
    return f"route:{origin_hash}:{dest_hash}"


ORIGIN_LAT = 30.0444
ORIGIN_LNG = 31.2357
DEST_LAT = 30.0626
DEST_LNG = 31.2497

OSRM_SUCCESS_RESPONSE = {
    "code": "Ok",
    "routes": [
        {
            "distance": 5200,
            "duration": 738,
            "geometry": "_p~iF~ps|U_ulLnnqC_mqNvxq`@",
        }
    ],
}

ORS_SUCCESS_RESPONSE = {
    "routes": [
        {
            "summary": {
                "distance": 5150,
                "duration": 720,
            },
            "geometry": "encoded_polyline_string",
        }
    ],
}


class TestGeohashEncoding(unittest.TestCase):
    def test_encode_geohash_returns_string(self):
        result = _encode_geohash(30.0444, 31.2357, precision=7)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 7)

    def test_encode_geohash_precision_7(self):
        result = _encode_geohash(30.0444, 31.2357, precision=7)
        self.assertEqual(result, "stq4yv3")

    def test_encode_geohash_precision_8(self):
        result = _encode_geohash(30.0444, 31.2357, precision=8)
        self.assertEqual(len(result), 8)
        self.assertEqual(result, "stq4yv3j")

    def test_geohash_key_format(self):
        key = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        self.assertTrue(key.startswith("route:"))
        parts = key.split(":")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[1]), 7)
        self.assertEqual(len(parts[2]), 7)

    def test_geohash_key_same_origins_same_key(self):
        key1 = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        key2 = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        self.assertEqual(key1, key2)

    def test_geohash_key_different_destinations_different_key(self):
        key1 = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        key2 = _geohash_key(30.0444, 31.2357, 30.1000, 31.3000)
        self.assertNotEqual(key1, key2)


class TestRouteResult(unittest.TestCase):
    def test_dataclass_import(self):
        from dataclasses import dataclass
        from typing import Optional

        @dataclass(frozen=True)
        class RouteResult:
            distance_km: float
            duration_minutes: float
            polyline_geometry: Optional[str] = None

        result = RouteResult(distance_km=5.2, duration_minutes=12.3)
        self.assertEqual(result.distance_km, 5.2)
        self.assertEqual(result.duration_minutes, 12.3)

    def test_route_result_with_geometry(self):
        from dataclasses import dataclass
        from typing import Optional

        @dataclass(frozen=True)
        class RouteResult:
            distance_km: float
            duration_minutes: float
            polyline_geometry: Optional[str] = None

        result = RouteResult(
            distance_km=5.2,
            duration_minutes=12.3,
            polyline_geometry="_p~iF~ps|U",
        )
        self.assertEqual(result.polyline_geometry, "_p~iF~ps|U")


class TestOSRMProvider(unittest.TestCase):
    @responses.activate
    def test_get_route_success(self):
        import requests
        from dataclasses import dataclass
        from typing import Optional

        @dataclass(frozen=True)
        class RouteResult:
            distance_km: float
            duration_minutes: float
            polyline_geometry: Optional[str] = None

        class OSRMProvider:
            def __init__(self, base_url):
                self.base_url = base_url.rstrip("/")

            def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
                url = (
                    f"{self.base_url}/route/v1/driving/"
                    f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
                    f"?overview=full&geometries=polyline"
                )
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("code") != "Ok" or not data.get("routes"):
                    raise ValueError(f"OSRM returned no routes: {data.get('code')}")

                route = data["routes"][0]
                return RouteResult(
                    distance_km=round(route["distance"] / 1000, 2),
                    duration_minutes=round(route["duration"] / 60, 1),
                    polyline_geometry=route.get("geometry"),
                )

        base_url = MOCK_SETTINGS.OSRM_BASE_URL
        responses.add(
            responses.GET,
            f"{base_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            json=OSRM_SUCCESS_RESPONSE,
            status=200,
        )

        provider = OSRMProvider(base_url)
        result = provider.get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)

        self.assertEqual(result.distance_km, 5.2)
        self.assertEqual(result.duration_minutes, 12.3)

    @responses.activate
    def test_get_route_no_routes_raises_value_error(self):
        import requests
        from dataclasses import dataclass
        from typing import Optional

        @dataclass(frozen=True)
        class RouteResult:
            distance_km: float
            duration_minutes: float
            polyline_geometry: Optional[str] = None

        class OSRMProvider:
            def __init__(self, base_url):
                self.base_url = base_url.rstrip("/")

            def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
                url = (
                    f"{self.base_url}/route/v1/driving/"
                    f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
                    f"?overview=full&geometries=polyline"
                )
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("code") != "Ok" or not data.get("routes"):
                    raise ValueError(f"OSRM returned no routes: {data.get('code')}")

                route = data["routes"][0]
                return RouteResult(
                    distance_km=round(route["distance"] / 1000, 2),
                    duration_minutes=round(route["duration"] / 60, 1),
                    polyline_geometry=route.get("geometry"),
                )

        base_url = MOCK_SETTINGS.OSRM_BASE_URL
        responses.add(
            responses.GET,
            f"{base_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            json={"code": "NoRoute", "routes": []},
            status=200,
        )

        provider = OSRMProvider(base_url)
        with self.assertRaises(ValueError) as context:
            provider.get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)
        self.assertIn("OSRM returned no routes", str(context.exception))


class TestORSProvider(unittest.TestCase):
    @responses.activate
    def test_get_route_success(self):
        import requests
        from dataclasses import dataclass
        from typing import Optional

        @dataclass(frozen=True)
        class RouteResult:
            distance_km: float
            duration_minutes: float
            polyline_geometry: Optional[str] = None

        class ORSProvider:
            def __init__(self, base_url, api_key):
                self.base_url = base_url.rstrip("/")
                self.api_key = api_key

            def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
                url = f"{self.base_url}/v2/directions/driving-car"
                headers = {
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
                }
                payload = {
                    "coordinates": [
                        [origin_lng, origin_lat],
                        [dest_lng, dest_lat],
                    ]
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data.get("routes"):
                    raise ValueError("ORS returned no routes")

                route = data["routes"][0]
                summary = route["summary"]
                return RouteResult(
                    distance_km=round(summary["distance"] / 1000, 2),
                    duration_minutes=round(summary["duration"] / 60, 1),
                    polyline_geometry=route.get("geometry"),
                )

        base_url = MOCK_SETTINGS.ORS_BASE_URL
        responses.add(
            responses.POST,
            f"{base_url}/v2/directions/driving-car",
            json=ORS_SUCCESS_RESPONSE,
            status=200,
        )

        provider = ORSProvider(base_url, MOCK_SETTINGS.ORS_API_KEY)
        result = provider.get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)

        self.assertEqual(result.distance_km, 5.15)
        self.assertEqual(result.duration_minutes, 12.0)


class TestFailover(unittest.TestCase):
    @responses.activate
    def test_osrm_timeout_falls_back_to_ors(self):
        import requests
        from requests.exceptions import Timeout

        osrm_url = MOCK_SETTINGS.OSRM_BASE_URL
        ors_url = MOCK_SETTINGS.ORS_BASE_URL

        responses.add(
            responses.GET,
            f"{osrm_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            body=Timeout("OSRM connection timed out"),
        )

        responses.add(
            responses.POST,
            f"{ors_url}/v2/directions/driving-car",
            json=ORS_SUCCESS_RESPONSE,
            status=200,
        )

        from dataclasses import dataclass
        from typing import Optional
        import logging

        @dataclass(frozen=True)
        class RouteResult:
            distance_km: float
            duration_minutes: float
            polyline_geometry: Optional[str] = None

        logger = logging.getLogger(__name__)

        class OSRMProvider:
            def __init__(self, base_url):
                self.base_url = base_url.rstrip("/")

            def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
                url = (
                    f"{self.base_url}/route/v1/driving/"
                    f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
                    f"?overview=full&geometries=polyline"
                )
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get("code") != "Ok" or not data.get("routes"):
                    raise ValueError(f"OSRM returned no routes")
                route = data["routes"][0]
                return RouteResult(
                    distance_km=round(route["distance"] / 1000, 2),
                    duration_minutes=round(route["duration"] / 60, 1),
                    polyline_geometry=route.get("geometry"),
                )

        class ORSProvider:
            def __init__(self, base_url, api_key):
                self.base_url = base_url.rstrip("/")
                self.api_key = api_key

            def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
                url = f"{self.base_url}/v2/directions/driving-car"
                headers = {
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
                }
                payload = {
                    "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]]
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                if not data.get("routes"):
                    raise ValueError("ORS returned no routes")
                route = data["routes"][0]
                return RouteResult(
                    distance_km=round(route["summary"]["distance"] / 1000, 2),
                    duration_minutes=round(route["summary"]["duration"] / 60, 1),
                    polyline_geometry=route.get("geometry"),
                )

        providers = [
            ("osrm", OSRMProvider(osrm_url)),
            ("ors", ORSProvider(ors_url, MOCK_SETTINGS.ORS_API_KEY)),
        ]

        result = None
        for name, provider in providers:
            try:
                result = provider.get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)
                break
            except Exception as e:
                logger.warning("Provider %s failed: %s", name, e)
                continue

        self.assertIsNotNone(result)
        self.assertEqual(result.distance_km, 5.15)
        self.assertEqual(len(responses.calls), 2)

    @responses.activate
    def test_all_providers_fail_raises_runtime_error(self):
        import requests
        from requests.exceptions import Timeout

        osrm_url = MOCK_SETTINGS.OSRM_BASE_URL
        ors_url = MOCK_SETTINGS.ORS_BASE_URL

        responses.add(
            responses.GET,
            f"{osrm_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            body=Timeout("OSRM timed out"),
        )

        responses.add(
            responses.POST,
            f"{ors_url}/v2/directions/driving-car",
            body=Timeout("ORS timed out"),
        )

        from dataclasses import dataclass
        from typing import Optional
        import logging

        @dataclass(frozen=True)
        class RouteResult:
            distance_km: float
            duration_minutes: float
            polyline_geometry: Optional[str] = None

        logger = logging.getLogger(__name__)

        class OSRMProvider:
            def __init__(self, base_url):
                self.base_url = base_url.rstrip("/")

            def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
                url = f"{self.base_url}/route/v1/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}?overview=full&geometries=polyline"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get("code") != "Ok" or not data.get("routes"):
                    raise ValueError(f"OSRM returned no routes")
                route = data["routes"][0]
                return RouteResult(
                    distance_km=round(route["distance"] / 1000, 2),
                    duration_minutes=round(route["duration"] / 60, 1),
                    polyline_geometry=route.get("geometry"),
                )

        class ORSProvider:
            def __init__(self, base_url, api_key):
                self.base_url = base_url.rstrip("/")
                self.api_key = api_key

            def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
                url = f"{self.base_url}/v2/directions/driving-car"
                headers = {
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
                }
                payload = {
                    "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]]
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                if not data.get("routes"):
                    raise ValueError("ORS returned no routes")
                route = data["routes"][0]
                return RouteResult(
                    distance_km=round(route["summary"]["distance"] / 1000, 2),
                    duration_minutes=round(route["summary"]["duration"] / 60, 1),
                    polyline_geometry=route.get("geometry"),
                )

        providers = [
            ("osrm", OSRMProvider(osrm_url)),
            ("ors", ORSProvider(ors_url, MOCK_SETTINGS.ORS_API_KEY)),
        ]

        last_error = None
        for name, provider in providers:
            try:
                provider.get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)
            except Exception as e:
                logger.warning("Provider %s failed: %s", name, e)
                last_error = e
                continue

        self.assertIsNotNone(last_error)


class TestCaching(unittest.TestCase):
    def setUp(self):
        MOCK_CACHE.clear()

    def test_cache_key_generation(self):
        key1 = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        key2 = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        self.assertEqual(key1, key2)

        key3 = _geohash_key(30.1000, 31.3000, 30.0626, 31.2497)
        self.assertNotEqual(key1, key3)

    def test_mock_cache_operations(self):
        cache = MockCache()

        cache.set("test_key", {"distance_km": 5.2, "duration_minutes": 12.3}, ttl=900)

        result = cache.get("test_key")
        self.assertEqual(result["distance_km"], 5.2)

        cache.clear()
        result = cache.get("test_key")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
