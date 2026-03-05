"""
Payment signals — connects visit lifecycle events to the payment service.

T037: When a visit transitions to COMPLETED → capture escrowed payment.
      When a visit transitions to CANCELLED → process refund.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="visits.Visit")
def handle_visit_status_change(sender, instance, **kwargs):
    """
    T037: Trigger payment actions on visit status transitions.

    Uses `_previous_status` attribute set by `Visit.transition_to()` to avoid
    a DB query inside the signal handler (C2 fix).

    - COMPLETED: Capture escrowed payment and credit agency wallet.
    - CANCELLED: Issue refund via Paymob.
    """
    from visits.models import VisitStatus, Transaction, TransactionStatus

    # Read the stashed previous status (set by transition_to())
    previous = getattr(instance, "_previous_status", None)
    if previous is None or previous == instance.status:
        return  # No transition occurred via transition_to()

    new_status = instance.status

    if new_status == VisitStatus.COMPLETED and previous != VisitStatus.COMPLETED:
        # Schedule capture on commit to avoid blocking the save
        from django.db import transaction as db_transaction

        def _capture():
            try:
                txn = Transaction.objects.filter(
                    visit=instance,
                    status=TransactionStatus.ESCROWED,
                ).first()
                if not txn:
                    logger.warning("No escrowed transaction for visit %s", instance.id)
                    return

                # In production, this would call Paymob's capture API
                # For now we update the transaction status directly
                txn.status = TransactionStatus.SETTLED
                txn.save(update_fields=["status"])

                # Credit agency wallet
                agency = instance.agency
                if agency and txn.agency_payout:
                    agency.wallet_balance += txn.agency_payout
                    agency.save(update_fields=["wallet_balance"])

                logger.info(
                    "Captured payment for visit %s: settled=%s, agency_payout=%s",
                    instance.id, txn.amount_paid, txn.agency_payout,
                )
            except Exception as e:
                logger.error("Failed to capture payment for visit %s: %s", instance.id, e)

        db_transaction.on_commit(_capture)

    elif new_status == VisitStatus.CANCELLED and previous != VisitStatus.CANCELLED:
        from django.db import transaction as db_transaction

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
                logger.error("Failed to refund payment for visit %s: %s", instance.id, e)

        db_transaction.on_commit(_refund)
