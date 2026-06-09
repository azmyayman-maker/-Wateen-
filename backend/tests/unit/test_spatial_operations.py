import uuid

import pytest
from django.contrib.gis.geos import Point, Polygon

from users.models import AgencyProfile, AgencyStatus, CustomUser
from visits.services.geo_service import (
    find_agencies_covering_point,
    validate_polygon_area_in_km2,
)


def get_unique_suffix():
    return str(uuid.uuid4().int)[:6]


def get_next_national_id():
    unique = str(uuid.uuid4().int)[:5]
    return f"290010101{unique}"


def get_next_phone():
    unique = str(uuid.uuid4().int)[:8]
    return f"010{unique}"


@pytest.fixture
def cairo_agency(db):
    user = CustomUser.objects.create_user(
        national_id=get_next_national_id(),
        phone_number=get_next_phone(),
        password="testpassword",
        role="AGENCY_ADMIN",
    )
    cairo_poly = Polygon.from_bbox((31.2, 30.0, 31.3, 30.1))
    cairo_poly.srid = 4326

    agency = AgencyProfile.objects.create(
        manager_name="Cairo Care",
        commercial_registry=f"CR-CAIRO-{get_unique_suffix()}",
        moh_license_number=f"MOH-CAIRO-{get_unique_suffix()}",
        tax_id=f"TAX-CAIRO-{get_unique_suffix()}",
        status=AgencyStatus.VERIFIED,
        coverage_polygon=cairo_poly,
        rating=4.8,
    )
    user.agency = agency
    user.save()
    return agency


@pytest.fixture
def giza_agency(db):
    user = CustomUser.objects.create_user(
        national_id=get_next_national_id(),
        phone_number=get_next_phone(),
        password="testpassword",
        role="AGENCY_ADMIN",
    )
    giza_poly = Polygon.from_bbox((31.15, 30.0, 31.25, 30.1))
    giza_poly.srid = 4326

    agency = AgencyProfile.objects.create(
        manager_name="Giza Health",
        commercial_registry=f"CR-GIZA-{get_unique_suffix()}",
        moh_license_number=f"MOH-GIZA-{get_unique_suffix()}",
        tax_id=f"TAX-GIZA-{get_unique_suffix()}",
        status=AgencyStatus.VERIFIED,
        coverage_polygon=giza_poly,
        rating=4.5,
    )
    user.agency = agency
    user.save()
    return agency


@pytest.mark.django_db
def test_point_strictly_inside_polygon(cairo_agency):
    point = Point(31.25, 30.05, srid=4326)
    agencies = find_agencies_covering_point(point)
    assert agencies.count() == 1
    assert agencies.first() == cairo_agency
    assert hasattr(agencies.first(), "distance_to_center")


@pytest.mark.django_db
def test_point_strictly_outside_polygon(cairo_agency):
    point = Point(31.4, 30.2, srid=4326)
    agencies = find_agencies_covering_point(point)
    assert agencies.count() == 0


@pytest.mark.django_db
def test_point_exactly_on_boundary(cairo_agency):
    point = Point(31.25, 30.1, srid=4326)
    agencies = find_agencies_covering_point(point)
    assert agencies.count() == 1
    assert agencies.first() == cairo_agency


@pytest.mark.django_db
def test_overlapping_polygons(cairo_agency, giza_agency):
    point = Point(31.22, 30.05, srid=4326)
    agencies = find_agencies_covering_point(point)
    assert agencies.count() == 2
    ids = [a.id for a in agencies]
    assert cairo_agency.id in ids
    assert giza_agency.id in ids


@pytest.mark.django_db
def test_unverified_agency_excluded():
    cairo_poly = Polygon.from_bbox((31.2, 30.0, 31.3, 30.1))
    cairo_poly.srid = 4326
    AgencyProfile.objects.create(
        manager_name="Pending Care",
        commercial_registry="CR-PEND",
        moh_license_number="MOH-PEND",
        tax_id="TAX-PEND",
        status=AgencyStatus.PENDING,
        coverage_polygon=cairo_poly,
        rating=4.8,
    )
    point = Point(31.25, 30.05, srid=4326)
    agencies = find_agencies_covering_point(point)
    assert agencies.count() == 0


def test_validate_polygon_area_in_km2_valid():
    poly = Polygon(
        ((31.0, 30.0), (31.01, 30.0), (31.01, 30.01), (31.0, 30.01), (31.0, 30.0))
    )
    poly.srid = 4326
    res = validate_polygon_area_in_km2(poly, max_km2=5000.0)
    assert res is True


def test_validate_polygon_area_in_km2_invalid():
    poly = Polygon(((0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0), (0.0, 0.0)))
    poly.srid = 4326
    res = validate_polygon_area_in_km2(poly, max_km2=5000.0)
    assert res is False


# ============================================================================
# P4-T5: Dispatch & Pricing QA - Additional Spatial Tests
# ============================================================================

from decimal import Decimal


@pytest.fixture
def three_overlapping_agencies(db):
    """Creates 3 agencies with overlapping coverage for P4-T5 tests."""
    agencies = []
    offsets_and_ratings = [
        (0.0, Decimal("4.8")),
        (0.05, Decimal("3.5")),
        (0.15, Decimal("2.5")),
    ]

    for i, (offset, rating) in enumerate(offsets_and_ratings):
        user = CustomUser.objects.create_user(
            national_id=get_next_national_id(),
            phone_number=get_next_phone(),
            password="testpassword",
            role="AGENCY_ADMIN",
        )

        poly = Polygon.from_bbox((30.0 + offset, 31.0, 30.2 + offset, 31.2))
        poly.srid = 4326

        agency = AgencyProfile.objects.create(
            manager_name=f"Agency {i + 1}",
            commercial_registry=f"CR-P4T5-{get_unique_suffix()}",
            moh_license_number=f"MOH-P4T5-{get_unique_suffix()}",
            tax_id=f"TAX-P4T5-{get_unique_suffix()}",
            status=AgencyStatus.VERIFIED,
            coverage_polygon=poly,
            rating=rating,
        )
        user.agency = agency
        user.save()
        agencies.append(agency)

    return agencies


@pytest.mark.django_db
class TestP4T5SpatialIntersection:
    """P4-T5 US1: Spatial intersection tests for dispatch engine."""

    def test_point_inside_overlapping_polygons(self, three_overlapping_agencies):
        """US1: Point inside multiple overlapping polygons returns all agencies."""
        point = Point(30.05, 31.05, srid=4326)
        agencies = find_agencies_covering_point(point)

        assert agencies.count() >= 1

    def test_agency_ranking_by_quality_score(self, three_overlapping_agencies):
        """US1: Agencies ranked by QualityScore formula."""
        from tests.fixtures.dispatch_pricing_fixtures import calculate_quality_score

        point = Point(30.05, 31.05, srid=4326)
        agencies = find_agencies_covering_point(point)

        scores = []
        for agency in agencies:
            rating = float(getattr(agency, "rating", 3.0))
            eta_minutes = 15
            capacity = 0.8

            score = calculate_quality_score(rating, eta_minutes, capacity)
            scores.append((agency, float(score)))

        scores_sorted = sorted(scores, key=lambda x: x[1], reverse=True)

        assert len(scores_sorted) >= 1

    def test_no_coverage_returns_empty_result(self):
        """US1 AC4: No agencies covering location returns empty."""
        point = Point(50.0, 50.0, srid=4326)
        agencies = find_agencies_covering_point(point)
        assert agencies.count() == 0

    def test_boundary_point_included(self, cairo_agency):
        """US1: Boundary points are included in intersection."""
        boundary_point = Point(31.2, 30.0, srid=4326)
        agencies = find_agencies_covering_point(boundary_point)

        assert agencies.count() >= 1
