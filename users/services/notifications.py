import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class AgencyNotificationService:
    """
    Service Layer for handling SuperAdmin and Agency notifications.
    Uses Celery for async execution and Channels for real-time delivery.
    """

    @staticmethod
    def notify_superadmins_of_new_registration(agency_id: str, manager_name: str) -> None:
        """
        Trigger an asynchronous task to notify all SuperAdmins of a new agency registration.
        """
        send_superadmin_notification_task.delay(
            agency_id=agency_id,
            message=f"New agency registration: {manager_name} (ID: {agency_id}) requires KYC review.",
            notification_type="NEW_REGISTRATION",
        )


@shared_task
def send_superadmin_notification_task(agency_id: str, message: str, notification_type: str) -> None:
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
                    "timestamp": None,
                },
            },
        )
    except Exception:
        logger.exception("Failed to send SuperAdmin notification")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_kyc_review_email_task(
    self,
    agency_id: str,
    action: str,
    notes: str = "",
) -> None:
    """
    Celery task to send KYC review notification emails to agency admins.
    Uses exponential backoff for retries.

    Args:
        agency_id: UUID of the agency
        action: 'APPROVE' or 'REJECT'
        notes: Reviewer notes (required for REJECT)
    """
    from users.models import AgencyProfile, CustomUser

    try:
        agency = AgencyProfile.objects.get(id=agency_id)
    except AgencyProfile.DoesNotExist:
        logger.error("Agency %s not found for email notification", agency_id)
        return

    # Get the agency admin user
    try:
        admin_user = CustomUser.objects.get(agency_id=agency_id, role='AGENCY_ADMIN')
    except CustomUser.DoesNotExist:
        # Try to find any user linked to this agency
        admin_user = CustomUser.objects.filter(agency_id=agency_id).first()
        if not admin_user:
            logger.error("No admin user found for agency %s", agency_id)
            return

    if not admin_user.email:
        logger.error("No email address for agency admin %s", admin_user.national_id)
        return

    # Prepare email content
    template_context = {
        'manager_name': agency.manager_name,
        'commercial_registry': agency.commercial_registry,
        'notes': notes,
    }

    if action == 'APPROVE':
        subject = _("🎉 Your agency has been approved! - Wateen")
        message_text = render_to_string('users/emails/agency_approved.txt', template_context)
        message_html = render_to_string('users/emails/agency_approved.html', template_context)
    else:  # REJECT
        subject = _("⚠️ Your agency application requires updates - Wateen")
        message_text = render_to_string('users/emails/agency_rejected.txt', template_context)
        message_html = render_to_string('users/emails/agency_rejected.html', template_context)

    try:
        send_mail(
            subject=subject,
            message=message_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_user.email],
            html_message=message_html,
            fail_silently=False,
        )
        logger.info("KYC review email sent to %s for agency %s", admin_user.email, agency_id)
    except Exception as exc:
        logger.warning(
            "Failed to send KYC review email for agency %s: %s", agency_id, exc
        )
        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(
                "Max retries exceeded for sending KYC review email to agency %s",
                agency_id,
            )
