from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class VisitRequestSerializer(serializers.Serializer):
    """Input serializer for creating a visit request."""

    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
        help_text=_("خط العرض"),
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
        help_text=_("خط الطول"),
    )
    service_type = serializers.CharField(
        max_length=50,
        required=False,
        default="",
        help_text=_("نوع الخدمة"),
    )


class VisitResponseSerializer(serializers.Serializer):
    """Output serializer for visit data."""

    id = serializers.UUIDField(read_only=True)
    status = serializers.CharField(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    service_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def get_latitude(self, obj) -> float:
        return obj.location.y if obj.location else None

    def get_longitude(self, obj) -> float:
        return obj.location.x if obj.location else None


class EstimateRequestSerializer(serializers.Serializer):
    """T021: Input serializer for price estimate requests."""

    service_type_id = serializers.UUIDField(
        help_text=_("UUID of the service type"),
    )
    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
        help_text=_("Customer latitude"),
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
        help_text=_("Customer longitude"),
    )
    request_time = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Optional time for estimate (defaults to now)"),
    )


class ServiceTypeInfoSerializer(serializers.Serializer):
    """Serializer for service type info in estimate response."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class PriceBreakdownSerializer(serializers.Serializer):
    """T023: Serializer for price breakdown."""

    base_price = serializers.CharField()
    distance_km = serializers.FloatField()
    distance_fee = serializers.CharField()
    time_multiplier = serializers.CharField()
    ai_surge_coefficient = serializers.CharField()
    final_price = serializers.CharField()


class EstimateResponseSerializer(serializers.Serializer):
    """T022: Output serializer for estimate response."""

    service_type = ServiceTypeInfoSerializer()
    breakdown = PriceBreakdownSerializer()
    is_night_hours = serializers.BooleanField()
    currency = serializers.CharField(default="EGP")


class MockPaymentRequestSerializer(serializers.Serializer):
    """T048: Input serializer for mock payment webhook."""

    visit_id = serializers.UUIDField(
        help_text=_("UUID of the visit to update"),
    )
    status = serializers.ChoiceField(
        choices=["success", "failed"],
        help_text=_("Payment result status"),
    )
    transaction_id = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
        help_text=_("Optional transaction reference"),
    )
    error_message = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
        help_text=_("Error message for failed payments"),
    )


class MockPaymentResponseSerializer(serializers.Serializer):
    """Output serializer for mock payment response."""

    visit_id = serializers.UUIDField()
    payment_status = serializers.CharField()
    previous_status = serializers.CharField()
