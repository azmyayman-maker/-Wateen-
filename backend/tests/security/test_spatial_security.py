import uuid

import pytest
from django.contrib.gis.geos import Polygon
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import AgencyProfile, AgencyStatus, CustomUser


def get_unique_suffix():
    return str(uuid.uuid4().int)[:6]

def get_next_national_id():
    return f"290010101{str(uuid.uuid4().int)[:5]}"

def get_next_phone():
    return f"010{str(uuid.uuid4().int)[:8]}"

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def agency_a(db):
    user = CustomUser.objects.create_user(
        national_id=get_next_national_id(),
        phone_number=get_next_phone(),
        password="testpassword",
        role="AGENCY_ADMIN"
    )
    poly = Polygon.from_bbox((31.0, 30.0, 31.1, 30.1))
    poly.srid = 4326

    agency = AgencyProfile.objects.create(
        manager_name="Agency A",
        commercial_registry=f"CR-{get_unique_suffix()}",
        moh_license_number=f"MOH-{get_unique_suffix()}",
        tax_id=f"TAX-{get_unique_suffix()}",
        status=AgencyStatus.VERIFIED,
        coverage_polygon=poly
    )
    user.agency = agency
    user.save()
    return user

@pytest.fixture
def agency_b(db):
    user = CustomUser.objects.create_user(
        national_id=get_next_national_id(),
        phone_number=get_next_phone(),
        password="testpassword",
        role="AGENCY_ADMIN"
    )
    poly = Polygon.from_bbox((31.5, 30.5, 31.6, 30.6))
    poly.srid = 4326

    agency = AgencyProfile.objects.create(
        manager_name="Agency B",
        commercial_registry=f"CR-{get_unique_suffix()}",
        moh_license_number=f"MOH-{get_unique_suffix()}",
        tax_id=f"TAX-{get_unique_suffix()}",
        status=AgencyStatus.VERIFIED,
        coverage_polygon=poly
    )
    user.agency = agency
    user.save()
    return user

@pytest.mark.django_db
def test_cross_tenant_polygon_manipulation(api_client, agency_a, agency_b):
    """
    Test that Agency A cannot modify the coverage polygon of Agency B.
    Tenant Isolation Test.
    """
    api_client.force_authenticate(user=agency_a)

    # Endpoint to update coverage polygon. Assuming there is a generic update or specific endpoint
    # that handles agency profile updates. The ticket specifically asks for testing this.

    # Let's try to update Agency B's profile
    url = reverse('users:agency_coverage', kwargs={'pk': agency_b.agency.id})

    payload = {
        "coverage_polygon": {
            "type": "Polygon",
            "coordinates": [[[31.0, 30.0], [31.5, 30.0], [31.5, 30.5], [31.0, 30.5], [31.0, 30.0]]]
        }
    }

    response = api_client.put(url, payload, format='json')

    # Due to tenant isolation, Agency A shouldn't even see Agency B's endpoint,
    # expecting 403 Forbidden or 404 Not Found.
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

@pytest.mark.django_db
def test_malformed_geojson_injection(api_client, agency_a):
    """
    Test that uploading malformed or malicious GeoJSON is properly rejected.
    It should yield 400 Bad Request, NOT a 500 Internal Server Error.
    """
    api_client.force_authenticate(user=agency_a)

    url = reverse('users:agency_coverage', kwargs={'pk': agency_a.agency.id})

    # Malformed GeoJSON: self-intersecting / bow-tie polygon
    payload = {
        "coverage_polygon": {
            "type": "Polygon",
            "coordinates": [
                [[0.0, 0.0], [10.0, 10.0], [10.0, 0.0], [0.0, 10.0], [0.0, 0.0]]
            ]
        }
    }

    response = api_client.put(url, payload, format='json')

    # DRF should catch validation errors from GIS and return 400
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Open ring payload (missing the closing coordinate)
    payload_open_ring = {
        "coverage_polygon": {
            "type": "Polygon",
            "coordinates": [
                [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
            ]
        }
    }

    response2 = api_client.put(url, payload_open_ring, format='json')

    assert response2.status_code == status.HTTP_400_BAD_REQUEST
