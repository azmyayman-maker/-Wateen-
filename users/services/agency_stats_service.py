import logging
from typing import Dict, Any
from uuid import UUID

from celery import shared_task
from django.core.cache import cache
from django.db.models import Count, Q, Case, When, IntegerField

from users.models import AgencyProfile, AgencyStatus
from visits.models import Visit, VisitStatus

logger = logging.getLogger(__name__)

CACHE_TTL = 3600  # 1 hour


def _compute_stats_from_db(agency_id: UUID) -> Dict[str, float]:
    """
    Computes operational metrics for an agency based on its last 100 visits.
    Returns default values if the agency has no history.

    Optimized: Single query with conditional aggregation instead of N+1 count queries.
    """
    defaults = {"response_rate": 0.5, "acceptance_rate": 0.5, "dispute_rate": 0.0}
    try:
        # Single query with conditional aggregation for all metrics
        stats = (
            Visit.objects.filter(agency_id=agency_id)
            .order_by("-created_at")[:100]
            .aggregate(
                total=Count("id"),
                responded=Count("id", filter=Q(nurse__isnull=False)),
                accepted=Count(
                    "id",
                    filter=Q(
                        status__in=[
                            VisitStatus.ACCEPTED,
                            VisitStatus.EN_ROUTE,
                            VisitStatus.IN_PROGRESS,
                            VisitStatus.COMPLETED,
                        ]
                    ),
                ),
                disputed=Count(
                    "id", filter=Q(status=VisitStatus.CANCELLED, nurse__isnull=False)
                ),
            )
        )

        total = stats["total"]
        if total == 0:
            return defaults

        total_f = float(total)
        return {
            "response_rate": stats["responded"] / total_f,
            "acceptance_rate": stats["accepted"] / total_f,
            "dispute_rate": stats["disputed"] / total_f,
        }

    except Exception as e:
        logger.error(f"Failed to compute stats for agency {agency_id}: {e}")
        return defaults


def get_agency_operational_stats(agency_id: UUID) -> Dict[str, float]:
    """
    Retrieves operational stats from cache, or computes and caches them on miss.
    """
    cache_key = f"agency_stats_{agency_id}"
    try:
        stats = cache.get(cache_key)
        if stats is not None:
            return stats
    except Exception as e:
        logger.warning(f"Redis cache inaccessible for stats lookup: {e}")

    # Cache miss or failure, compute from DB
    stats = _compute_stats_from_db(agency_id)

    try:
        cache.set(cache_key, stats, CACHE_TTL)
    except Exception as e:
        logger.warning(f"Redis cache inaccessible for stats storage: {e}")

    return stats


@shared_task
def refresh_agency_stats() -> int:
    """
    Periodic task to warm the cache for all verified agencies.
    Returns the number of agencies refreshed.
    """
    agencies = AgencyProfile.objects.filter(status=AgencyStatus.VERIFIED).values_list(
        "id", flat=True
    )
    count = 0
    for agency_id in agencies:
        stats = _compute_stats_from_db(agency_id)
        cache_key = f"agency_stats_{agency_id}"
        try:
            cache.set(cache_key, stats, CACHE_TTL)
            count += 1
        except Exception as e:
            logger.error(
                f"Failed to update cache for agency {agency_id} during refresh: {e}"
            )

    logger.info(f"Successfully refreshed operational stats for {count} agencies.")
    return count
