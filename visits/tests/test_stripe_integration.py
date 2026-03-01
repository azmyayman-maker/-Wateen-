import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from visits.models import VisitStatus, TransactionStatus
from visits.services.payment import PaymentService
from visits.services.settlement import SettlementService

@pytest.mark.django_db
class TestStripeIntegration:
    """
    T030: Contract tests for Stripe Connect integrations.
    """

    def test_transaction_initiation(self, sample_visit):
        """Verifies that a transaction is correctly initialized."""
        transaction = SettlementService.create_transaction_for_visit(sample_visit)
        
        assert transaction.status == TransactionStatus.ESCROWED
        assert transaction.amount_paid == sample_visit.final_price
        assert transaction.wateen_take_rate == Decimal('15.00')
        assert transaction.agency_payout == sample_visit.final_price * Decimal('0.85')

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent(self, mock_stripe_create, sample_visit, sample_agency):
        """Verifies PaymentIntent creation with destination charges."""
        sample_agency.stripe_account_id = "acct_test_123"
        sample_agency.save()
        
        mock_stripe_create.return_value = MagicMock(id="pi_test_123")
        
        intent = PaymentService.create_payment_intent(sample_visit, sample_agency)
        
        assert intent.id == "pi_test_123"
        mock_stripe_create.assert_called_once()
        args, kwargs = mock_stripe_create.call_args
        assert kwargs['transfer_data']['destination'] == "acct_test_123"
        assert kwargs['amount'] == int(sample_visit.final_price * 100)

    def test_settlement_logic(self, sample_visit, sample_agency):
        """Verifies settlement logic on visit completion."""
        # Setup
        sample_visit.status = VisitStatus.COMPLETED
        sample_visit.agency = sample_agency
        sample_visit.save()
        
        transaction = SettlementService.create_transaction_for_visit(sample_visit)
        transaction.status = TransactionStatus.ESCROWED
        transaction.save()
        
        initial_balance = sample_agency.wallet_balance
        
        # Execute
        success = SettlementService.settle_visit(sample_visit)
        
        # Verify
        assert success is True
        sample_agency.refresh_from_db()
        transaction = sample_visit.transaction
        assert transaction.status == TransactionStatus.SETTLED
        assert sample_agency.wallet_balance == initial_balance + transaction.agency_payout
