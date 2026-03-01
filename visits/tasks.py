import logging
from celery import shared_task
from django.utils import timezone
from visits.models import Visit, VisitStatus, Transaction, TransactionStatus
from users.models import AgencyProfile, AgencyStatus
from .services.dispatch import DispatchEngine

logger = logging.getLogger(__name__)

@shared_task(name="visits.tasks.re_route_visit")
def re_route_visit(visit_id: str):
    """
    Background task to handle dispatch timeouts.
    If a visit is still in PENDING_AGENCY after the timeout, re-route to the next best agency.
    """
    try:
        visit = Visit.objects.get(id=visit_id)
    except Visit.DoesNotExist:
        logger.error(f"Task re_route_visit failed: Visit {visit_id} not found.")
        return

    # Only re-route if still pending agency
    if visit.status != VisitStatus.PENDING_AGENCY:
        logger.info(f"Visit {visit_id} is in status {visit.status}. No re-routing needed.")
        return

    logger.info(f"Dispatch timeout for visit {visit_id}. Attempting re-routing.")

    # 1. Find agencies that have NOT been tried yet
    # For MVP, we'll exclude the current agency and find next by rating
    current_agency_id = visit.agency_id
    
    # Re-run spatial query but exclude current agency
    location = visit.location
    eligible_agencies = AgencyProfile.objects.filter(
        status=AgencyStatus.VERIFIED,
        coverage_polygon__intersects=location
    ).exclude(id=current_agency_id).order_by('-rating')

    next_agency = eligible_agencies.first()

    if next_agency:
        logger.info(f"Re-routing visit {visit_id} from agency {current_agency_id} to {next_agency.id}")
        visit.agency = next_agency
        visit.save(update_fields=['agency', 'updated_at'])
        
        # Trigger dispatch for the new agency
        dispatch_engine = DispatchEngine()
        dispatch_engine.trigger_dispatch(visit)
        
        # Schedule next timeout (recursive check)
        re_route_visit.apply_async((visit.id,), countdown=300) # 5 more minutes
    else:
        logger.warning(f"No more eligible agencies for visit {visit_id}. Marking as failed.")
        visit.transition_to(VisitStatus.CANCELLED)
        # Notify patient via WebSockets
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"patient_{visit.patient_id}",
            {
                "type": "visit.update",
                "data": {
                    "status": "FAILED_NO_AGENCY",
                    "detail": "No agencies available in your area at this time."
                }
            }
        )

@shared_task(name="visits.tasks.process_settlements")
def process_settlements():
    """
    Periodic task to settle COMPLETED visits.
    """
    from .services.settlement import SettlementService
    
    # Find completed visits with pending transactions
    pending_visits = Visit.objects.filter(
        status=VisitStatus.COMPLETED,
        transaction__status=TransactionStatus.ESCROWED
    )
    
    count = 0
    for visit in pending_visits:
        if SettlementService.settle_visit(visit):
            count += 1
            
    return f"Settled {count} visits."
