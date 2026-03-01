import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.translation import gettext_lazy as _

from users.models import DispatchMode, NurseProfile, UserRole, VerificationStatus
from visits.models import Visit, VisitStatus
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
        Finds all eligible nurses within the agency and broadcasts the request to them.
        """
        agency = visit.agency
        
        # 1. Find all active and verified nurses belonging to this agency
        # We also filter by those who are "is_available"
        eligible_nurses = NurseProfile.objects.filter(
            agency=agency,
            is_available=True,
            verification_status=VerificationStatus.VERIFIED
        )

        if not eligible_nurses.exists():
            logger.warning("No eligible nurses found for agency %s to handle visit %s", agency.id, visit.id)
            # In a real system, we might notify the agency admin that no nurses are available
            self._notify_agency_admin(visit, "no_nurses_available")
            return

        # 2. Optionally filter by proximity using GeoMatchingService
        # For Tier 2 B2B2C, we broadcast to ALL agency nurses in the area.
        # We'll use the patient's location.
        lat, lng = visit.location.y, visit.location.x
        
        # We can limit to a reasonable radius (e.g. 15km) even if they are in the agency polygon
        candidates = self.geo_service.find_candidates(lat, lng, radius_km=15.0)
        candidate_ids = [c['nurse_id'] for c in candidates]
        
        # Intersect agency nurses with nearby nurses
        final_nurses = eligible_nurses.filter(id__in=candidate_ids)
        
        if not final_nurses.exists():
            # Fallback to all agency staff if none are in the "immediate" radius? 
            # Or just use the nearest one.
            final_nurses = eligible_nurses[:5] # Notify top 5 as fallback

        # 3. Broadcast to nurses via WebSockets
        from visits.serializers import VisitResponseSerializer
        data = {
            "type": "visit_request",
            "data": {
                "visit": VisitResponseSerializer(visit).data,
                "expires_in": 60 # 60 seconds to accept
            }
        }

        for nurse in final_nurses:
            group_name = f"nurse_{nurse.id}"
            try:
                async_to_sync(self.channel_layer.group_send)(
                    group_name,
                    {
                        "type": "visit.request",
                        "data": data["data"]
                    }
                )
                logger.debug("Broadcasted visit %s to nurse %s", visit.id, nurse.id)
            except Exception as e:
                # Log but don't fail the dispatch if WebSocket fails
                logger.error(
                    "Failed to broadcast visit %s to nurse %s via WebSocket: %s",
                    visit.id, nurse.id, str(e)
                )
                continue  # Continue with other nurses

        # 4. Also notify agency admin that auto-dispatch is in progress
        self._notify_agency_admin(visit, "auto_dispatch_started")

    def _handle_manual_dispatch(self, visit: Visit):
        """
        Notifies the agency admin that a new visit is awaiting manual nurse assignment.
        """
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
