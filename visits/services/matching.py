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

from users.models import NurseProfile, VerificationStatus

logger = logging.getLogger(__name__)

GEO_KEY: str = "nurse_geo:active_nurses"
LOCATION_TTL_SECONDS: int = 3600


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
            self._redis: redis.Redis = get_redis_connection("default")
        except redis.RedisError as e:
            logger.error(
                "Failed to establish Redis connection for GeoMatchingService: %s",
                e,
                exc_info=True,
            )
            self._redis = None  # type: ignore[assignment]

    def _is_available(self) -> bool:
        """Check if Redis connection is available."""
        return self._redis is not None

    def _validate_coordinates(self, lat: float, lng: float) -> None:
        """
        Validate latitude and longitude ranges.

        Args:
            lat: Latitude to validate.
            lng: Longitude to validate.

        Raises:
            ValueError: If coordinates are out of valid range.
        """
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
        if not (-180 <= lng <= 180):
            raise ValueError(f"Invalid longitude: {lng}. Must be between -180 and 180.")

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

        Raises:
            ValueError: If coordinates are out of valid range.
        """
        self._validate_coordinates(lat, lng)

        if not self._is_available():
            return False

        try:
            member: str = f"nurse:{nurse_id}"
            self._redis.geoadd(GEO_KEY, (lng, lat, member))
            self._redis.expire(GEO_KEY, LOCATION_TTL_SECONDS)
            logger.debug(
                "Updated location for nurse %s: lat=%.6f, lng=%.6f",
                nurse_id,
                lat,
                lng,
            )
            return True
        except redis.RedisError as e:
            logger.error(
                "Redis error updating nurse %s location: %s",
                nurse_id,
                e,
                exc_info=True,
            )
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

        Raises:
            ValueError: If coordinates are out of valid range.
        """
        self._validate_coordinates(patient_lat, patient_lng)

        if not self._is_available():
            return []

        try:
            results = self._redis.geosearch(
                name=GEO_KEY,
                longitude=patient_lng,
                latitude=patient_lat,
                radius=radius_km,
                unit="km",
                sort="ASC",
                withcoord=False,
                withdist=True,
            )  # type: ignore[misc]

            candidates: list[dict[str, Any]] = []
            for item in results:
                member_val: Any = item[0]  # type: ignore
                distance: Any = item[1]  # type: ignore
                
                # FIX: Decode bytes to string if necessary
                member_str = (
                    member_val.decode("utf-8") if isinstance(member_val, bytes) else member_val
                )

                try:
                    # FIX: Robust ID extraction
                    # Safe parsing for "nurse:<id>" or just "<id>"
                    if member_str.startswith("nurse:"):
                        nurse_id_str = member_str.split(":", 1)[1]
                    else:
                        nurse_id_str = member_str

                    if not nurse_id_str.isdigit():
                         logger.warning("Skipping non-numeric nurse ID in geo set: %s", member_str)
                         continue
                         
                    nurse_id = int(nurse_id_str)
                except (IndexError, ValueError, AttributeError) as e:
                    logger.error("Failed to parse geo member '%s': %s", member_str, e)
                    continue

                candidates.append(
                    {
                        "nurse_id": nurse_id,
                        "distance_km": round(float(distance), 3),
                    }
                )

            if not candidates:
                return []

            nurse_ids = [c["nurse_id"] for c in candidates]
            available_nurse_ids = set(
                NurseProfile.objects.filter(
                    id__in=nurse_ids,
                    is_available=True,
                    verification_status=VerificationStatus.VERIFIED,
                ).values_list("id", flat=True)
            )

            candidates = [c for c in candidates if c["nurse_id"] in available_nurse_ids]

            logger.debug(
                "Found %d candidates within %.1f km of (%.6f, %.6f)",
                len(candidates),
                radius_km,
                patient_lat,
                patient_lng,
            )
            return candidates
        except redis.RedisError as e:
            logger.error(
                "Redis error searching candidates near (%.6f, %.6f): %s",
                patient_lat,
                patient_lng,
                e,
                exc_info=True,
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
            member: str = f"nurse:{nurse_id}"
            positions = self._redis.geopos(GEO_KEY, member)
            if not positions or positions[0] is None:
                return None

            lng, lat = positions[0]  # type: ignore
            return (float(lat), float(lng))
        except redis.RedisError as e:
            logger.error(
                "Redis error getting nurse %s location: %s",
                nurse_id,
                e,
                exc_info=True,
            )
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
            member: str = f"nurse:{nurse_id}"
            removed: Any = self._redis.zrem(GEO_KEY, member)
            if removed:
                logger.debug("Removed nurse %s from geo index", nurse_id)
            return bool(removed)
        except redis.RedisError as e:
            logger.error(
                "Redis error removing nurse %s: %s",
                nurse_id,
                e,
                exc_info=True,
            )
            return False


def rank_agencies(agencies_qs, patient_location=None) -> list:
    """
    Rank overlapping agencies by QualityScore for Tier 1 dispatch selection.
    
    QualityScore = (rating × 0.4) + (normalized_capacity × 0.3) + (response_rate × 0.3)
    
    Args:
        agencies_qs: QuerySet of AgencyProfile instances (already filtered by coverage)
        patient_location: Optional Point for distance bonus (future enhancement)
    
    Returns:
        List of dicts: [{"agency": AgencyProfile, "score": float}, ...]
        Sorted by score descending (best agency first)
    """
    from users.models import VerificationStatus
    from django.core.cache import cache
    from django.db.models import Count, Q

    # Annotate nurse counts in a single query (eliminates N+1)
    annotated_agencies = agencies_qs.select_related("user").annotate(
        total_nurses=Count("nurses"),
        available_nurses=Count(
            "nurses",
            filter=Q(
                nurses__is_available=True,
                nurses__verification_status=VerificationStatus.VERIFIED,
            ),
        ),
    )

    # Batch cache lookup for response rates (W4 fix — eliminates N+1 on cache)
    agency_list = list(annotated_agencies)
    cache_keys = {a.id: f"agency_response_rate:{a.id}" for a in agency_list}
    cached_rates = cache.get_many(list(cache_keys.values()))

    scored_agencies = []

    for agency in agency_list:
        # 1. Rating component (0-5 scale, normalized to 0-1)
        rating = float(agency.rating or 0) / 5.0

        # 2. Capacity component — available nurses / total nurses
        capacity = agency.available_nurses / max(agency.total_nurses, 1)

        # 3. Response rate — batch-cached for 1 hour
        cache_key = cache_keys[agency.id]
        response_rate = cached_rates.get(cache_key)
        if response_rate is None:
            from visits.models import Visit, VisitStatus
            last_100 = Visit.objects.filter(agency=agency).order_by("-created_at")[:100]
            total = last_100.count()
            if total > 0:
                accepted = last_100.filter(
                    status__in=[
                        VisitStatus.ACCEPTED,
                        VisitStatus.EN_ROUTE,
                        VisitStatus.IN_PROGRESS,
                        VisitStatus.COMPLETED,
                    ]
                ).count()
                response_rate = accepted / total
            else:
                response_rate = 0.5  # Default for new agencies
            cache.set(cache_key, response_rate, 3600)  # 1 hour

        # Compute QualityScore
        score = (rating * 0.4) + (capacity * 0.3) + (response_rate * 0.3)
        scored_agencies.append({"agency": agency, "score": round(score, 4)})

    # Sort by score descending
    scored_agencies.sort(key=lambda x: x["score"], reverse=True)
    return scored_agencies
