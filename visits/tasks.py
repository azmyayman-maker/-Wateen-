import logging
from celery import shared_task
from visits.models import Visit, VisitStatus, TransactionStatus
from users.models import AgencyProfile, AgencyStatus
from .services.dispatch import DispatchEngine
from .services.matching import GeoMatchingService

logger = logging.getLogger(__name__)


@shared_task(name="visits.tasks.re_evaluate_pending_visits")
def re_evaluate_pending_visits(agency_id: str):
    """
    Background task triggered when an agency updates its coverage polygon.
    Re-evaluates any visits strictly in PENDING_AGENCY state that might now
    fall inside or outside the new coverage area.
    """
    try:
        agency = AgencyProfile.objects.get(id=agency_id)
        logger.info(f"Re-evaluating pending visits for agency {agency_id} after coverage update.")
        # TODO: Implement full re-evaluation logic (Issue #XXX, Phase 4)
        # Currently stubbed - needs to query PENDING_AGENCY visits and re-run spatial matching.
    except AgencyProfile.DoesNotExist:
        logger.error(f"Task re_evaluate_pending_visits failed: Agency {agency_id} not found.")


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
        logger.info(
            f"Visit {visit_id} is in status {visit.status}. No re-routing needed."
        )
        return

    logger.info(f"Dispatch timeout for visit {visit_id}. Attempting re-routing.")

    # 1. Find agencies that have NOT been tried yet
    # For MVP, we'll exclude the current agency and find next by rating
    current_agency_id = visit.agency_id

    # Re-run spatial query but exclude current agency
    location = visit.location
    eligible_agencies = (
        AgencyProfile.objects.filter(
            status=AgencyStatus.VERIFIED, coverage_polygon__intersects=location
        )
        .exclude(id=current_agency_id)
        .order_by("-rating")
    )

    next_agency = eligible_agencies.first()

    MAX_REROUTE_ATTEMPTS = 3

    # Check retry limit to prevent infinite loops
    if visit.reroute_attempts >= MAX_REROUTE_ATTEMPTS:
        logger.warning(
            f"Visit {visit_id} has exceeded max re-routing attempts. Marking as failed."
        )
        visit.transition_to(VisitStatus.CANCELLED)
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"patient_{visit.patient_id}",
            {
                "type": "visit.update",
                "data": {
                    "status": "FAILED_MAX_REROUTES",
                    "detail": "No agencies available after multiple attempts.",
                },
            },
        )
        return

    if next_agency:
        logger.info(
            f"Re-routing visit {visit_id} from agency {current_agency_id} to {next_agency.id}"
        )
        visit.agency = next_agency
        visit.reroute_attempts += 1
        visit.save(update_fields=["agency", "updated_at", "reroute_attempts"])

        # Trigger dispatch for the new agency
        dispatch_engine = DispatchEngine()
        dispatch_engine.trigger_dispatch(visit)

        # Schedule next timeout (recursive check) - use string UUID
        re_route_visit.apply_async((str(visit.id),), countdown=300)  # 5 more minutes
    else:
        logger.warning(
            f"No more eligible agencies for visit {visit_id}. Marking as failed."
        )
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
                    "detail": "No agencies available in your area at this time.",
                },
            },
        )


@shared_task(name="visits.tasks.process_settlements")
def process_settlements():
    """
    Periodic task to settle COMPLETED visits.
    """
    from .services.settlement import SettlementService

    # Find completed visits with pending transactions
    pending_visits = Visit.objects.filter(
        status=VisitStatus.COMPLETED, transaction__status=TransactionStatus.ESCROWED
    )

    count = 0
    for visit in pending_visits:
        if SettlementService.settle_visit(visit):
            count += 1

    return f"Settled {count} visits."


@shared_task(name="visits.tasks.expire_dispatch_offer")
def expire_dispatch_offer(offer_id: str):
    """
    Background task to expire a dispatch offer after 60s timeout.
    Scheduled with countdown=60 when the offer is created.
    """
    from visits.models import DispatchOffer, OfferStatus

    try:
        offer = DispatchOffer.objects.get(id=offer_id)
    except DispatchOffer.DoesNotExist:
        logger.error("Offer %s not found for expiry.", offer_id)
        return

    if offer.status != OfferStatus.PENDING:
        logger.debug("Offer %s already resolved (status=%s).", offer_id, offer.status)
        return

    offer.status = OfferStatus.EXPIRED
    offer.save(update_fields=["status"])
    logger.info("Expired dispatch offer %s for visit %s.", offer_id, offer.visit_id)

    # Check if all offers for this visit are resolved
    pending = DispatchOffer.objects.filter(
        visit=offer.visit, status=OfferStatus.PENDING
    ).count()

    if pending == 0:
        # All offers expired/rejected — check if any was accepted
        accepted = DispatchOffer.objects.filter(
            visit=offer.visit, status=OfferStatus.ACCEPTED
        ).exists()
        if not accepted:
            logger.info(
                "All offers expired for visit %s. Triggering re-route.",
                offer.visit_id,
            )
            visit = offer.visit
            visit.reroute_attempts += 1
            visit.save(update_fields=["reroute_attempts"])
            re_route_visit.apply_async((str(visit.id),), countdown=5)


@shared_task(name="visits.tasks.auto_dispatch_to_nurses")
def auto_dispatch_to_nurses(visit_id: str, agency_id: str):
    """
    Create DispatchOffer records for the top-5 nearest nurses and notify them.
    Scheduled after agency routing is complete.
    """
    from visits.models import DispatchOffer, OfferStatus
    from django.utils import timezone
    from datetime import timedelta

    try:
        visit = Visit.objects.get(id=visit_id)
    except Visit.DoesNotExist:
        logger.error("Visit %s not found for nurse dispatch.", visit_id)
        return

    if visit.status != VisitStatus.PENDING_AGENCY:
        logger.info("Visit %s no longer pending. Skipping dispatch.", visit_id)
        return

    # Find nearest available nurses via GeoMatchingService
    geo_service = GeoMatchingService()
    if visit.location:
        candidates = geo_service.find_candidates(
            visit.location.y, visit.location.x, radius_km=15.0
        )
    else:
        candidates = []

    if not candidates:
        logger.warning("No nearby nurses found for visit %s. Notifying agency.", visit_id)
        dispatch_engine = DispatchEngine()
        dispatch_engine._notify_agency_admin(visit, "no_nurses_available")
        return

    # Create offers for top-5 nearest nurses
    now = timezone.now()
    offers_created = []
    for candidate in candidates[:5]:
        nurse_id = candidate["nurse_id"]
        try:
            offer = DispatchOffer.objects.create(
                visit=visit,
                nurse_id=nurse_id,
                status=OfferStatus.PENDING,
                expires_at=now + timedelta(seconds=60),
            )
            offers_created.append(offer)

            # Schedule expiry task
            expire_dispatch_offer.apply_async(
                (str(offer.id),), countdown=60
            )
        except Exception as e:
            logger.error("Failed to create offer for nurse %s: %s", nurse_id, e)

    # Notify nurses via WebSocket
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from visits.serializers import VisitResponseSerializer

    channel_layer = get_channel_layer()
    visit_data = VisitResponseSerializer(visit).data

    for offer in offers_created:
        group_name = f"nurse_{offer.nurse_id}"
        try:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "visit.request",
                    "data": {
                        "offer_id": str(offer.id),
                        "visit": visit_data,
                        "expires_in": 60,
                    },
                },
            )
        except Exception as e:
            logger.error(
                "Failed to notify nurse %s of offer %s: %s",
                offer.nurse_id, offer.id, e,
            )

    logger.info(
        "Created %d dispatch offers for visit %s.",
        len(offers_created), visit_id,
    )
