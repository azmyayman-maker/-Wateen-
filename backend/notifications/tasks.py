import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    queue="notifications",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    max_retries=3,
    acks_late=True,
)
def send_notification_task(self, user_ids: list, event_type: str, context: dict) -> int:
    """
    Send push notifications to multiple users.
    
    Args:
        user_ids: List of user UUIDs
        event_type: The NotificationEventType value
        context: Dictionary of context variables for template rendering
    
    Returns:
        Count of sent notifications
    """
    from notifications.services.push_service import send_to_users

    logger.info(
        "Notification task [%s] → %d users, event=%s",
        self.request.id, len(user_ids), event_type,
    )

    try:
        logs = send_to_users(user_ids, event_type, context)
        sent_count = len([log for log in logs if log.status == "SENT"])
        logger.info("Notification task completed: %d sent", sent_count)
        return sent_count
    except Exception as exc:
        logger.error(
            "Notification task FAILED after %d retries: %s",
            self.request.retries, str(exc),
        )
        raise


@shared_task(queue="notifications")
def cleanup_stale_tokens() -> int:
    """
    Clean up stale device tokens that haven't been active recently.
    
    Returns:
        Count of tokens deactivated
    """
    stale_days = getattr(settings, "NOTIFICATION_STALE_TOKEN_DAYS", 30)
    cutoff = timezone.now() - timedelta(days=stale_days)

    from notifications.models import DeviceToken

    count = DeviceToken.objects.filter(
        is_active=True,
        last_active__lt=cutoff,
    ).update(is_active=False)

    logger.info("Cleaned up %d stale device tokens", count)
    return count
