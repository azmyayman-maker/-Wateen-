import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import AgencyProfile, AgencyStatus, CustomUser

@pytest.fixture
def api_client():
    """Provide DRF APIClient instead of Django's default test client."""
    return APIClient()

@pytest.mark.django_db
class TestAgencyOnboarding:
    def test_agency_registration(self, api_client):
        url = reverse('users:agency_register')
        data = {
            'manager_name': 'Test Manager',
            'commercial_registry': '123456789',
            'moh_license_number': 'MOH-123',
            'tax_id': 'TAX-123',
            'admin_national_id': '29001011234567',
            'admin_phone_number': '01001234567',
            'admin_password': 'SecurePassword123!'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify agency creation
        agency = AgencyProfile.objects.get(commercial_registry='123456789')
        assert agency.status == AgencyStatus.PENDING
        assert agency.manager_name == 'Test Manager'
        
        # Verify user creation
        user = CustomUser.objects.get(national_id='29001011234567')
        assert user.role == 'AGENCY_ADMIN'
        
    def test_superadmin_agency_approval(self, api_client):
        # Create an agency
        agency = AgencyProfile.objects.create(
            manager_name='Test Manager',
            commercial_registry='987654321',
            moh_license_number='MOH-987',
            tax_id='TAX-987'
        )
        assert agency.status == AgencyStatus.PENDING
        
        # Create superuser and authenticate
        superuser = CustomUser.objects.create_superuser(
            national_id='28001011234567',
            phone_number='01101234567',
            password='Password123!',
        )
        api_client.force_authenticate(user=superuser)
        
        # Approve the agency
        url = reverse('users:agency_approve', kwargs={'pk': str(agency.id)})
        response = api_client.patch(url, {'status': AgencyStatus.VERIFIED}, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        if 'status' in response.data:
            assert response.data['status'] == AgencyStatus.VERIFIED
            
        agency.refresh_from_db()
        assert agency.status == AgencyStatus.VERIFIED
        
    def test_non_admin_cannot_approve(self, api_client):
        # Create an agency
        agency = AgencyProfile.objects.create(
            manager_name='Test Manager',
            commercial_registry='555555555',
            moh_license_number='MOH-555',
            tax_id='TAX-555'
        )
        
        # Create normal user and authenticate
        user = CustomUser.objects.create_user(
            national_id='27001011234567',
            phone_number='01201234567',
            password='Password123!',
        )
        api_client.force_authenticate(user=user)
        
        url = reverse('users:agency_approve', kwargs={'pk': str(agency.id)})
        response = api_client.patch(url, {'status': AgencyStatus.VERIFIED}, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        agency.refresh_from_db()
        assert agency.status == AgencyStatus.PENDING
