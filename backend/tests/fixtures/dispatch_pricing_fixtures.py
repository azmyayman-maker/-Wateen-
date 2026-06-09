"""
Wateen Dispatch & Pricing QA Test Fixtures
==========================================
B2B2C Healthcare Aggregator - Test Factories for P4-T5

CRITICAL CONSTRAINTS (from AGENTS.md):
- NurseProfile.agency is MANDATORY (B2B2C model)
- All financial calculations use decimal.Decimal
- PostGIS spatial queries for coverage polygons
"""

from datetime import timedelta
from decimal import Decimal

import factory
from django.contrib.gis.geos import Point, Polygon
from django.utils import timezone
from factory import fuzzy

from users.models import (
    AgencyProfile,
    CustomUser,
    DispatchMode,
    NurseProfile,
    PatientProfile,
    VerificationStatus,
)
from visits.models import DispatchOffer, OfferStatus, ServiceType, Visit, VisitStatus


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        django_get_or_create = ("phone_number",)

    phone_number = factory.Sequence(lambda n: f"+2010111111{n % 100000:05d}")
    role = "PATIENT"
    is_active = True


class PatientProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PatientProfile

    user = factory.SubFactory(CustomUserFactory, role="PATIENT")
    full_name = factory.Faker("name")
    phone_number = factory.LazyAttribute(lambda obj: obj.user.phone_number)


class AgencyProfileFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test agencies with coverage polygons.
    Supports overlapping polygon zones for dispatch testing.
    """

    class Meta:
        model = AgencyProfile

    user = factory.SubFactory(CustomUserFactory, role="AGENCY_ADMIN")
    manager_name = factory.Faker("name")
    commercial_registry = factory.Sequence(lambda n: f"CR-{n:06d}")
    moh_license_number = factory.Sequence(lambda n: f"MOH-{n:06d}")
    tax_id = factory.Sequence(lambda n: f"TAX-{n:06d}")
    status = VerificationStatus.VERIFIED
    dispatch_mode = DispatchMode.AUTO
    rating = fuzzy.FuzzyChoice([3.0, 3.5, 4.0, 4.5, 5.0])
    network_capacity = 10

    @factory.lazy_attribute
    def coverage_polygon(obj):
        offset = getattr(obj, "polygon_offset", 0.0)
        return Polygon(
            [
                (30.0 + offset, 31.0),
                (30.1 + offset, 31.0),
                (30.1 + offset, 31.1),
                (30.0 + offset, 31.1),
                (30.0 + offset, 31.0),
            ],
            srid=4326,
        )

    class Params:
        polygon_offset = 0.0


class NurseProfileFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test nurses with agency binding (B2B2C enforced).

    CRITICAL: agency FK is MANDATORY - cannot be null.
    """

    class Meta:
        model = NurseProfile

    user = factory.SubFactory(CustomUserFactory, role="NURSE")
    agency = factory.SubFactory(AgencyProfileFactory)
    full_name = factory.Faker("name")
    national_id = factory.Sequence(lambda n: f"NAT-{n:010d}")
    syndicate_id = factory.Sequence(lambda n: f"SYN-{n:08d}")
    is_available = True
    verification_status = VerificationStatus.VERIFIED

    @factory.lazy_attribute
    def last_location(obj):
        lat_offset = getattr(obj, "lat_offset", 0.0)
        lng_offset = getattr(obj, "lng_offset", 0.0)
        return Point(30.0444 + lat_offset, 31.2357 + lng_offset, srid=4326)

    class Params:
        lat_offset = 0.0
        lng_offset = 0.0


class ServiceTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceType

    name = factory.Sequence(lambda n: f"Service {n}")
    name_ar = factory.Sequence(lambda n: f"خدمة {n}")
    base_price = Decimal("200.00")
    icon = "nursing"
    requires_prescription = False
    estimated_duration_minutes = 60


class VisitFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test visits with pricing snapshot.

    CRITICAL: All pricing fields use Decimal type.
    """

    class Meta:
        model = Visit

    patient = factory.SubFactory(PatientProfileFactory)
    agency = factory.SubFactory(AgencyProfileFactory)
    status = VisitStatus.PENDING_AGENCY
    location = Point(30.0444, 31.2357, srid=4326)
    service_type = factory.SubFactory(ServiceTypeFactory)
    urgency = "medium"

    base_price = Decimal("200.00")
    time_multiplier = Decimal("1.0")
    urgency_multiplier = Decimal("1.0")
    distance_km = Decimal("10.0")
    surge_coefficient = Decimal("1.5")
    final_price = Decimal("330.00")

    reroute_attempts = 0


class DispatchOfferFactory(factory.django.DjangoModelFactory):
    """Factory for creating test dispatch offers."""

    class Meta:
        model = DispatchOffer

    visit = factory.SubFactory(VisitFactory)
    nurse = factory.SubFactory(NurseProfileFactory)
    status = OfferStatus.PENDING

    @factory.lazy_attribute
    def expires_at(obj):
        return timezone.now() + timedelta(seconds=60)


# ============================================
# Test Helper Functions
# ============================================


def create_overlapping_agencies(offset=0.0):
    """
    Creates 3 agencies with overlapping coverage polygons for ranking tests.

    Returns:
        list: [agency1 (highest rating), agency2, agency3 (lowest rating)]
    """
    agencies = []

    for i, (offset_val, rating) in enumerate([(0.0, 4.8), (0.05, 3.5), (0.15, 2.5)]):
        agency = AgencyProfileFactory(polygon_offset=offset + offset_val, rating=rating)
        agencies.append(agency)

    return agencies


def create_concurrent_offers(num_nurses=10):
    """
    Creates a visit with multiple pending offers for concurrency testing.

    Args:
        num_nurses: Number of nurses to create offers for (default: 10)

    Returns:
        tuple: (visit, nurses list, offers list)
    """
    agency = AgencyProfileFactory()
    patient = PatientProfileFactory()
    visit = VisitFactory(patient=patient, agency=agency)

    nurses = [
        NurseProfileFactory(
            agency=agency,
            user__phone_number=f"+2010111111{i:02d}",
            lat_offset=i * 0.001,
            lng_offset=i * 0.001,
        )
        for i in range(num_nurses)
    ]

    expires_at = timezone.now() + timedelta(seconds=60)

    offers = [
        DispatchOffer.objects.create(visit=visit, nurse=nurse, expires_at=expires_at)
        for nurse in nurses
    ]

    return visit, nurses, offers


def mock_find_agencies_covering_point(lat, lng, agencies=None):
    """
    Mock function for spatial intersection testing.
    Replaces actual PostGIS ST_Intersects query for deterministic testing.

    Args:
        lat: Latitude of patient location
        lng: Longitude of patient location
        agencies: Optional list of agencies to filter (uses created ones if None)

    Returns:
        QuerySet: Filtered agencies (mocked)
    """
    if agencies is None:
        agencies = AgencyProfileFactory.create_batch(3)

    from unittest.mock import MagicMock

    queryset = MagicMock()
    queryset.__iter__ = lambda self: iter(agencies)
    return queryset


def mock_get_route(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Mock function for deterministic OSRM routing.
    Returns predictable distance and duration for pricing tests.

    Returns:
        namedtuple: (distance_km, duration_minutes)
    """
    from collections import namedtuple

    RouteResult = namedtuple("RouteResult", ["distance_km", "duration_minutes"])

    distance = abs(dest_lat - origin_lat) + abs(dest_lng - origin_lng)
    distance_km = 10.0

    duration_minutes = distance_km * 2.4

    return RouteResult(distance_km=distance_km, duration_minutes=duration_minutes)


def mock_calculate_surge(geohash):
    """
    Mock function for deterministic surge coefficient.

    Returns:
        Decimal: Fixed surge value for testing (1.5)
    """
    return Decimal("1.5")


# ============================================
# Pricing Test Matrix
# ============================================

PRICING_TEST_MATRIX = [
    {
        "name": "day_standard",
        "base_price": Decimal("200.00"),
        "urgency": "low",
        "hour": 14,
        "distance_km": Decimal("10.0"),
        "surge": Decimal("1.0"),
        "rating": Decimal("4.5"),
        "night_multiplier": Decimal("1.0"),
        "urgency_multiplier": Decimal("1.0"),
        "expected_final": Decimal("270.00"),
    },
    {
        "name": "night_premium",
        "base_price": Decimal("200.00"),
        "urgency": "high",
        "hour": 23,
        "distance_km": Decimal("10.0"),
        "surge": Decimal("1.5"),
        "rating": Decimal("4.5"),
        "night_multiplier": Decimal("1.2"),
        "urgency_multiplier": Decimal("1.2"),
        "expected_final": Decimal("525.00"),
    },
    {
        "name": "sos_maximum_surge",
        "base_price": Decimal("200.00"),
        "urgency": "sos",
        "hour": 3,
        "distance_km": Decimal("5.0"),
        "surge": Decimal("5.0"),
        "rating": Decimal("5.0"),
        "night_multiplier": Decimal("1.2"),
        "urgency_multiplier": Decimal("1.5"),
        "expected_final": Decimal("1175.00"),
        "note": "Surge capped to 3.0",
    },
    {
        "name": "high_traffic",
        "base_price": Decimal("200.00"),
        "urgency": "low",
        "hour": 14,
        "distance_km": Decimal("20.0"),
        "surge": Decimal("1.0"),
        "rating": Decimal("3.0"),
        "night_multiplier": Decimal("1.0"),
        "urgency_multiplier": Decimal("1.0"),
        "expected_final": Decimal("312.00"),
    },
]


# ============================================
# QualityScore Test Constants
# ============================================

QUALITY_SCORE_WEIGHTS = {
    "rating": Decimal("0.5"),
    "eta": Decimal("0.3"),
    "capacity": Decimal("0.2"),
}


def calculate_quality_score(rating, eta_minutes, capacity):
    """
    Calculate agency quality score for dispatch ranking.

    Formula: Score = (Rating × 0.5) + (1/ETA × 0.3) + (Capacity × 0.2)

    Args:
        rating: Agency rating (1.0 to 5.0)
        eta_minutes: Estimated time of arrival in minutes
        capacity: Normalized capacity (0.0 to 1.0)

    Returns:
        Decimal: Quality score
    """
    rating_score = Decimal(str(rating)) * QUALITY_SCORE_WEIGHTS["rating"]
    eta_score = (Decimal("1") / Decimal(str(eta_minutes))) * QUALITY_SCORE_WEIGHTS[
        "eta"
    ]
    capacity_score = Decimal(str(capacity)) * QUALITY_SCORE_WEIGHTS["capacity"]

    return rating_score + eta_score + capacity_score
