from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from visits.models import ServiceType


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
    service_type = serializers.PrimaryKeyRelatedField(
        queryset=ServiceType.objects.all(),
        required=False,
        allow_null=True,
        help_text=_("UUID of the service type"),
    )


class VisitResponseSerializer(serializers.Serializer):
    """Output serializer for visit data."""

    id = serializers.UUIDField(read_only=True)
    status = serializers.CharField(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    def get_latitude(self, obj) -> float:
        return obj.location.y if obj.location else None

    def get_longitude(self, obj) -> float:
        return obj.location.x if obj.location else None

    def get_service_type(self, obj) -> str | None:
        """Return service type name or None."""
        if obj.service_type:
            return obj.service_type.name
        return None


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


# ─── Nurse-Side Serializers ───────────────────────────────────────────────────


class NurseToggleSerializer(serializers.Serializer):
    """Input serializer for toggling nurse availability."""

    is_online = serializers.BooleanField(
        help_text=_("Whether the nurse wants to go online or offline"),
    )
    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
        required=False,
        allow_null=True,
        help_text=_("Nurse latitude (required when going online)"),
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
        required=False,
        allow_null=True,
        help_text=_("Nurse longitude (required when going online)"),
    )

    def validate(self, attrs):
        if attrs["is_online"] and (attrs.get("latitude") is None or attrs.get("longitude") is None):
            raise serializers.ValidationError(
                _("Latitude and longitude are required when going online.")
            )
        return attrs


class NurseRespondSerializer(serializers.Serializer):
    """Input serializer for accepting or declining a visit."""

    visit_id = serializers.UUIDField(
        help_text=_("UUID of the visit to respond to"),
    )
    action = serializers.ChoiceField(
        choices=["accept", "decline"],
        help_text=_("Whether to accept or decline the visit"),
    )


class NursePendingVisitSerializer(serializers.Serializer):
    """Output serializer for pending visits shown to nurses."""

    id = serializers.UUIDField(read_only=True)
    status = serializers.CharField(read_only=True)
    patient_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    distance_km = serializers.FloatField(read_only=True, required=False, default=None)
    estimated_price = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    def get_patient_name(self, obj) -> str:
        if obj.patient:
            return obj.patient.user.get_full_name()
        return "Unknown"

    def get_service_name(self, obj) -> str | None:
        if obj.service_type:
            return obj.service_type.name
        return _("General Care")

    def get_latitude(self, obj) -> float | None:
        return obj.location.y if obj.location else None

    def get_longitude(self, obj) -> float | None:
        return obj.location.x if obj.location else None

    def get_estimated_price(self, obj) -> str:
        if obj.service_type and obj.service_type.base_price:
            return str(obj.service_type.base_price)
        return "150.00"
