"""
API Views for Pricing Engine

Contains EstimateView for price estimates and MockPaymentWebhookView for testing.
"""

import logging

from django.utils import timezone
import dataclasses
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from visits.models import ServiceType
from visits.serializers import (
    EstimateRequestSerializer,
    MockPaymentRequestSerializer,
)
from visits.services.pricing import RuleBasedPricingStrategy
from visits.utils import find_nearest_available_nurse

logger = logging.getLogger(__name__)


class EstimateRateThrottle(AnonRateThrottle):
    """T020: Rate throttle for estimate endpoint - 30 requests per hour."""

    rate = "30/hour"


class EstimateView(APIView):
    """
    T024: API view for requesting price estimates.

    POST /api/v1/visits/estimate/

    Public endpoint with IP-based rate limiting.
    Returns detailed price breakdown for a service visit.
    """

    throttle_classes = [EstimateRateThrottle]
    permission_classes = []  # Public endpoint

    def post(self, request):
        serializer = EstimateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            service_type = ServiceType.objects.get(
                id=data["service_type_id"],
                is_active=True,
            )
        except ServiceType.DoesNotExist:
            return Response(
                {"detail": "Service type not found.", "code": "service_type_not_found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request_time = data.get("request_time") or timezone.now()

        strategy = RuleBasedPricingStrategy()

        _, distance_km = find_nearest_available_nurse(
            data["latitude"], data["longitude"]
        )

        breakdown = strategy.calculate_price(
            base_price=service_type.base_price,
            distance_km=distance_km,
            request_time=request_time,
        )

        response_data = {
            "service_type": {
                "id": str(service_type.id),
                "name": service_type.name,
                "base_price": service_type.base_price,
            },
            "breakdown": dataclasses.asdict(breakdown),
            "is_night_hours": strategy.is_night_hours(request_time),
            "currency": "EGP",
        }

        from visits.services.logging import log_estimate_request

        log_estimate_request(
            service_type_id=str(service_type.id),
            latitude=data["latitude"],
            longitude=data["longitude"],
            request_time=request_time,
            price_components=dataclasses.asdict(breakdown),
            ip_address=self._get_client_ip(request),
        )

        return Response(response_data, status=status.HTTP_200_OK)

    def _get_client_ip(self, request) -> str | None:
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class MockPaymentWebhookView(APIView):
    """
    T049: Mock payment webhook for testing.

    POST /api/v1/payments/webhook/mock/

    Only available when DEBUG=True. Requires X-Mock-Token header.
    """

    permission_classes = []

    def post(self, request):
        from django.utils.translation import gettext_lazy as _
        from visits.payment_mock import validate_mock_token

        if not validate_mock_token(request):
            return Response(
                {
                    "detail": _("Mock webhook is disabled or invalid token."),
                    "code": "forbidden",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = MockPaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        from visits.models import Visit

        try:
            visit = Visit.objects.get(id=data["visit_id"])
        except Visit.DoesNotExist:
            return Response(
                {"detail": _("Visit not found."), "code": "visit_not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        previous_status = visit.status
        payment_status = self._update_visit_status(visit, data["status"])

        response_data = {
            "visit_id": str(visit.id),
            "payment_status": payment_status,
            "previous_status": previous_status,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def _update_visit_status(self, visit, payment_status: str) -> str:
        """T051: Update visit status based on payment result."""
        if payment_status == "success":
            try:
                visit.transition_to("COMPLETED")
                return "completed"
            except Exception as e:
                logger.error(
                    "Failed to transition visit %s to COMPLETED: %s",
                    visit.id,
                    e,
                    exc_info=True,
                )
                return "failed"
        else:
            try:
                visit.transition_to("CANCELLED")
                return "failed"
            except Exception as e:
                logger.error(
                    "Failed to transition visit %s to CANCELLED: %s",
                    visit.id,
                    e,
                    exc_info=True,
                )
                return "failed"


class PaymentIntentView(APIView):
    """
    T032: Create a Paymob payment intent for a visit.

    POST /api/v1/payments/intent/

    Called by the patient frontend before rendering the payment form.
    Returns a Paymob payment key and iframe URL.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from visits.models import Visit, VisitStatus, Transaction, TransactionStatus
        from visits.services.paymob_service import PaymobService
        from django.utils.translation import gettext_lazy as _

        visit_id = request.data.get("visit_id")
        if not visit_id:
            return Response(
                {"detail": _("visit_id is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            visit = Visit.objects.get(id=visit_id, patient__user=request.user)
        except Visit.DoesNotExist:
            return Response(
                {"detail": _("الزيارة غير موجودة.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if visit.status not in (VisitStatus.ACCEPTED, VisitStatus.PENDING_AGENCY):
            return Response(
                {"detail": _("لا يمكن الدفع لهذه الزيارة في حالتها الحالية.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = PaymobService.create_payment_intent(
                visit_id=str(visit.id),
                amount_egp=visit.final_price,
                patient_name=request.user.get_full_name() or "Patient",
                patient_email=getattr(request.user, "email", ""),
                patient_phone=getattr(request.user, "phone_number", ""),
            )
        except Exception as e:
            logger.error("Failed to create Paymob payment intent: %s", e)
            return Response(
                {"detail": _("فشل في إنشاء عملية الدفع. حاول مرة أخرى.")},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Update or create transaction in ESCROWED state
        txn, _ = Transaction.objects.update_or_create(
            visit=visit,
            defaults={
                "amount": visit.final_price,
                "status": TransactionStatus.ESCROWED,
                "paymob_order_id": result.order_id,
                "agency": visit.agency,
            },
        )

        return Response({
            "payment_key": result.payment_key,
            "iframe_url": result.iframe_url,
            "order_id": result.order_id,
            "amount": str(visit.final_price),
            "currency": "EGP",
        }, status=status.HTTP_201_CREATED)


class PaymobWebhookView(APIView):
    """
    T033: Paymob HMAC-verified webhook callback.

    POST /api/v1/webhooks/paymob/

    Verifies HMAC SHA-512 signature, then processes payment result.
    """
    permission_classes = []  # Paymob sends no auth header — HMAC is the auth
    authentication_classes = []

    def post(self, request):
        from visits.services.paymob_service import PaymobService
        from visits.models import Transaction, TransactionStatus

        # Verify HMAC
        received_hmac = request.query_params.get("hmac", "")
        if not PaymobService.verify_webhook_hmac(request.data, received_hmac):
            logger.warning("Paymob webhook HMAC verification failed")
            return Response(
                {"detail": "Invalid HMAC signature."},
                status=status.HTTP_403_FORBIDDEN,
            )

        obj = request.data.get("obj", request.data)
        paymob_order_id = str(obj.get("order", {}).get("id", ""))
        success = obj.get("success", False)
        transaction_id = str(obj.get("id", ""))

        if not paymob_order_id:
            return Response(
                {"detail": "Missing order ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            txn = Transaction.objects.get(paymob_order_id=paymob_order_id)
        except Transaction.DoesNotExist:
            logger.warning("Paymob webhook: no transaction for order %s", paymob_order_id)
            return Response(
                {"detail": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Store the Paymob transaction ID for future refunds
        txn.paymob_transaction_id = transaction_id

        if success:
            txn.status = TransactionStatus.ESCROWED
            txn.save(update_fields=["status", "paymob_transaction_id"])
            logger.info("Paymob payment confirmed for order %s", paymob_order_id)
        else:
            txn.status = TransactionStatus.FAILED
            txn.save(update_fields=["status", "paymob_transaction_id"])
            logger.warning("Paymob payment failed for order %s", paymob_order_id)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)

