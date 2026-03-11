import logging
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(queue='notifications')
def send_push_notification(user_id: str, payload: dict) -> bool:
    """
    Sends an FCM push notification to the user's devices.
    Used for waking up the app in background mode.
    """
    # Stub for FCM integration
    logger.info(f"FCM Push Notification sent to user {user_id}. Payload: {payload}")
    return True
