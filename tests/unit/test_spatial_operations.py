import pytest
from django.contrib.gis.geos import Polygon, Point
from users.models import CustomUser, AgencyProfile, AgencyStatus
from visits.services.geo_service import find_agencies_covering_point, validate_polygon_area_in_km2

import uuid

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
        role="AGENCY_ADMIN"
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
        rating=4.8
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
        role="AGENCY_ADMIN"
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
        rating=4.5
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
    assert hasattr(agencies.first(), 'distance_to_center')

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
        rating=4.8
    )
    point = Point(31.25, 30.05, srid=4326)
    agencies = find_agencies_covering_point(point)
    assert agencies.count() == 0

def test_validate_polygon_area_in_km2_valid():
    poly = Polygon((
        (31.0, 30.0), (31.01, 30.0), (31.01, 30.01), (31.0, 30.01), (31.0, 30.0)
    ))
    poly.srid = 4326
    res = validate_polygon_area_in_km2(poly, max_km2=5000.0)
    assert res is True

def test_validate_polygon_area_in_km2_invalid():
    poly = Polygon((
        (0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0), (0.0, 0.0)
    ))
    poly.srid = 4326
    res = validate_polygon_area_in_km2(poly, max_km2=5000.0)
    assert res is False

