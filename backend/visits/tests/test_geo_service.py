from unittest.mock import MagicMock, patch

import pytest
from django.contrib.gis.geos import Point, Polygon

from users.models import AgencyProfile, AgencyStatus
from visits.services.geo_service import (
    find_agencies_covering_point,
    geocode_address,
)


@pytest.fixture
def mock_redis():
    with patch('visits.services.geo_service.get_redis_client') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_nominatim():
    with patch('requests.get') as mock:
        yield mock

class TestGeocoding:
    def test_geocode_address_success(self, mock_nominatim, mock_redis):
        # Setup
        mock_redis.get.return_value = None  # Cache miss
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"lat": "30.0444", "lon": "31.2357"}]
        mock_nominatim.return_value = mock_response

        # Execute
        result = geocode_address("Cairo, Egypt")

        # Verify
        assert isinstance(result, Point)
        assert result.y == 30.0444
        assert result.x == 31.2357
        mock_nominatim.assert_called_once()
        # Verify caching was called
        mock_redis.setex.assert_called_once()

    def test_geocode_address_cache_hit(self, mock_nominatim, mock_redis):
        # Setup
        mock_redis.get.return_value = '{"lat": 30.0444, "lng": 31.2357}'

        # Execute
        result = geocode_address("Cairo, Egypt")

        # Verify
        assert isinstance(result, Point)
        assert result.y == 30.0444
        assert result.x == 31.2357
        mock_nominatim.assert_not_called()

    def test_geocode_address_not_found(self, mock_nominatim, mock_redis):
        # Setup
        mock_redis.get.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_nominatim.return_value = mock_response

        # Execute
        result = geocode_address("Nonexistent Place")

        # Verify
        assert result is None

class TestSpatialQueries:
    @pytest.mark.django_db
    def test_find_agencies_covering_point_success(self):
        # Setup: Create a verified agency with a coverage polygon (Cairo area)
        cairo_poly = Polygon.from_bbox((31.0, 29.8, 31.5, 30.2)) # min_x, min_y, max_x, max_y
        agency = AgencyProfile.objects.create(
            manager_name="Cairo Agency",
            commercial_registry="123",
            moh_license_number="456",
            tax_id="789",
            status=AgencyStatus.VERIFIED,
            coverage_polygon=cairo_poly
        )

        # Execute: Search for a point inside Cairo
        patient_point = Point(31.2357, 30.0444, srid=4326) # Cairo center
        results = find_agencies_covering_point(patient_point)

        # Verify
        assert len(results) == 1
        assert results[0].id == agency.id
        assert hasattr(results[0], 'distance_to_center')

    @pytest.mark.django_db
    def test_find_agencies_covering_point_exclusion(self):
        # Setup: Cairo agency
        cairo_poly = Polygon.from_bbox((31.0, 29.8, 31.5, 30.2))
        AgencyProfile.objects.create(
            manager_name="Cairo Agency",
            commercial_registry="123",
            moh_license_number="456",
            tax_id="789",
            status=AgencyStatus.VERIFIED,
            coverage_polygon=cairo_poly
        )

        # Execute: Search for a point in Alexandria (outside coverage)
        alex_point = Point(29.9187, 31.2001, srid=4326)
        results = find_agencies_covering_point(alex_point)

        # Verify
        assert len(results) == 0

    @pytest.mark.django_db
    def test_find_agencies_covering_point_unverified_exclusion(self):
        # Setup: Pending agency
        cairo_poly = Polygon.from_bbox((31.0, 29.8, 31.5, 30.2))
        AgencyProfile.objects.create(
            manager_name="Unverified Agency",
            commercial_registry="999",
            moh_license_number="888",
            tax_id="777",
            status=AgencyStatus.PENDING,
            coverage_polygon=cairo_poly
        )

        patient_point = Point(31.2357, 30.0444, srid=4326)
        results = find_agencies_covering_point(patient_point)

        # Verify
        assert len(results) == 0
