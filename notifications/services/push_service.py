"""
Push Notification Service — Firebase Cloud Messaging integration.
"""

import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# PII fields that must NOT be sent in push notification data payloads
PII_FIELDS = frozenset([
    "phone",
    "national_id", 
    "email",
    "medical_notes",
    "address",
    "first_name_ar",
    "last_name_ar",
    "full_name",
])


def _build_data_payload(context: dict) -> dict:
    """Build the data payload for FCM, excluding PII fields."""
    data = {
        "visit_id": context.get("visit_id", ""),
        "event_type": context.get("event_type", ""),
    }
    for key in context.keys():
        if key.lower() in PII_FIELDS:
            raise ValueError(f"PII field cannot be in payload")
    return data


def send_to_user(user_id: str, event_type: str, context: dict) -> list:
    from django.contrib.auth import get_user_model
    from notifications.models import DeviceToken, NotificationLog, NotificationStatus, EVENT_CATEGORY_MAP
    from notifications.templates import render_template
    
    User = get_user_model()
    logs = []
    
    try:
        user = User.objects.select_related("notification_prefs").get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("Push user not found: %s", user_id)
        return logs
    
    category = EVENT_CATEGORY_MAP.get(event_type)
    if category is not None:
        try:
            prefs = user.notification_prefs
            if not prefs.is_category_enabled(category):
                log = NotificationLog.objects.create(
                    recipient=user, event_type=event_type, template_key=event_type,
                    title="", body="", data_payload=_build_data_payload(context),
                    status=NotificationStatus.SKIPPED,
                    fcm_error=f"User preference: {category} disabled",
                )
                logs.append(log)
                return logs
        except:
            pass
    
    language = getattr(user, "preferred_language", "ar")
    try:
        title, body = render_template(event_type, language, **context)
    except KeyError as e:
        logger.error("Template render error: %s", str(e))
        return logs
    
    tokens = DeviceToken.objects.filter(user_id=user_id, is_active=True)
    
    if not tokens.exists():
        log = NotificationLog.objects.create(
            recipient=user, event_type=event_type, template_key=event_type,
            title=title, body=body, data_payload=_build_data_payload(context),
            status=NotificationStatus.SKIPPED, fcm_error="No active device tokens",
        )
        logs.append(log)
        return logs
    
    logger.info("Push to user=%s event=%s tokens=%d", user_id, event_type, tokens.count())
    data_payload = _build_data_payload(context)
    
    try:
        from firebase_admin import messaging
    except ImportError:
        log = NotificationLog.objects.create(
            recipient=user, event_type=event_type, template_key=event_type,
            title=title, body=body, data_payload=data_payload,
            status=NotificationStatus.SKIPPED, fcm_error="Firebase not configured",
        )
        logs.append(log)
        return logs
    
    messages = []
    for token_obj in tokens:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data_payload, token=token_obj.token,
        )
        messages.append(message)
    
    BATCH_SIZE = 500
    for i in range(0, len(messages), BATCH_SIZE):
        batch = messages[i:i + BATCH_SIZE]
        try:
            batch_response = messaging.send_each(batch)
            for idx, response in enumerate(batch_response.responses):
                token_obj = list(tokens)[idx]
                if response.success:
                    log = NotificationLog.objects.create(
                        recipient=user, event_type=event_type, template_key=event_type,
                        title=title, body=body, data_payload=data_payload,
                        status=NotificationStatus.SENT, device_token_used=token_obj.token,
                    )
                    logs.append(log)
                else:
                    error_msg = str(response.exception) if response.exception else "Unknown error"
                    log = NotificationLog.objects.create(
                        recipient=user, event_type=event_type, template_key=event_type,
                        title=title, body=body, data_payload=data_payload,
                        status=NotificationStatus.FAILED, fcm_error=error_msg,
                        device_token_used=token_obj.token,
                    )
                    logs.append(log)
                    if response.exception and isinstance(response.exception, messaging.UnregisteredError):
                        token_obj.is_active = False
                        token_obj.save()
        except Exception as e:
            logger.error("Push batch error: %s", str(e))
    return logs


def send_to_users(user_ids: list, event_type: str, context: dict) -> list:
    all_logs = []
    for user_id in user_ids:
        logs = send_to_user(user_id, event_type, context)
        all_logs.extend(logs)
    return all_logs
