import decimal
import logging
from typing import Dict, Any, List
from uuid import UUID

from celery import shared_task
from django.core.cache import cache
from django.db.models import Count, Q, Case, When, IntegerField, OuterRef, Subquery

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


class AgencyStatsInjector:
    """
    Service class responsible for bulk-injecting operational stats onto 
    AgencyProfile instances to prevent N+1 queries during ranking.
    """

    @classmethod
    def bulk_inject_operational_stats(cls, agencies: List[AgencyProfile]) -> List[AgencyProfile]:
        if not agencies:
            return agencies

        agency_ids = [agency.id for agency in agencies]
        cache_keys = {str(agency_id): f"agency_stats_{agency_id}" for agency_id in agency_ids}
        
        # Redis First: Fetch from cache
        cached_stats_batch = cache.get_many(list(cache_keys.values()))
        
        missed_ids = []
        for agency_id in agency_ids:
            cache_key = cache_keys[str(agency_id)]
            if cache_key not in cached_stats_batch:
                missed_ids.append(agency_id)
                
        db_stats_map = {}
        if missed_ids:
            # Graceful Degradation: Compute for cache misses in a SINGLE query
            recent_visits = Visit.objects.filter(
                agency_id=OuterRef('agency_id')
            ).order_by('-created_at').values('id')[:100]
            
            computed_stats = Visit.objects.filter(
                id__in=Subquery(recent_visits)
            ).values('agency_id').annotate(
                total=Count('id'),
                responded=Count('id', filter=Q(nurse__isnull=False)),
                accepted=Count(
                    'id',
                    filter=Q(
                        status__in=[
                            VisitStatus.ACCEPTED,
                            VisitStatus.EN_ROUTE,
                            VisitStatus.IN_PROGRESS,
                            VisitStatus.COMPLETED,
                        ]
                    )
                ),
                disputed=Count('id', filter=Q(status=VisitStatus.CANCELLED, nurse__isnull=False))
            )

            # Map the results
            for row in computed_stats:
                ag_id = row['agency_id']
                total = float(row['total'])
                if total > 0:
                    db_stats_map[ag_id] = {
                        "response_rate": row['responded'] / total,
                        "acceptance_rate": row['accepted'] / total,
                        "dispute_rate": row['disputed'] / total,
                    }
                    
                # Store back in cache to self-heal
                cache_key = cache_keys[str(ag_id)]
                cache.set(cache_key, db_stats_map.get(ag_id, {
                    "response_rate": 0.5, 
                    "acceptance_rate": 0.5, 
                    "dispute_rate": 0.0
                }), CACHE_TTL)

        # Inject into objects
        for agency in agencies:
            cache_key = cache_keys[str(agency.id)]
            
            if cache_key in cached_stats_batch:
                stats = cached_stats_batch[cache_key]
            else:
                stats = db_stats_map.get(agency.id, {
                    "response_rate": 0.5, 
                    "acceptance_rate": 0.5, 
                    "dispute_rate": 0.0
                })
                
            # Decimal Strictness & Zero-History Safeguard
            agency.cached_response_rate = decimal.Decimal(str(stats.get("response_rate", 0.5)))
            agency.cached_acceptance_rate = decimal.Decimal(str(stats.get("acceptance_rate", 0.5)))
            agency.cached_dispute_rate = decimal.Decimal(str(stats.get("dispute_rate", 0.0)))
            
            # Cached capacity ratio calculated purely in-memory
            # nurseprofile_set is assumed to be prefetched
            nurses = agency.nurseprofile_set.all()
            total_nurses = len(nurses)
            if total_nurses > 0:
                available_nurses = len([n for n in nurses if n.is_available])
                capacity_ratio = available_nurses / total_nurses
            else:
                capacity_ratio = 0.0
                
            agency.cached_capacity_ratio = decimal.Decimal(str(capacity_ratio))
            
        return agencies
