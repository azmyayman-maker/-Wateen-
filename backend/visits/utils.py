"""
Utility functions for the visits app.

Contains helper functions for distance calculations and nurse lookups.
"""

from decimal import Decimal

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from users.models import NurseProfile, VerificationStatus


def find_nearest_available_nurse(
    lat: float, lng: float
) -> tuple[NurseProfile | None, Decimal]:
    """
    Find the nearest available verified nurse to the given coordinates.

    Uses PostGIS Distance function for accurate geodetic distance calculation.
    Only considers nurses that are:
    - Available (is_available=True)
    - Verified (verification_status=VERIFIED)
    - Have a valid location (last_location is not null)

    Args:
        lat: Patient latitude (-90 to 90)
        lng: Patient longitude (-180 to 180)

    Returns:
        Tuple of (nurse, distance_km). Returns (None, Decimal("0")) if no nurse found.
    """
    point = Point(lng, lat, srid=4326)

    nurse = (
        NurseProfile.objects.filter(
            is_available=True,
            verification_status=VerificationStatus.VERIFIED,
            last_location__isnull=False,
        )
        .annotate(distance=Distance("last_location", point))
        .order_by("distance")
        .first()
    )

    if nurse is None:
        return None, Decimal("0")

    distance_km = Decimal(str(nurse.distance.km))
    return nurse, distance_km
