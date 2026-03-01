import stripe
from django.conf import settings
from decimal import Decimal
from .logging import logger

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


class PaymentService:
    """
    T028: Handles Stripe Connect Destination Charges and Escrow logic.
    """

    @staticmethod
    def create_payment_intent(visit, agency):
        """
        Creates a PaymentIntent that splits funds between Wateen and the Agency.
        Uses Destination Charges: https://stripe.com/docs/connect/destination-charges
        """
        if not agency.stripe_account_id:
            logger.error(f"Agency {agency.id} has no Stripe Account ID.")
            return None

        try:
            # Wateen takes 15% (take rate)
            # Stripe amounts are in cents
            total_cents = int(visit.final_price * 100)
            take_rate_percent = 15

            intent = stripe.PaymentIntent.create(
                amount=total_cents,
                currency="egp",
                payment_method_types=["card"],
                transfer_data={
                    "destination": agency.stripe_account_id,
                },
                application_fee_amount=int(total_cents * (take_rate_percent / 100)),
                idempotency_key=f"payment_intent_visit_{visit.id}",
                metadata={
                    "visit_id": str(visit.id),
                    "agency_id": str(agency.id),
                    "client_id": str(visit.patient_id),
                },
            )
            return intent
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Error: {str(e)}")
            return None

    @staticmethod
    def capture_payment(payment_intent_id):
        """Captures a previously authorized payment."""
        try:
            return stripe.PaymentIntent.capture(payment_intent_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Capture Error: {str(e)}")
            return None

    @staticmethod
    def refund_payment(payment_intent_id):
        """Refunds a payment."""
        try:
            return stripe.Refund.create(payment_intent=payment_intent_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Refund Error: {str(e)}")
            return None
