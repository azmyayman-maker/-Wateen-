import logging
from datetime import timedelta
from uuid import UUID

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.gis.db.models.functions import Distance
from django.utils import timezone

from notifications.tasks import send_notification_task
from users.models import NurseProfile, VerificationStatus
from visits.models import DispatchOffer, Visit
from visits.tasks import check_dispatch_timeout

logger = logging.getLogger(__name__)

def auto_dispatch_to_nurses(visit_id: UUID, agency_id: UUID) -> bool:
    """
    Spatial Auto-dispatch to the 5 nearest available nurses for a given agency.
    Creates time-limited DispatchOffers and triggers notifications.
    """
    try:
        visit = Visit.objects.get(id=visit_id)
    except Visit.DoesNotExist:
        logger.error(f"Visit {visit_id} does not exist.")
        return False

    if not visit.location:
        logger.error(f"Visit {visit_id} has no location set for spatial dispatch.")
        return False

    nearest_nurses = NurseProfile.objects.filter(
        agency_id=agency_id,
        is_available=True,
        verification_status=VerificationStatus.VERIFIED,
        last_location__isnull=False
    ).annotate(
        distance=Distance('last_location', visit.location)
    ).order_by('distance')[:5]

    nearest_nurses_list = list(nearest_nurses)

    if not nearest_nurses_list:
        logger.warning(f"No available nurses found for agency {agency_id} near visit {visit_id}.")
        return False

    expires_in = 60
    expires_at = timezone.now() + timedelta(seconds=expires_in)

    channel_layer = get_channel_layer()
    offers_created = False

    from visits.serializers import VisitResponseSerializer
    visit_data = VisitResponseSerializer(visit).data

    for nurse in nearest_nurses_list:
        offer = DispatchOffer.objects.create(
            visit=visit,
            nurse=nurse,
            expires_at=expires_at
        )
        offers_created = True

        ws_payload = {
            "type": "visit.request",
            "data": {
                "offer_id": str(offer.id),
                "visit": visit_data,
                "expires_in": expires_in
            }
        }
        try:
            async_to_sync(channel_layer.group_send)(
                f"nurse_{nurse.id}",
                ws_payload
            )
        except Exception as e:
            logger.error(f"Failed to send websocket for offer {offer.id} to nurse {nurse.user_id}: {e}")

        fcm_payload = {
            "type": "dispatch_offer",
            "offer_id": str(offer.id),
            "visit_id": str(visit.id),
            "expires_in": expires_in
        }
        try:
            send_notification_task.delay([str(nurse.user_id)], "DISPATCH_OFFER", fcm_payload)
        except Exception as e:
            logger.error(f"Failed to trigger FCM for offer {offer.id} to nurse {nurse.user_id}: {e}")

    if offers_created:
        check_dispatch_timeout.apply_async(args=[str(visit_id)], countdown=expires_in)
        return True

    return False
