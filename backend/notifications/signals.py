"""
Notification Signals — Auto-create notification preferences for new users
and dispatch visit notifications.
"""

import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import NotificationEventType, UserNotificationPrefs
from notifications.tasks import send_notification_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_notification_prefs(sender, instance, created, **kwargs):
    """
    Automatically create UserNotificationPrefs when a new user is created.
    """
    if created:
        UserNotificationPrefs.objects.get_or_create(user=instance)


def _dispatch_visit_notification(visit, old_status, new_status):
    """
    Dispatch notification based on visit status transition.
    
    This function is called from Visit.transition_to() in visits/models.py.
    
    Args:
        visit: The Visit instance
        old_status: Previous status
        new_status: New status
    """
    from visits.models import VisitStatus

    # Mapping of status -> (event_type, recipient_getter)
    # recipient_getter returns list of user IDs to notify

    nurse_name = ""
    if visit.nurse and hasattr(visit.nurse, 'user'):
        nurse_name = visit.nurse.user.first_name_ar or ""

    context = {
        "visit_id": str(visit.id),
        "nurse_name": nurse_name,
    }

    # Status transition handlers
    if new_status == VisitStatus.PENDING_AGENCY:
        # Notify agency admin of new dispatch offer
        if visit.agency and visit.agency.admin_user:
            user_ids = [str(visit.agency.admin_user.id)]
            send_notification_task.delay(
                user_ids=user_ids,
                event_type=NotificationEventType.DISPATCH_OFFER,
                context=context,
            )

    elif new_status == VisitStatus.PENDING_NURSE:
        # Notify patient of nurse assignment
        user_ids = [str(visit.patient_id)]
        send_notification_task.delay(
            user_ids=user_ids,
            event_type=NotificationEventType.NURSE_ASSIGNED,
            context=context,
        )
        # Also notify the nurse if assigned
        if visit.nurse and hasattr(visit.nurse, 'user_id'):
            nurse_ids = [str(visit.nurse.user_id)]
            send_notification_task.delay(
                user_ids=nurse_ids,
                event_type=NotificationEventType.DISPATCH_OFFER,
                context=context,
            )

    elif new_status == VisitStatus.EN_ROUTE:
        # Notify patient nurse is on the way
        user_ids = [str(visit.patient_id)]
        send_notification_task.delay(
            user_ids=user_ids,
            event_type=NotificationEventType.NURSE_EN_ROUTE,
            context=context,
        )

    elif new_status == VisitStatus.IN_PROGRESS:
        # Notify patient and agency admin of arrival
        user_ids = [str(visit.patient_id)]
        if visit.agency and visit.agency.admin_user:
            user_ids.append(str(visit.agency.admin_user.id))
        send_notification_task.delay(
            user_ids=user_ids,
            event_type=NotificationEventType.NURSE_ARRIVED,
            context=context,
        )

    elif new_status == VisitStatus.COMPLETED:
        # Notify patient of visit completion
        user_ids = [str(visit.patient_id)]
        send_notification_task.delay(
            user_ids=user_ids,
            event_type=NotificationEventType.VISIT_COMPLETED,
            context=context,
        )

    elif new_status == VisitStatus.CANCELLED:
        # Notify patient, nurse, and agency admin
        user_ids = [str(visit.patient_id)]
        if visit.nurse and hasattr(visit.nurse, 'user_id'):
            user_ids.append(str(visit.nurse.user_id))
        if visit.agency and visit.agency.admin_user:
            user_ids.append(str(visit.agency.admin_user.id))
        send_notification_task.delay(
            user_ids=user_ids,
            event_type=NotificationEventType.VISIT_CANCELLED,
            context=context,
        )


def notify_payment_settled(transaction):
    """
    Send payment settlement notification to agency admin.
    
    Called from Transaction.save() when status changes to SETTLED.
    
    Args:
        transaction: The Transaction instance
    """

    if not transaction.agency or not transaction.agency.admin_user:
        return

    # Use str(Decimal) to avoid float conversion
    amount_str = str(transaction.agency_payout)

    context = {
        "visit_id": str(transaction.visit_id),
        "amount": amount_str,
    }

    user_ids = [str(transaction.agency.admin_user.id)]
    send_notification_task.delay(
        user_ids=user_ids,
        event_type=NotificationEventType.PAYMENT_SETTLED,
        context=context,
    )
