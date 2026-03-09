from celery import shared_task
from django.db import transaction
import logging

from visits.models import Visit, VisitStatus
from users.models import AgencyProfile

logger = logging.getLogger(__name__)

# NOTE (Phase 2): Legacy tasks such as `re_evaluate_pending_visits`, `re_route_visit`,
# `process_settlements`, `expire_dispatch_offer`, and `auto_dispatch_to_nurses` have been
# removed as part of the Visit Request & Pricing rewrite.
# Their advanced routing logic is deliberately deferred to Phase 5: Real-Time Sockets.
# The current `dispatch_visit` acts as the simple Phase 2 MVP agency assignment.

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="dispatch"
)
def dispatch_visit(self, visit_id: str):
    """
    Celery task spawned asynchronously post-DB commit.
    Locates the best-fit covering agency and routes the ticket to them.
    If multiple agencies match, it could iterate or fan out.
    """

    try:
        visit = Visit.objects.get(id=visit_id)
        if visit.status != VisitStatus.PENDING_AGENCY:
            logger.warning(f"Visit {visit_id} is not pending. Aborting dispatch.")
            return

        # Find agencies whose coverage_polygon encompasses the visit location
        agencies = AgencyProfile.objects.filter(
            coverage_polygon__contains=visit.location,
            is_active=True
        )

        # Distribute logic (For now, just pick the first or create an offer layer)
        # Using simple DispatchOffer logic if it exists, or update status
        agency = agencies.first()
        
        if not agency:
            # In a real system, might flag for manual review or cancel
            logger.error(f"No active agencies found for Visit {visit_id} at {visit.location}.")
            return
            
        visit.agency = agency
        visit.status = VisitStatus.PENDING_NURSE
        visit.save(update_fields=["agency", "status", "updated_at"])

        logger.info(f"Dispatched Visit {visit_id} to Agency {agency.agency_name}.")

    except Visit.DoesNotExist:
        logger.error(f"Visit {visit_id} NOT FOUND inside Celery Task! Atomic commit race condition breached.")
    except Exception as exc:
        logger.error(f"Dispatch failed for Visit {visit_id}: {exc}")
        raise self.retry(exc=exc)
