"""
Paymob Payment Service — Egyptian Payment Gateway Integration.

Handles:
  1. Payment intent creation (T031)
  2. Payment capture / 3DS redirect (T032)
  3. HMAC webhook verification (T033)
  4. Refund processing (T034)

API Docs: https://docs.paymob.com/docs
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass
from decimal import Decimal

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class PaymobAuthToken:
    """Authentication token from Paymob (valid for ~1 hour)."""
    token: str


@dataclass
class PaymentIntentResult:
    """Result of creating a payment intent."""
    order_id: str
    payment_key: str
    iframe_url: str


class PaymobService:
    """
    Stateless service for interacting with the Paymob payment gateway.
    All methods are classmethods — no instance state needed.
    """
    BASE_URL = "https://accept.paymob.com/api"

    @classmethod
    def _get_auth_token(cls) -> str:
        """Step 1: Authenticate with Paymob API to get a session token."""
        response = requests.post(
            f"{cls.BASE_URL}/auth/tokens",
            json={"api_key": settings.PAYMOB_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["token"]

    @classmethod
    def create_payment_intent(
        cls,
        visit_id: str,
        amount_egp: Decimal,
        patient_name: str,
        patient_email: str = "",
        patient_phone: str = "",
    ) -> PaymentIntentResult:
        """
        Create a Paymob payment intent (Order + Payment Key).

        Args:
            visit_id: UUID of the visit (used as merchant_order_id)
            amount_egp: Amount in EGP (will be sent in piasters to Paymob)
            patient_name: Patient's full name for billing
            patient_email: Optional email
            patient_phone: Optional phone number

        Returns:
            PaymentIntentResult with order_id, payment_key, and iframe_url
        """
        auth_token = cls._get_auth_token()
        amount_cents = int(amount_egp * 100)

        # Step 2: Register order
        order_response = requests.post(
            f"{cls.BASE_URL}/ecommerce/orders",
            json={
                "auth_token": auth_token,
                "delivery_needed": "false",
                "amount_cents": amount_cents,
                "currency": "EGP",
                "merchant_order_id": visit_id,
                "items": [],
            },
            timeout=10,
        )
        order_response.raise_for_status()
        order_id = str(order_response.json()["id"])

        # Step 3: Generate payment key
        first_name, *last_parts = patient_name.split(" ", 1)
        last_name = last_parts[0] if last_parts else first_name

        payment_key_response = requests.post(
            f"{cls.BASE_URL}/acceptance/payment_keys",
            json={
                "auth_token": auth_token,
                "amount_cents": amount_cents,
                "expiration": 3600,  # 1 hour
                "order_id": order_id,
                "billing_data": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": patient_email or "na@na.com",
                    "phone_number": patient_phone or "+201000000000",
                    "apartment": "NA",
                    "floor": "NA",
                    "street": "NA",
                    "building": "NA",
                    "shipping_method": "NA",
                    "postal_code": "NA",
                    "city": "Cairo",
                    "country": "EG",
                    "state": "Cairo",
                },
                "currency": "EGP",
                "integration_id": int(settings.PAYMOB_INTEGRATION_ID),
            },
            timeout=10,
        )
        payment_key_response.raise_for_status()
        payment_key = payment_key_response.json()["token"]

        iframe_url = (
            f"https://accept.paymob.com/api/acceptance/iframes/"
            f"{settings.PAYMOB_INTEGRATION_ID}?payment_token={payment_key}"
        )

        logger.info(
            "Created Paymob payment intent: order=%s visit=%s amount=%s EGP",
            order_id, visit_id, amount_egp,
        )

        return PaymentIntentResult(
            order_id=order_id,
            payment_key=payment_key,
            iframe_url=iframe_url,
        )

    @classmethod
    def verify_webhook_hmac(cls, request_data: dict, received_hmac: str) -> bool:
        """
        Verify the HMAC signature of a Paymob webhook callback.

        Paymob sends an HMAC SHA-512 of concatenated transaction fields.
        """
        # Fields that Paymob includes in HMAC calculation (alphabetical order)
        hmac_fields = [
            "amount_cents", "created_at", "currency", "error_occured",
            "has_parent_transaction", "id", "integration_id",
            "is_3d_secure", "is_auth", "is_capture", "is_refunded",
            "is_standalone_payment", "is_voided", "order",
            "owner", "pending", "source_data_pan", "source_data_sub_type",
            "source_data_type", "success",
        ]

        obj = request_data.get("obj", request_data)

        concatenated = ""
        for field in hmac_fields:
            value = obj.get(field, "")
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, dict):
                # Handle nested fields like source_data
                if field.startswith("source_data_"):
                    key = field.replace("source_data_", "")
                    source = obj.get("source_data", {})
                    value = str(source.get(key, ""))
                else:
                    value = str(value.get("id", value))
            else:
                value = str(value)
            concatenated += value

        expected_hmac = hmac.new(
            settings.PAYMOB_HMAC_SECRET.encode("utf-8"),
            concatenated.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

        return hmac.compare_digest(expected_hmac, received_hmac)

    @classmethod
    def process_refund(
        cls,
        transaction_id: str,
        amount_egp: Decimal,
    ) -> dict:
        """
        Process a refund for a completed transaction.

        Args:
            transaction_id: Paymob transaction ID
            amount_egp: Amount to refund in EGP

        Returns:
            Paymob refund response dict
        """
        auth_token = cls._get_auth_token()
        amount_cents = int(amount_egp * 100)

        response = requests.post(
            f"{cls.BASE_URL}/acceptance/void_refund/refund",
            json={
                "auth_token": auth_token,
                "transaction_id": transaction_id,
                "amount_cents": amount_cents,
            },
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()

        logger.info(
            "Processed Paymob refund: transaction=%s amount=%s EGP",
            transaction_id, amount_egp,
        )

        return result
