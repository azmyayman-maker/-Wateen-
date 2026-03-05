"""
Routing Service — Calculates driving distance and ETA between two points.

Supports OSRM (default, free) and OpenRouteService (ORS, fallback) with
automatic failover and Redis caching.

Usage:
    from visits.services.routing_service import get_route, calculate_nurse_eta
    
    result = get_route(30.0444, 31.2357, 30.0626, 31.2497)
    # RouteResult(distance_km=5.2, duration_minutes=12.3, polyline_geometry="...")
"""

from __future__ import annotations

import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RouteResult:
    """Immutable result of a routing query."""
    distance_km: float
    duration_minutes: float
    polyline_geometry: Optional[str] = None


class RoutingProvider(ABC):
    """Abstract base class for routing providers."""

    @abstractmethod
    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> RouteResult:
        """Calculate the driving route between two points."""
        ...


class OSRMProvider(RoutingProvider):
    """
    Open Source Routing Machine (OSRM) provider.
    Free, self-hostable, no API key required for the demo server.
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or getattr(settings, "OSRM_BASE_URL", "")).rstrip("/")

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> RouteResult:
        # OSRM uses lng,lat ordering
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


class ORSProvider(RoutingProvider):
    """
    OpenRouteService (ORS) provider — fallback with API key.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or getattr(settings, "ORS_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or getattr(settings, "ORS_API_KEY", "")

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> RouteResult:
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


def _geohash_key(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    """Generate a cache key from coordinates with 4-decimal precision (~11m)."""
    raw = f"{lat1:.4f},{lng1:.4f}:{lat2:.4f},{lng2:.4f}"
    return f"route:{hashlib.md5(raw.encode()).hexdigest()}"


def get_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    *,
    bypass_cache: bool = False,
) -> RouteResult:
    """
    Calculate driving route with automatic provider failover and Redis caching.

    Tries the primary provider (from settings.ROUTING_PROVIDER), then falls back
    to the secondary. Results are cached for 15 minutes by geohash.
    """
    # Check cache
    if not bypass_cache:
        cache_key = _geohash_key(origin_lat, origin_lng, dest_lat, dest_lng)
        cached = cache.get(cache_key)
        if cached:
            return RouteResult(**cached)

    # Provider order based on settings
    primary_name = getattr(settings, "ROUTING_PROVIDER", "osrm")
    providers: list[tuple[str, RoutingProvider]] = []

    if primary_name == "ors":
        providers = [("ors", ORSProvider()), ("osrm", OSRMProvider())]
    else:
        providers = [("osrm", OSRMProvider()), ("ors", ORSProvider())]

    last_error: Exception | None = None
    for name, provider in providers:
        try:
            result = provider.get_route(origin_lat, origin_lng, dest_lat, dest_lng)

            # Cache the result
            if not bypass_cache:
                ttl = getattr(settings, "ROUTE_CACHE_TTL", 900)
                cache.set(cache_key, {
                    "distance_km": result.distance_km,
                    "duration_minutes": result.duration_minutes,
                    "polyline_geometry": result.polyline_geometry,
                }, ttl)

            return result
        except Exception as e:
            logger.warning("Routing provider %s failed: %s", name, e)
            last_error = e
            continue

    raise RuntimeError(
        f"All routing providers failed. Last error: {last_error}"
    ) from last_error


def calculate_nurse_eta(nurse_profile, patient_location) -> Optional[RouteResult]:
    """
    Calculate ETA from a nurse's last known location to the patient.

    Args:
        nurse_profile: NurseProfile instance with last_location (Point)
        patient_location: Point (GeoDjango) of the patient

    Returns:
        RouteResult or None if nurse has no location
    """
    if not nurse_profile.last_location:
        return None

    try:
        return get_route(
            origin_lat=nurse_profile.last_location.y,
            origin_lng=nurse_profile.last_location.x,
            dest_lat=patient_location.y,
            dest_lng=patient_location.x,
        )
    except RuntimeError:
        logger.error(
            "Failed to calculate ETA for nurse %s",
            nurse_profile.user_id,
        )
        return None
