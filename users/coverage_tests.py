import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.gis.geos import Polygon

from users.models import AgencyProfile, CustomUser

@pytest.mark.django_db
class TestAgencyCoverageValidation:
    
    @pytest.fixture
    def setup_agency(self):
        agency = AgencyProfile.objects.create(
            manager_name="Coverage Test Agency",
            commercial_registry="COV-123",
            moh_license_number="COV-MOH-123",
            tax_id="COV-TAX"
        )
        
        user = CustomUser.objects.create_user(
            national_id="29001011234568",
            phone_number="01001234568",
            password="Password1234!",
            role="ADMIN"
        )
        return agency, user

    def test_valid_polygon_upload(self, client, setup_agency):
        agency, user = setup_agency
        client.force_authenticate(user=user)
        
        valid_geojson = {
            "type": "Polygon",
            "coordinates": [
                [
                    [31.235, 30.044],
                    [31.250, 30.044],
                    [31.250, 30.060],
                    [31.235, 30.060],
                    [31.235, 30.044]
                ]
            ]
        }
        
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = client.post(url, {'coverage_polygon': valid_geojson}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        agency.refresh_from_db()
        assert agency.coverage_polygon is not None
        assert isinstance(agency.coverage_polygon, Polygon)

    def test_invalid_geometry_upload(self, client, setup_agency):
        agency, user = setup_agency
        client.force_authenticate(user=user)
        
        # Point is invalid, we only accept Polygon/MultiPolygon
        invalid_geojson = {
            "type": "Point",
            "coordinates": [31.235, 30.044]
        }
        
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = client.post(url, {'coverage_polygon': invalid_geojson}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Geometry must be a Polygon" in str(response.data)

    def test_malformed_geojson(self, client, setup_agency):
        agency, user = setup_agency
        client.force_authenticate(user=user)
        
        # Malformed geojson (missing necessary closing brackets/coordinates)
        malformed_geojson = {
            "type": "Polygon",
            "coordinates": [[[31.235]]]
        }
        
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = client.post(url, {'coverage_polygon': malformed_geojson}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid GeoJSON format" in str(response.data)
