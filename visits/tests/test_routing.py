"""
Test suite for OSRM/ORS Routing Service.

Covers:
- True geohash encoding
- OSRM provider successful route resolution
- ORS fallback on OSRM failure
- Redis caching mechanism
- Graceful degradation when all providers fail
"""

from __future__ import annotations

import os
import sys
import unittest

import requests
import responses

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from django.conf import settings
if not settings.configured:
    settings.configure(
        OSRM_BASE_URL="http://router.project-osrm.org",
        ORS_BASE_URL="https://api.openrouteservice.org",
        ORS_API_KEY="test-api-key",
        ROUTING_PROVIDER="osrm",
        ROUTE_CACHE_TTL=900,
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    )

from django.core.cache import cache

from visits.services.routing_service import (
    OSRMProvider,
    ORSProvider,
    RouteResult,
    _encode_geohash,
    _geohash_key,
    get_route,
)

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
    def test_encode_geohash_returns_string(self) -> None:
        result = _encode_geohash(30.0444, 31.2357, precision=7)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 7)

    def test_encode_geohash_precision_7(self) -> None:
        result = _encode_geohash(30.0444, 31.2357, precision=7)
        self.assertEqual(result, "stq4yv3")

    def test_encode_geohash_precision_8(self) -> None:
        result = _encode_geohash(30.0444, 31.2357, precision=8)
        self.assertEqual(len(result), 8)
        self.assertEqual(result, "stq4yv3j")

    def test_geohash_key_format(self) -> None:
        key = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        self.assertTrue(key.startswith("route:"))
        parts = key.split(":")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[1]), 7)
        self.assertEqual(len(parts[2]), 7)

    def test_geohash_key_same_origins_same_key(self) -> None:
        key1 = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        key2 = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        self.assertEqual(key1, key2)

    def test_geohash_key_different_destinations_different_key(self) -> None:
        key1 = _geohash_key(30.0444, 31.2357, 30.0626, 31.2497)
        key2 = _geohash_key(30.0444, 31.2357, 30.1000, 31.3000)
        self.assertNotEqual(key1, key2)


class TestRouteResult(unittest.TestCase):
    def test_route_result_initialization(self) -> None:
        result = RouteResult(distance_km=5.2, duration_minutes=12.3)
        self.assertEqual(result.distance_km, 5.2)
        self.assertEqual(result.duration_minutes, 12.3)
        self.assertIsNone(result.polyline_geometry)

    def test_route_result_with_geometry(self) -> None:
        result = RouteResult(
            distance_km=5.2,
            duration_minutes=12.3,
            polyline_geometry="_p~iF~ps|U",
        )
        self.assertEqual(result.polyline_geometry, "_p~iF~ps|U")


class TestOSRMProvider(unittest.TestCase):
    @responses.activate
    def test_get_route_success(self) -> None:
        base_url = settings.OSRM_BASE_URL
        responses.add(
            responses.GET,
            f"{base_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            json=OSRM_SUCCESS_RESPONSE,
            status=200,
        )

        provider = OSRMProvider()
        result = provider.get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)

        self.assertEqual(result.distance_km, 5.2)
        self.assertEqual(result.duration_minutes, 12.3)

    @responses.activate
    def test_get_route_no_routes_raises_value_error(self) -> None:
        base_url = settings.OSRM_BASE_URL
        responses.add(
            responses.GET,
            f"{base_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            json={"code": "NoRoute", "routes": []},
            status=200,
        )

        provider = OSRMProvider()
        with self.assertRaises(ValueError) as context:
            provider.get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)
        self.assertIn("OSRM returned no routes", str(context.exception))


class TestORSProvider(unittest.TestCase):
    @responses.activate
    def test_get_route_success(self) -> None:
        base_url = settings.ORS_BASE_URL
        responses.add(
            responses.POST,
            f"{base_url}/v2/directions/driving-car",
            json=ORS_SUCCESS_RESPONSE,
            status=200,
        )

        provider = ORSProvider()
        result = provider.get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)

        self.assertEqual(result.distance_km, 5.15)
        self.assertEqual(result.duration_minutes, 12.0)


class TestFailover(unittest.TestCase):
    def setUp(self) -> None:
        cache.clear()

    @responses.activate
    def test_osrm_timeout_falls_back_to_ors(self) -> None:
        osrm_url = settings.OSRM_BASE_URL
        ors_url = settings.ORS_BASE_URL

        responses.add(
            responses.GET,
            f"{osrm_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            body=requests.exceptions.Timeout("OSRM connection timed out"),
        )

        responses.add(
            responses.POST,
            f"{ors_url}/v2/directions/driving-car",
            json=ORS_SUCCESS_RESPONSE,
            status=200,
        )

        result = get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)

        self.assertIsNotNone(result)
        self.assertEqual(result.distance_km, 5.15)
        self.assertEqual(len(responses.calls), 2)

    @responses.activate
    def test_all_providers_fail_raises_runtime_error(self) -> None:
        osrm_url = settings.OSRM_BASE_URL
        ors_url = settings.ORS_BASE_URL

        responses.add(
            responses.GET,
            f"{osrm_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            body=requests.exceptions.Timeout("OSRM timed out"),
        )

        responses.add(
            responses.POST,
            f"{ors_url}/v2/directions/driving-car",
            body=requests.exceptions.Timeout("ORS timed out"),
        )

        with self.assertRaises(RuntimeError) as context:
            get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)

        self.assertIn("All routing providers failed. Last error", str(context.exception))


class TestCaching(unittest.TestCase):
    def setUp(self) -> None:
        cache.clear()

    @responses.activate
    def test_caching_mechanism_prevents_api_call(self) -> None:
        osrm_url = settings.OSRM_BASE_URL

        responses.add(
            responses.GET,
            f"{osrm_url}/route/v1/driving/31.2357,30.0444;31.2497,30.0626",
            json=OSRM_SUCCESS_RESPONSE,
            status=200,
        )

        # First call hits the API and caches the result
        result1 = get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)
        self.assertEqual(result1.distance_km, 5.2)
        self.assertEqual(len(responses.calls), 1)

        # Second call should hit the cache instead of the API
        result2 = get_route(ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG)
        self.assertEqual(result2.distance_km, 5.2)
        self.assertEqual(len(responses.calls), 1)  # Stays at 1


if __name__ == "__main__":
    unittest.main(verbosity=2)
