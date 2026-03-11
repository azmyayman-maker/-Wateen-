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
        visit.status = VisitStatus.PENDING_AGENCY
        
        from django.utils import timezone
        visit.routed_at = timezone.now()
        visit.save(update_fields=["agency", "status", "routed_at", "updated_at"])

        from users.models import DispatchMode
        if agency.dispatch_mode == DispatchMode.MANUAL:
            re_route_visit.apply_async(
                args=[str(visit.id), str(agency.id)],
                countdown=300
            )

        logger.info(f"Dispatched Visit {visit_id} to Agency {agency.agency_name}.")

    except Visit.DoesNotExist:
        logger.error(f"Visit {visit_id} NOT FOUND inside Celery Task! Atomic commit race condition breached.")
    except Exception as exc:
        logger.error(f"Dispatch failed for Visit {visit_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, queue="dispatch")
def re_route_visit(self, visit_id: str, agency_id: str):
    from django.utils import timezone
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from users.models import DispatchMode
    
    try:
        with transaction.atomic():
            visit = Visit.objects.select_for_update().get(id=visit_id)
            if visit.status != VisitStatus.PENDING_AGENCY or str(visit.agency_id) != agency_id:
                logger.info("Escalation timer ignored for visit %s at agency %s (status=%s, current_agency=%s)", visit_id, agency_id, visit.status, visit.agency_id)
                return

            logger.info("Escalation timer fired for visit %s at agency %s", visit_id, agency_id)
            
            old_agency_id = visit.agency_id
            visit.reroute_attempts += 1
            
            from visits.services.matching import rank_agencies
            candidates = AgencyProfile.objects.filter(
                coverage_polygon__contains=visit.location,
                is_active=True,
            ).exclude(id=old_agency_id)
            
            ranked = rank_agencies(candidates, visit.location, urgency=visit.urgency)
            
            channel_layer = get_channel_layer()

            if ranked:
                next_agency = ranked[0]["agency"]
                visit.agency = next_agency
                visit.routed_at = timezone.now()
                visit.save(update_fields=["agency", "routed_at", "reroute_attempts", "updated_at"])
                
                if next_agency.dispatch_mode == DispatchMode.MANUAL:
                    re_route_visit.apply_async(
                        args=[str(visit.id), str(next_agency.id)],
                        countdown=300
                    )
                
                # Notify new agency
                try:
                    async_to_sync(channel_layer.group_send)(
                        f"agency_{next_agency.id}",
                        {
                            "type": "visit.new",
                            "data": {
                                "alert_type": "manual_assignment_required",
                                "visit_id": str(visit.id)
                            }
                        }
                    )
                except Exception as e:
                    logger.error("Failed to notify new agency %s via websocket: %s", next_agency.id, e)
                    
                logger.info("Visit %s rerouted to agency %s (attempt #%d)", visit.id, next_agency.id, visit.reroute_attempts)
            else:
                visit.agency = None
                visit.save(update_fields=["agency", "reroute_attempts", "updated_at"])
                visit.transition_to(VisitStatus.CANCELLED)
                
                # Notify patient
                try:
                    async_to_sync(channel_layer.group_send)(
                        f"patient_{visit.patient.user_id}",
                        {
                            "type": "visit.cancelled",
                            "data": {
                                "visit_id": str(visit.id),
                                "reason": "No agencies available"
                            }
                        }
                    )
                except Exception as e:
                    logger.error("Failed to notify patient %s via websocket: %s", visit.patient.user_id, e)
                    
                logger.info("Visit %s cancelled — no agencies remaining", visit.id)

            # Notify old agency
            try:
                async_to_sync(channel_layer.group_send)(
                    f"agency_{old_agency_id}",
                    {
                        "type": "visit.revoked",
                        "data": {
                            "alert_type": "visit_revoked",
                            "visit_id": str(visit.id)
                        }
                    }
                )
            except Exception as e:
                logger.error("Failed to notify old agency %s via websocket: %s", old_agency_id, e)

    except Visit.DoesNotExist:
        logger.error(f"Visit {visit_id} NOT FOUND inside re_route_visit Task.")
    except Exception as exc:
        logger.error(f"Reroute failed for Visit {visit_id}: {exc}")
        raise self.retry(exc=exc)

