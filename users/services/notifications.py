import logging
from celery import shared_task
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class AgencyNotificationService:
    """
    Service Layer for handling SuperAdmin and Agency notifications.
    Uses Celery for async execution and Channels for real-time delivery.
    """

    @staticmethod
    def notify_superadmins_of_new_registration(agency_id: str, manager_name: str):
        """
        Trigger an asynchronous task to notify all SuperAdmins of a new agency registration.
        """
        send_superadmin_notification_task.delay(
            agency_id=agency_id,
            message=f"New agency registration: {manager_name} (ID: {agency_id}) requires KYC review.",
            notification_type="NEW_REGISTRATION"
        )

@shared_task
def send_superadmin_notification_task(agency_id: str, message: str, notification_type: str):
    """
    Celery task to deliver real-time notifications via WebSocket (Django Channels).
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        logger.warning("Channel layer not configured. Notification not sent via WebSocket.")
        return

    # Broadcast to the 'superadmins' group
    try:
        async_to_sync(channel_layer.group_send)(
            "superadmins",
            {
                "type": "notification.message",
                "notification": {
                    "id": agency_id,
                    "type": notification_type,
                    "text": message,
                    "timestamp": None # Could add isoformat timestamp
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to send SuperAdmin notification: {e}")
