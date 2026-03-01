from django.utils import timezone
from visits.models import Visit, VisitStatus, Transaction, TransactionStatus
from .logging import logger


class SettlementService:
    """
    T029: Logic to handle transaction settlements after visit completion.
    """

    @staticmethod
    def create_transaction_for_visit(visit):
        """Initializes a transaction for a new visit."""
        from decimal import Decimal
        
        total = visit.final_price
        if total is None:
            raise ValueError(
                f"Cannot create transaction for visit {visit.id}: "
                f"final_price is None. Ensure pricing is calculated first."
            )
        total = Decimal(str(total))
        
        transaction = Transaction(
            visit=visit,
            amount_paid=total,
            status=TransactionStatus.ESCROWED,
        )
        # Payout is auto-calculated on save
        transaction.save()
        return transaction

    @staticmethod
    def mark_escrowed(visit, payment_intent_id):
        """Marks a transaction as escrowed after payment intent creation."""
        try:
            transaction = visit.transaction
            transaction.paymob_order_id = payment_intent_id
            transaction.status = TransactionStatus.ESCROWED
            transaction.save()
        except Exception as e:
            logger.error(f"Error marking escrow for visit {visit.id}: {str(e)}")

    @staticmethod
    def settle_visit(visit):
        """
        Calculates final settlement once visit is COMPLETED.
        Updates wallet balances if necessary or verifies Stripe status.
        """
        if visit.status != VisitStatus.COMPLETED:
            logger.warning(f"Cannot settle visit {visit.id} (status: {visit.status})")
            return False

        try:
            transaction = visit.transaction
            if transaction.status == TransactionStatus.SETTLED:
                return True

            # In a real Stripe Connect Destination Charge setup,
            # funds are already split and will be settled to the agency's
            # connected account pending the capture/delay settings.

            transaction.status = TransactionStatus.SETTLED
            transaction.save()

            # Update Agency internal wallet for accounting (atomic update using F())
            agency = visit.agency
            if agency is not None:
                from django.db.models import F
                from users.models import AgencyProfile

                AgencyProfile.objects.filter(pk=agency.pk).update(
                    wallet_balance=F("wallet_balance") + transaction.agency_payout
                )
                agency.refresh_from_db()

            logger.info(
                f"Settled transaction for visit {visit.id}. Agency wallet updated."
            )
            return True
        except Exception as e:
            logger.error(f"Settlement failed for visit {visit.id}: {str(e)}")
            return False
