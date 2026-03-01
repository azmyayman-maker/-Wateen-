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
        transaction = Transaction(
            visit=visit,
            total_amount=visit.final_price,
            status=TransactionStatus.PENDING
        )
        transaction.calculate_split()
        transaction.save()
        return transaction

    @staticmethod
    def mark_escrowed(visit, payment_intent_id):
        """Marks a transaction as escrowed after payment intent creation."""
        try:
            transaction = visit.transaction
            transaction.stripe_payment_intent_id = payment_intent_id
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
            
            # Update Agency internal wallet for accounting
            agency = visit.agency
            agency.wallet_balance += transaction.agency_amount
            agency.save(update_fields=['wallet_balance'])
            
            logger.info(f"Settled transaction for visit {visit.id}. Agency wallet updated.")
            return True
        except Exception as e:
            logger.error(f"Settlement failed for visit {visit.id}: {str(e)}")
            return False
