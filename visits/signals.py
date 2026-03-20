"""
Payment signals — connects visit lifecycle events to the payment service.

T037: When a visit transitions to COMPLETED → capture escrowed payment.
      When a visit transitions to CANCELLED → process refund.
T012: Broadcast visit status changes to WebSocket groups via Redis cache.
"""

import json
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction as db_transaction
from django.core.cache import cache
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


@receiver(post_save, sender="visits.Visit")
def handle_visit_status_change(sender, instance, **kwargs):
    """
    T037: Trigger payment actions on visit status transitions.
    T012: Broadcast status changes to WebSocket groups.

    Uses `_previous_status` attribute set by `Visit.transition_to()` to avoid
    a DB query inside the signal handler (C2 fix).

    - COMPLETED: Capture escrowed payment and credit agency wallet.
    - CANCELLED: Issue refund via Paymob.
    """
    from visits.models import VisitStatus, Transaction, TransactionStatus

    previous = getattr(instance, "_previous_status", None)
    if previous is None or previous == instance.status:
        return

    new_status = instance.status

    def _broadcast_status_change():
        """
        Broadcast visit status change to WebSocket groups.
        Called via transaction.on_commit() to avoid stale reads.
        """
        try:
            channel_layer = get_channel_layer()

            nurse_data = None
            # Use already loaded nurse if available (from select_related), otherwise query
            if hasattr(instance, "nurse") and instance.nurse:
                nurse = instance.nurse
            else:
                from users.models import NurseProfile

                nurse = (
                    NurseProfile.objects.select_related("user")
                    .filter(id=instance.nurse_id)
                    .first()
                )

            if nurse:
                nurse_data = {
                    "id": str(nurse.id),
                    "name": nurse.user.get_full_name() if nurse.user else "",
                    "latitude": nurse.last_location.y if nurse.last_location else None,
                    "longitude": nurse.last_location.x if nurse.last_location else None,
                }

            payload = {
                "visit_id": str(instance.id),
                "status": instance.status,
                "previous_status": previous,
                "timestamp": timezone.now().isoformat(),
                "nurse": nurse_data,
            }

            async_to_sync(channel_layer.group_send)(
                f"visit_{instance.id}",
                {
                    "type": "visit_state_change",
                    "data": payload,
                },
            )

            if instance.agency_id:
                async_to_sync(channel_layer.group_send)(
                    f"agency_{instance.agency_id}",
                    {
                        "type": "visit_update",
                        "data": payload,
                    },
                )

            cache_key = f"visit_status:{instance.id}"
            cache.set(cache_key, json.dumps(payload, default=str), timeout=120)

            logger.info(
                "Broadcast visit %s status change: %s -> %s",
                instance.id,
                previous,
                instance.status,
            )

        except Exception as e:
            logger.error(
                "Failed to broadcast visit %s status change: %s", instance.id, e
            )

    if new_status == VisitStatus.COMPLETED and previous != VisitStatus.COMPLETED:

        def _capture():
            try:
                txn = Transaction.objects.filter(
                    visit=instance,
                    status=TransactionStatus.ESCROWED,
                ).first()
                if not txn:
                    logger.warning("No escrowed transaction for visit %s", instance.id)
                    return

                txn.status = TransactionStatus.SETTLED
                txn.save(update_fields=["status"])

                if instance.agency_id and txn.agency_payout:
                    from django.db.models import F
                    from users.models import AgencyProfile
                    AgencyProfile.objects.filter(id=instance.agency_id).update(
                        wallet_balance=F("wallet_balance") + txn.agency_payout
                    )

                logger.info(
                    "Captured payment for visit %s: settled=%s, agency_payout=%s",
                    instance.id,
                    txn.amount_paid,
                    txn.agency_payout,
                )
            except Exception as e:
                logger.error(
                    "Failed to capture payment for visit %s: %s", instance.id, e
                )

        db_transaction.on_commit(_capture)
        db_transaction.on_commit(_broadcast_status_change)

    elif new_status == VisitStatus.CANCELLED and previous != VisitStatus.CANCELLED:

        def _refund():
            try:
                from visits.models import Transaction, TransactionStatus

                txn = Transaction.objects.filter(
                    visit=instance,
                    status__in=[TransactionStatus.ESCROWED, TransactionStatus.SETTLED],
                ).first()
                if not txn:
                    return

                from visits.services.paymob_service import PaymobService

                if txn.paymob_transaction_id:
                    PaymobService.process_refund(
                        transaction_id=txn.paymob_transaction_id,
                        amount_egp=txn.amount_paid,
                    )

                txn.status = TransactionStatus.REFUNDED
                txn.save(update_fields=["status"])

                logger.info("Refunded payment for visit %s", instance.id)
            except Exception as e:
                logger.error(
                    "Failed to refund payment for visit %s: %s", instance.id, e
                )

        db_transaction.on_commit(_refund)
        db_transaction.on_commit(_broadcast_status_change)

    else:
        db_transaction.on_commit(_broadcast_status_change)
