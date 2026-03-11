import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from users.models import DispatchMode, NurseProfile, VerificationStatus
from visits.models import Visit
from .matching import GeoMatchingService

logger = logging.getLogger(__name__)

class DispatchEngine:
    """
    Handles Tier 2 dispatching logic.
    Decides whether to auto-dispatch to agency nurses or notify agency admins for manual selection.
    """
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.geo_service = GeoMatchingService()

    def trigger_dispatch(self, visit: Visit):
        """
        Primary entry point for dispatching a visit after it has been assigned to an agency.
        """
        agency = visit.agency
        if not agency:
            logger.error("Visit %s has no assigned agency for dispatch.", visit.id)
            return

        logger.info("Triggering dispatch for visit %s via agency %s (Mode: %s)", 
                    visit.id, agency.id, agency.dispatch_mode)

        if agency.dispatch_mode == DispatchMode.AUTO:
            self._handle_auto_dispatch(visit)
        else:
            self._handle_manual_dispatch(visit)

    def _handle_auto_dispatch(self, visit: Visit):
        """
        Uses PostGIS spatial engine to find the 5 nearest nurses and create auto-dispatch offers.
        """
        from django.utils import timezone
        from visits.services.dispatch_service import auto_dispatch_to_nurses
        from visits.tasks import re_route_visit
        
        # Set the routing timestamp
        visit.routed_at = timezone.now()
        visit.save(update_fields=['routed_at', 'updated_at'])

        success = auto_dispatch_to_nurses(visit.id, visit.agency_id)
        
        # Notify agency admin
        self._notify_agency_admin(visit, "auto_dispatch_started")

        if not success:
            logger.warning("Auto-dispatch found zero nurses for visit %s. Triggering immediate re-route.", visit.id)
            re_route_visit.delay(str(visit.id), str(visit.agency_id))

    def _handle_manual_dispatch(self, visit: Visit):
        """
        Notifies the agency admin that a new visit is awaiting manual nurse assignment.
        """
        from django.utils import timezone
        from visits.tasks import re_route_visit

        # Set the routing timestamp
        visit.routed_at = timezone.now()
        visit.save(update_fields=['routed_at', 'updated_at'])

        # Schedule the escalation timer (300 seconds)
        re_route_visit.apply_async(
            args=[str(visit.id), str(visit.agency_id)],
            countdown=300
        )
        logger.info(
            "Scheduled escalation timer for visit %s at agency %s (300s countdown)",
            visit.id, visit.agency_id
        )

        self._notify_agency_admin(visit, "manual_assignment_required")

    def _notify_agency_admin(self, visit: Visit, alert_type: str):
        """
        Sends a WebSocket message to the agency admin group.
        """
        agency = visit.agency
        from visits.serializers import VisitResponseSerializer
        
        group_name = f"agency_{agency.id}"
        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    "type": "visit.new",
                    "data": {
                        "alert_type": alert_type,
                        "visit": VisitResponseSerializer(visit).data
                    }
                }
            )
            logger.debug("Notified agency %s admin of visit %s (%s)", agency.id, visit.id, alert_type)
        except Exception as e:
            # Log but don't fail the dispatch if WebSocket fails
            logger.error(
                "Failed to notify agency %s admin of visit %s (%s): %s",
                agency.id, visit.id, alert_type, str(e)
            )
