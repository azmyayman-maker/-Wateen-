"""
API Views for Pricing Engine

Contains EstimateView for price estimates and MockPaymentWebhookView for testing.
"""

import logging
from decimal import Decimal

from django.utils import timezone
import dataclasses
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from visits.models import ServiceType
from visits.serializers import (
    EstimateRequestSerializer,
    EstimateResponseSerializer,
    MockPaymentRequestSerializer,
    MockPaymentResponseSerializer,
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
