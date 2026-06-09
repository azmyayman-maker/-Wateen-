from decimal import Decimal

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import AgencyProfile, PatientProfile
from visits.models import ServiceType, Visit, VisitStatus
from visits.services.pricing import RuleBasedPricingStrategy


class NoCoverageError(Exception):
    pass

class RequestVisitService:
    """Service dedicated to orchestrating the visit request transaction safely."""

    def __init__(self):
        self.pricing_strategy = RuleBasedPricingStrategy()

    def _dispatch_async(self, visit_id: str) -> None:
        from visits.tasks import dispatch_visit
        dispatch_visit.delay(visit_id)

    @transaction.atomic
    def execute(
        self,
        patient: PatientProfile,
        service_type: ServiceType,
        location: Point,
        distance_km: float | None = None
    ) -> Visit:
        # Pre-emptive concurrency lock (or duplicate check)
        if Visit.objects.filter(patient=patient, status__in=[VisitStatus.PENDING_AGENCY, VisitStatus.PENDING_NURSE]).select_for_update().exists():
            raise ValidationError("Patient already has an active pending visit.")

        # 1. Validate geographical coverage utilizing PostGIS spatial indexing
        if not AgencyProfile.objects.filter(coverage_polygon__contains=location, is_active=True).exists():
            raise NoCoverageError("لا توجد وكالات تغطي هذه المنطقة الجغرافية في الوقت الحالي.")

        # 2. Calculate Pricing via the exact algorithmic formula
        if distance_km is None:
            raise NotImplementedError("Real distance calculation via OSRM/ORS must be implemented (Phase 5). Stubbed for MVP.")

        # Determine Surge
        ai_surge = Decimal("0.00")

        price_result = self.pricing_strategy.calculate_price(
            base_price=service_type.base_price,
            distance_km=distance_km,
            request_time=timezone.now(),
            ai_surge_coefficient=ai_surge
        )

        # 3. Create the Visit snapshot immutably
        visit = Visit(
            patient=patient,
            status=VisitStatus.PENDING_AGENCY,
            location=location,
            service_type=service_type,
            # Snapshot pricing explicitly
            base_price=service_type.base_price,
            distance_fee=price_result.distance_fee,
            distance_km=distance_km,
            distance_rate=self.pricing_strategy.get_factor("per_km_rate"),
            time_multiplier=price_result.time_multiplier,
            ai_surge_coefficient=ai_surge,
            final_price=price_result.final_price
        )
        visit.save() # Mutates ID and enforces immutable checks instantly

        # 4. Asynchronous Task Dispatch (Triggered ONLY if DB commits without error)
        transaction.on_commit(lambda: self._dispatch_async(visit.id))

        return visit


def create_visit_request(
    patient_profile: PatientProfile,
    latitude: float,
    longitude: float,
    service_type: ServiceType | None = None,
) -> Visit:
    """
    Create a new Visit request for a patient.

    Args:
        patient_profile: PatientProfile instance of the requesting patient.
        latitude: Latitude of the patient's location (-90 to 90).
        longitude: Longitude of the patient's location (-180 to 180).
        service_type: ServiceType instance (optional).

    Returns:
        Visit instance with status PENDING.

    Raises:
        ValidationError: If coordinates are out of valid range.
    """
    if not (-90 <= latitude <= 90):
        raise ValidationError(
            _("خط العرض يجب أن يكون بين -90 و 90."),
            code="invalid_latitude",
        )
    if not (-180 <= longitude <= 180):
        raise ValidationError(
            _("خط الطول يجب أن يكون بين -180 و 180."),
            code="invalid_longitude",
        )

    location = Point(longitude, latitude, srid=4326)

    visit = Visit.objects.create(
        patient=patient_profile,
        status=VisitStatus.PENDING_AGENCY,
        location=location,
        service_type=service_type,
    )
    return visit

def broadcast_visit_request(visit: Visit) -> None:
    """Broadcast a new visit request to nearby available nurses."""
    from visits.services.matching import GeoMatchingService
    geo_service = GeoMatchingService()
    candidates = geo_service.find_candidates(patient_lat=visit.location.y, patient_lng=visit.location.x)

    if candidates:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        from visits.serializers import NursePendingVisitSerializer

        channel_layer = get_channel_layer()
        visit_base_data = NursePendingVisitSerializer(visit).data

        for candidate in candidates:
            visit_data = visit_base_data.copy()
            visit_data['distance_km'] = candidate['distance_km']

            async_to_sync(channel_layer.group_send)(
                f"nurse_{candidate['nurse_id']}",
                {
                    "type": "visit.request",
                    "data": {
                        "type": "new_visit",
                        "visit": visit_data
                    }
                }
            )
