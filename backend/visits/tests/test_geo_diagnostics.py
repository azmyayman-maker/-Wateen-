from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser, UserRole


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def superadmin_user(db):
    return CustomUser.objects.create_superuser(
        national_id="12345678901234",
        phone_number="01012345678",
        password="password123"
    )

@pytest.fixture
def patient_user(db):
    return CustomUser.objects.create_user(
        national_id="98765432109876",
        phone_number="01112345678",
        password="password123",
        role=UserRole.PATIENT
    )

@pytest.mark.django_db
class TestGeoDiagnosticsPermissions:
    def test_diagnostics_unauthorized(self, api_client):
        url = reverse('geo-diagnostics')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_diagnostics_forbidden_for_patient(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user)
        url = reverse('geo-diagnostics')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_diagnostics_success_for_superadmin(self, api_client, superadmin_user):
        api_client.force_authenticate(user=superadmin_user)
        url = reverse('geo-diagnostics')

        with patch('visits.services.geo_service.get_redis_client') as mock_redis:
            mock_client = mock_redis.return_value
            mock_client.get.side_effect = lambda k: "10" if "hit" in k else "2"

            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert 'cache_hit_rate' in data
            assert 'spatial_index_status' in data
            assert 'nominatim_health' in data
