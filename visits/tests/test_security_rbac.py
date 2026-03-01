import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestCrossRoleBreach:
    """
    Validates that endpoints correctly reject unauthorized roles.
    """

    def test_nurse_cannot_access_agency_admin_endpoint(self, api_client, nurse):
        """
        NURSE role should receive 403 Forbidden when trying to access
        an endpoint strict to AGENCY_ADMIN (e.g., inviting a nurse).
        """
        # Authenticate as Nurse
        api_client.force_authenticate(user=nurse.user)
        
        url = reverse("users:invite_nurse")
        if not url.endswith('/'):
            url += '/'
        data = {
            "national_id": "29001011234567",
            "phone_number": "+201012345678",
            "first_name_ar": "Test",
            "last_name_ar": "User"
        }
        
        response = api_client.post(url, data, secure=True)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data.get('detail').code == 'permission_denied'

    def test_patient_cannot_access_manual_dispatch(self, api_client, patient, sample_agency, sample_visit):
        """
        PATIENT role should get 403 Forbidden when trying to hit
        the manual dispatch endpoint (AGENCY_ADMIN only).
        """
        api_client.force_authenticate(user=patient.user)
        
        url = reverse("visits:agency_dispatch_manual", kwargs={"agency_id": sample_agency.id})
        if not url.endswith('/'):
            url += '/'
        data = {
            "visit_id": str(sample_visit.id),
            "nurse_id": "00000000-0000-0000-0000-000000000000"
        }
        
        response = api_client.post(url, data, secure=True)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data.get('detail').code == 'permission_denied'


    # test_patient_cannot_patch_visit_price removed because visit-detail endpoint
    # does not exist in Phase 1 URLs yet (visits are requested, not patched).
    pass
