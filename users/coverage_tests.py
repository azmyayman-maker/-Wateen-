import secrets
from unittest.mock import patch

import pytest
from django.contrib.gis.geos import Polygon
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import AgencyProfile, CustomUser, UserRole
from visits.models import Visit, VisitStatus

@pytest.fixture
def api_client():
    return APIClient()

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
            password=secrets.token_urlsafe(16),
            role=UserRole.AGENCY_ADMIN,
        )
        user.agency = agency
        user.save()
        return agency, user

    @pytest.fixture
    def setup_second_agency(self):
        agency = AgencyProfile.objects.create(
            manager_name="Second Agency",
            commercial_registry="COV-999",
            moh_license_number="COV-MOH-999",
            tax_id="COV-TAX-2"
        )
        
        user = CustomUser.objects.create_user(
            national_id="29001011234569",
            phone_number="01001234569",
            password=secrets.token_urlsafe(16),
            role=UserRole.AGENCY_ADMIN,
        )
        user.agency = agency
        user.save()
        return agency, user

    @patch('visits.tasks.re_evaluate_pending_visits.delay')
    def test_valid_polygon_upload(self, mock_celery, api_client, setup_agency):
        agency, user = setup_agency
        api_client.force_authenticate(user=user)
        
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
        response = api_client.post(url, {'coverage_polygon': valid_geojson}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        agency.refresh_from_db()
        assert agency.coverage_polygon is not None
        assert isinstance(agency.coverage_polygon, Polygon)
        mock_celery.assert_called_once_with(str(agency.id))
        
    def test_get_coverage_properties(self, api_client, setup_agency):
        agency, user = setup_agency
        agency.coverage_polygon = Polygon((
            (31.235, 30.044),
            (31.250, 30.044),
            (31.250, 30.060),
            (31.235, 30.060),
            (31.235, 30.044)
        ))
        agency.save()
        
        api_client.force_authenticate(user=user)
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        props = response.data['properties']
        assert 'area_km2' in props
        assert 'centroid' in props
        assert props['vertex_count'] == 5
        
    def test_cross_tenant_isolation(self, api_client, setup_agency, setup_second_agency):
        agency1, user1 = setup_agency
        agency2, user2 = setup_second_agency
        
        api_client.force_authenticate(user=user1)
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency2.id)})
        
        valid_geojson = {
            "type": "Polygon",
            "coordinates": [[[31.0, 30.0], [31.1, 30.0], [31.1, 30.1], [31.0, 30.1], [31.0, 30.0]]]
        }
        response = api_client.put(url, {'coverage_polygon': valid_geojson}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_spatial_anomaly_unclosed(self, api_client, setup_agency):
        agency, user = setup_agency
        api_client.force_authenticate(user=user)
        invalid_geojson = {
            "type": "Polygon",
            "coordinates": [[[31.0, 30.0], [31.1, 30.0], [31.1, 30.1]]]
        }
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = api_client.post(url, {'coverage_polygon': invalid_geojson}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_spatial_anomaly_self_intersecting(self, api_client, setup_agency):
        agency, user = setup_agency
        api_client.force_authenticate(user=user)
        invalid_geojson = {
            "type": "Polygon",
            "coordinates": [[[0,0], [10,10], [10,0], [0,10], [0,0]]]
        }
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = api_client.post(url, {'coverage_polygon': invalid_geojson}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in str(response.data)

    def test_area_exploitation_max_limit(self, api_client, setup_agency):
        agency, user = setup_agency
        api_client.force_authenticate(user=user)
        invalid_geojson = {
            "type": "Polygon",
            "coordinates": [[[25.0, 22.0], [35.0, 22.0], [35.0, 32.0], [25.0, 32.0], [25.0, 22.0]]]
        }
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = api_client.post(url, {'coverage_polygon': invalid_geojson}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_str = str(response.data)
        assert "5000" in error_str or "exceeds" in error_str.lower()
        
    @patch('visits.tasks.re_evaluate_pending_visits.delay')
    def test_delete_coverage_no_visits(self, mock_celery, api_client, setup_agency):
        agency, user = setup_agency
        agency.coverage_polygon = Polygon(((31.2, 30.0), (31.3, 30.0), (31.3, 30.1), (31.2, 30.1), (31.2, 30.0)))
        agency.save()
        
        api_client.force_authenticate(user=user)
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        agency.refresh_from_db()
        assert agency.coverage_polygon is None
        mock_celery.assert_called_once_with(str(agency.id))
        
    def test_delete_coverage_with_active_visits(self, api_client, setup_agency):
        agency, user = setup_agency
        agency.coverage_polygon = Polygon(((31.2, 30.0), (31.3, 30.0), (31.3, 30.1), (31.2, 30.1), (31.2, 30.0)))
        agency.save()
        
        from users.models import PatientProfile
        patient_user = CustomUser.objects.create_user(
            national_id="12345678901234", phone_number="123", password="pw", role=UserRole.PATIENT
        )
        patient = PatientProfile.objects.create(user=patient_user)
        
        # Create an active visit for the agency
        visit = Visit.objects.create(
            patient=patient,
            agency=agency,
            status=VisitStatus.ACCEPTED,
            pricing_snapshot={}
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('users:agency_coverage', kwargs={'pk': str(agency.id)})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        agency.refresh_from_db()
        assert agency.coverage_polygon is not None
