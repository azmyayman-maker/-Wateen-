from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models import PatientProfile
from visits.models import Visit, VisitStatus, ServiceType


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
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
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
