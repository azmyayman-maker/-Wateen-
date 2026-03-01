import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test import override_settings
from users.models import UserRole, PatientProfile, NurseProfile
from visits.models import ServiceType, Visit, VisitStatus
from decimal import Decimal
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.conf import settings

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def patient_user(db):
    user = User.objects.create_user(
        national_id="29001010100000",
        phone_number="01000000000",
        password="password123",
        role=UserRole.PATIENT,
        first_name_ar="Test",
        last_name_ar="Patient"
    )
    # Profile created by signal
    return user

@pytest.fixture
def nurse_user(db):
    user = User.objects.create_user(
        national_id="29001010100001",
        phone_number="01000000001",
        password="password123",
        role=UserRole.NURSE,
        first_name_ar="Test",
        last_name_ar="Nurse"
    )
    # Profile created by signal
    return user

@pytest.fixture
def auth_tokens(patient_user, api_client):
    response = api_client.post('/api/v1/auth/token/', {
        'national_id': patient_user.national_id,
        'password': 'password123'
    })
    return response.data

@pytest.fixture
def service_type(db):
    return ServiceType.objects.create(
        name="Nursing",
        base_price=Decimal("100.00"),
        surge_multiplier=Decimal("1.0"),
        is_active=True
    )

@pytest.mark.django_db
class TestAuthentication:
    
    def test_register_patient(self, api_client):
        """TC001: Test user registration with valid patient payload"""
        payload = {
            "national_id": "29001010100002",
            "phone_number": "01000000002",
            "password": "password123",
            "role": "PATIENT",
            "first_name_ar": "New",
            "last_name_ar": "Patient"
        }
        response = api_client.post('/api/v1/auth/register/', payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert response.data['role'] == 'PATIENT'

    def test_login_token(self, api_client, patient_user):
        """TC002: Test token obtain with valid credentials"""
        payload = {
            "national_id": patient_user.national_id,
            "password": "password123"
        }
        response = api_client.post('/api/v1/auth/token/', payload)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_token_refresh(self, api_client, auth_tokens):
        """TC003: Test token refresh with valid refresh token"""
        payload = {
            "refresh": auth_tokens['refresh']
        }
        response = api_client.post('/api/v1/auth/token/refresh/', payload)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_logout(self, api_client, auth_tokens):
        """TC004: Test logout with valid access token"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")
        payload = {
            "refresh": auth_tokens['refresh']
        }
        response = api_client.post('/api/v1/auth/logout/', payload)
        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_get_profile(self, api_client, patient_user, auth_tokens):
        """TC005: Test retrieve user profile"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")
        response = api_client.get('/api/v1/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['national_id'] == patient_user.national_id

    def test_update_profile(self, api_client, patient_user, auth_tokens):
        """TC006: Test update user profile"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")
        payload = {
            "first_name_ar": "Updated Name"
        }
        response = api_client.patch('/api/v1/profile/', payload)
        assert response.status_code == status.HTTP_200_OK
        patient_user.refresh_from_db()
        assert patient_user.first_name_ar == "Updated Name"


@pytest.mark.django_db
@override_settings(DEBUG=True)
class TestVisits:
    
    def test_estimate_visit_price(self, api_client, auth_tokens, service_type):
        """TC007: Test visit price estimation"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")
        payload = {
            "service_id": str(service_type.id),
            "latitude": 30.0444,
            "longitude": 31.2357
        }
        response = api_client.post('/api/v1/visits/estimate/', payload)
        assert response.status_code == status.HTTP_200_OK
        assert 'total' in response.data
        assert 'breakdown' in response.data

    def test_create_visit_request(self, api_client, auth_tokens, service_type):
        """TC008: Test visit request creation"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")
        payload = {
            "service_type": str(service_type.id),
            "latitude": 30.0444,
            "longitude": 31.2357,
            "notes": "Urgent visit",
            "vitals_consent": True
        }
        response = api_client.post('/api/v1/visits/request/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert response.data['status'] == 'PENDING'

    def test_payment_webhook_mock(self, api_client, auth_tokens, service_type, patient_user):
        """TC009: Test mock payment webhook"""
        # Create a visit first to pay for
        visit = Visit.objects.create(
            patient=patient_user.patient_profile,
            service_type=service_type,
            status=VisitStatus.PENDING_AGENCY,
            location=Point(31.2357, 30.0444)
        )
        
        payload = {
            "visit_id": str(visit.id),
            "status": "success",
            "transaction_id": "TXN_123456"
        }
        
        mock_token = settings.SECRET_KEY[:20] if settings.SECRET_KEY else "dev-only-token"
        api_client.credentials(HTTP_X_MOCK_TOKEN=mock_token)
        
        response = api_client.post('/api/v1/visits/payments/webhook/mock/', payload)
        assert response.status_code == status.HTTP_200_OK
