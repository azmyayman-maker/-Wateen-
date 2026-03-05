"""
Celery Tasks for User Module.

Implements asynchronous task processing for:
- Nurse invitation notifications (SMS/Email)
- Background invitation expiration cleanup
- Rate limit cache maintenance

Design Decision (from research.md):
- Choice: Celery Task in users/tasks.py
- Rationale: Decouples API response from potentially slow SMS/Email gateway
- Contract: send_nurse_invitation_task(invitation_id) fetches invitation 
  and triggers NotificationService
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    name="users.send_nurse_invitation_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_nurse_invitation_task(self, invitation_id: str):
    """
    Async task to send nurse invitation notification.
    
    Fetches the invitation and triggers the notification service
    to send SMS/Email to the prospective nurse.
    
    Args:
        invitation_id: UUID string of the NurseInvitation
        
    Returns:
        dict with success status and message ID
        
    Raises:
        Exception: Retries on failure (up to 3 times)
    """
    from .models import NurseInvitation, InvitationStatus
    from .services.notifications import NotificationService
    
    logger.info(f"Processing invitation notification for {invitation_id}")
    
    try:
        invitation = NurseInvitation.objects.select_related("agency").get(
            id=invitation_id,
            status=InvitationStatus.PENDING
        )
    except NurseInvitation.DoesNotExist:
        logger.warning(f"Invitation {invitation_id} not found or not pending")
        return {"success": False, "error": "invitation_not_found"}
    
    # Check if invitation is still valid
    if not invitation.is_valid:
        logger.info(f"Invitation {invitation_id} has expired")
        return {"success": False, "error": "invitation_expired"}
    
    try:
        # Send notification via NotificationService
        result = NotificationService.send_nurse_invitation(
            phone=invitation.phone,
            agency_name=invitation.agency.manager_name,
            token=str(invitation.token),
            expires_at=invitation.expires_at
        )
        
        logger.info(
            f"Successfully sent invitation notification to {invitation.phone}, "
            f"message_id: {result.get('message_id')}"
        )
        
        return {
            "success": True,
            "message_id": result.get("message_id"),
            "invitation_id": str(invitation_id)
        }
        
    except Exception as e:
        logger.exception(f"Failed to send invitation notification: {e}")
        
        # Retry with exponential backoff
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(
                f"Max retries exceeded for invitation {invitation_id}, "
                f"marking as failed"
            )
            return {
                "success": False,
                "error": str(e),
                "invitation_id": str(invitation_id)
            }


@shared_task(
    name="users.expire_old_invitations_task",
    bind=True
)
def expire_old_invitations_task(self):
    """
    Background task to mark expired invitations.
    
    Runs periodically (e.g., every hour) to clean up invitations
    that have passed their expiry date.
    
    Returns:
        Number of invitations marked as expired
    """
    from .services.invitation import InvitationService
    
    logger.info("Running invitation expiration cleanup")
    
    try:
        expired_count = InvitationService.expire_old_invitations()
        logger.info(f"Marked {expired_count} invitations as expired")
        return {"expired_count": expired_count}
    except Exception as e:
        logger.exception(f"Failed to expire invitations: {e}")
        return {"expired_count": 0, "error": str(e)}


@shared_task(
    name="users.send_invitation_reminder_task",
    bind=True,
    max_retries=2
)
def send_invitation_reminder_task(self, invitation_id: str):
    """
    Send a reminder for pending invitations (24 hours before expiry).
    
    Args:
        invitation_id: UUID string of the NurseInvitation
        
    Returns:
        dict with success status
    """
    from .models import NurseInvitation, InvitationStatus
    from .services.notifications import NotificationService
    
    logger.info(f"Processing invitation reminder for {invitation_id}")
    
    try:
        invitation = NurseInvitation.objects.select_related("agency").get(
            id=invitation_id,
            status=InvitationStatus.PENDING
        )
    except NurseInvitation.DoesNotExist:
        logger.warning(f"Invitation {invitation_id} not found or not pending")
        return {"success": False, "error": "invitation_not_found"}
    
    # Check if reminder is appropriate (within 24 hours of expiry)
    time_until_expiry = invitation.expires_at - timezone.now()
    hours_remaining = time_until_expiry.total_seconds() / 3600
    
    if hours_remaining > 24:
        logger.info(f"Invitation {invitation_id} has >24h remaining, skipping reminder")
        return {"success": False, "error": "too_early_for_reminder"}
    
    try:
        result = NotificationService.send_invitation_reminder(
            phone=invitation.phone,
            agency_name=invitation.agency.manager_name,
            hours_remaining=int(hours_remaining)
        )
        
        logger.info(f"Sent reminder for invitation {invitation_id}")
        return {"success": True, "invitation_id": str(invitation_id)}
        
    except Exception as e:
        logger.exception(f"Failed to send reminder: {e}")
        return {"success": False, "error": str(e)}