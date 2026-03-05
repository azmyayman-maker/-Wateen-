"""
Push Notification Service — Stub for future FCM/web push integration.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> bool:
    """
    Send a push notification to all active devices for a user.
    
    This is a stub — integrate with Firebase Cloud Messaging (FCM)
    or Web Push API when ready.
    
    Args:
        user_id: UUID of the user to notify
        title: Notification title (Arabic)
        body: Notification body (Arabic)
        data: Optional payload (e.g., visit_id, action type)
    
    Returns:
        True if at least one notification was sent
    """
    # TODO: Implement FCM integration
    # from notifications.models import DeviceToken
    # tokens = DeviceToken.objects.filter(user_id=user_id, is_active=True)
    # for token in tokens:
    #     fcm.send(token.token, title=title, body=body, data=data)
    
    logger.info(
        "Push notification (stub): user=%s title=%s",
        user_id, title,
    )
    return False
