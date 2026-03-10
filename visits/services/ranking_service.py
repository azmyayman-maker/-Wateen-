from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import NamedTuple, List, Optional
from uuid import UUID

from django.core.cache import cache
from django.db.models import QuerySet, Count, Q
from django.contrib.gis.geos import Point

from users.models import AgencyProfile, NurseProfile
from users.services.agency_stats_service import get_agency_operational_stats
from visits.models import VisitUrgency
from visits.services.routing_service import calculate_nurse_eta, RouteResult

logger = logging.getLogger(__name__)


@dataclass
class AlgConstants:
    """Mathematical constants for the dynamic vector-based scoring algorithm."""

    kappa: float = 0.5
    mu: float = 0.6
    lambda_decay: float = 0.1
    ETA_optimal: float = 15.0


ALGORITHM_CONSTANTS = AlgConstants()


class AgencyScore(NamedTuple):
    agency_id: UUID
    score: float
    eta: Optional[float]
    clinical_quality: float
    operational_reliability: float
    spatial_proximity: float
    debug_info: dict


# Maps VisitUrgency to weights: (W_q, W_r, W_p)
URGENCY_WEIGHTS = {
    VisitUrgency.LOW: (0.4, 0.3, 0.3),
    VisitUrgency.MEDIUM: (0.4, 0.3, 0.3),
    VisitUrgency.HIGH: (0.3, 0.3, 0.4),
    VisitUrgency.CRITICAL: (0.1, 0.2, 0.7),
    VisitUrgency.SOS: (0.1, 0.2, 0.7),
}


def _compute_clinical_quality(
    rating: float, dispute_rate: float, kappa: float
) -> float:
    """
    Computes Q = max(0, (Rating / 5) - (kappa * dispute_rate))
    """
    return max(0.0, (rating / 5.0) - (kappa * dispute_rate))


def _compute_operational_reliability(
    response_rate: float, acceptance_rate: float, mu: float
) -> float:
    """
    Computes R = (mu * response_rate) + ((1 - mu) * acceptance_rate)
    """
    return (mu * response_rate) + ((1 - mu) * acceptance_rate)


def _compute_spatial_proximity(
    capacity: float,
    eta_minutes: Optional[float],
    eta_optimal: float,
    lambda_decay: float,
) -> float:
    """
    Computes P = Capacity_Ratio * exp(-lambda * max(0, ETA - ETA_optimal))
    """
    if capacity <= 0.0 or eta_minutes is None:
        return 0.0
    return capacity * math.exp(-lambda_decay * max(0.0, eta_minutes - eta_optimal))


def _find_nearest_nurse_eta(agency: AgencyProfile, patient_location: Point) -> Optional[float]:
    """
    Finds the minimum ETA from available nurses to the patient.

    Optimization layers:
    1. Pre-filter to nurses with a location
    2. Sort by raw geodesic distance (PostGIS, 0 API calls)
    3. Only call routing API for top 3 nearest candidates
    4. Cache each nurse→patient ETA for 10 minutes
    """
    from django.contrib.gis.db.models.functions import Distance

    nurses_with_location = (
        NurseProfile.objects.filter(
            agency=agency,
            is_available=True,
            last_location__isnull=False,
        )
        .annotate(raw_distance=Distance("last_location", patient_location))
        .order_by("raw_distance")
        .only("id", "last_location")[:3]
    )

    if not nurses_with_location:
        return None

    min_eta = None
    for nurse in nurses_with_location:
        try:
            # Cache layer: avoid redundant routing API calls
            eta_cache_key = f"nurse_eta_{nurse.id}_{patient_location.x:.4f}_{patient_location.y:.4f}"
            cached_eta = cache.get(eta_cache_key)
            if cached_eta is not None:
                minutes = cached_eta
            else:
                eta_data = calculate_nurse_eta(nurse, patient_location)
                if eta_data is not None:
                    minutes = eta_data.duration_minutes
                    cache.set(eta_cache_key, minutes, 600)  # 10 min TTL
                else:
                    continue

            if minutes is not None and (min_eta is None or minutes < min_eta):
                min_eta = minutes
        except Exception as e:
            # Graceful degradation: A routing API failure for one nurse shouldn't crash the entire ranking process.
            # We log the warning and fallback to ignoring this nurse's ETA. The algorithm handles missing ETA gracefully.
            logger.warning(f"Failed to calculate ETA for nurse {nurse.id}: {e}")

    return min_eta


def rank_agencies(
    agencies_queryset: "QuerySet[AgencyProfile]",
    patient_location,
    urgency: VisitUrgency = VisitUrgency.MEDIUM,
) -> List[AgencyScore]:
    """
    Core dynamic vector-based ranking algorithm.
    Calculates composite scores for given agencies and sorts descending.

    Performance Optimization:
    - Expects agencies_queryset to be pre-annotated with _available_nurses_count and _total_nurses_count
    - Falls back to batch query if annotations missing
    - Batches all nurse queries to avoid N+1 pattern
    """
    if not isinstance(urgency, VisitUrgency):
        try:
            urgency = VisitUrgency(urgency)
        except ValueError:
            urgency = VisitUrgency.MEDIUM

    if urgency not in URGENCY_WEIGHTS:
        urgency = VisitUrgency.MEDIUM

    w_q, w_r, w_p = URGENCY_WEIGHTS[urgency]

    results = []
    agency_list = list(agencies_queryset)

    if not agency_list:
        return []

    # Pre-fetch cached stats for speed (batch cache lookup)
    agency_ids = [a.id for a in agency_list]
    cache_keys = {str(ag_id): f"agency_stats_{ag_id}" for ag_id in agency_ids}
    cached_stats_batch = cache.get_many(list(cache_keys.values()))

    # Batch nurse counts if not pre-annotated (eliminates N+1)
    nurse_counts = None
    first_agency = agency_list[0]
    if not hasattr(first_agency, "_available_nurses_count"):
        nurse_counts = (
            NurseProfile.objects.filter(agency__in=agency_ids)
            .values("agency")
            .annotate(
                total=Count("id"), available=Count("id", filter=Q(is_available=True))
            )
        )
        nurse_counts = {item["agency"]: item for item in nurse_counts}

    logger.info(f"Ranking {len(agency_ids)} agencies for urgency {urgency}")

    for agency in agency_list:
        try:
            # Stats (cached or computed)
            cache_key = cache_keys[str(agency.id)]
            stats = cached_stats_batch.get(cache_key)
            if not stats:
                stats = get_agency_operational_stats(agency.id)

            dispute_rate = stats.get("dispute_rate", 0.0)
            response_rate = stats.get("response_rate", 0.5)
            acceptance_rate = stats.get("acceptance_rate", 0.5)

            # Capacity ratio — actual ratio, not binary 0/1
            if nurse_counts is not None:
                counts = nurse_counts.get(agency.id, {"total": 0, "available": 0})
                available_nurses_count = counts["available"]
                total_nurses_count = counts["total"]
            else:
                available_nurses_count = (
                    getattr(agency, "_available_nurses_count", 0) or 0
                )
                total_nurses_count = getattr(agency, "_total_nurses_count", 1) or 1

            capacity_ratio = available_nurses_count / max(total_nurses_count, 1)

            eta_minutes = None
            if available_nurses_count > 0 and patient_location is not None:
                eta_minutes = _find_nearest_nurse_eta(agency, patient_location)

            # Components — default rating 0.0 (not 5.0) to avoid unfair advantage for new agencies
            rating = float(getattr(agency, "rating", 0.0) or 0.0)
            q_vector = _compute_clinical_quality(
                rating, dispute_rate, ALGORITHM_CONSTANTS.kappa
            )
            r_vector = _compute_operational_reliability(
                response_rate, acceptance_rate, ALGORITHM_CONSTANTS.mu
            )
            p_vector = _compute_spatial_proximity(
                capacity_ratio,
                eta_minutes,
                ALGORITHM_CONSTANTS.ETA_optimal,
                ALGORITHM_CONSTANTS.lambda_decay,
            )

            # Total score
            total_score = (w_q * q_vector) + (w_r * r_vector) + (w_p * p_vector)

            debug_info = {
                "rating": rating,
                "dispute_rate": dispute_rate,
                "response_rate": response_rate,
                "acceptance_rate": acceptance_rate,
                "available_nurses": available_nurses_count,
                "weights": {"w_q": w_q, "w_r": w_r, "w_p": w_p},
            }

            results.append(
                AgencyScore(
                    agency_id=agency.id,
                    score=total_score,
                    eta=eta_minutes,
                    clinical_quality=q_vector,
                    operational_reliability=r_vector,
                    spatial_proximity=p_vector,
                    debug_info=debug_info,
                )
            )

            logger.debug(
                f"Agency {agency.id} scored {total_score:.2f} (Q:{q_vector:.2f}, R:{r_vector:.2f}, P:{p_vector:.2f})"
            )

        except Exception as e:
            logger.error(f"Error ranking agency {agency.id}: {e}")

    # Sort primarily by score descending
    results.sort(key=lambda x: x.score, reverse=True)

    return results
