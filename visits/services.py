from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Visit, VisitStatus


def create_visit_request(patient_profile, latitude: float, longitude: float, service_type: str = '') -> Visit:
    """
    Create a new Visit request for a patient.

    Args:
        patient_profile: PatientProfile instance of the requesting patient.
        latitude: Latitude of the patient's location (-90 to 90).
        longitude: Longitude of the patient's location (-180 to 180).
        service_type: Type of nursing service requested.

    Returns:
        Visit instance with status PENDING.

    Raises:
        ValidationError: If coordinates are out of valid range.
    """
    if not (-90 <= latitude <= 90):
        raise ValidationError(
            _('خط العرض يجب أن يكون بين -90 و 90.'),
            code='invalid_latitude',
        )
    if not (-180 <= longitude <= 180):
        raise ValidationError(
            _('خط الطول يجب أن يكون بين -180 و 180.'),
            code='invalid_longitude',
        )

    location = Point(longitude, latitude, srid=4326)

    visit = Visit.objects.create(
        patient=patient_profile,
        status=VisitStatus.PENDING,
        location=location,
        service_type=service_type,
    )
    return visit
