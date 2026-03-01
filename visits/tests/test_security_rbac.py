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
        
        url = reverse("invite-nurse")
        data = {
            "national_id": "29001011234567",
            "phone_number": "+201012345678",
            "first_name_ar": "Test",
            "last_name_ar": "User"
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "permission" in str(response.data).lower()

    def test_patient_cannot_access_manual_dispatch(self, api_client, patient, sample_agency, sample_visit):
        """
        PATIENT role should get 403 Forbidden when trying to hit
        the manual dispatch endpoint (AGENCY_ADMIN only).
        """
        api_client.force_authenticate(user=patient.user)
        
        url = reverse("manual-dispatch", kwargs={"agency_id": sample_agency.id})
        data = {
            "visit_id": str(sample_visit.id),
            "nurse_id": "00000000-0000-0000-0000-000000000000"
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestFinancialTampering:
    """
    Validates that sensitive financial fields cannot be modified
    by patients (or any client) via standard endpoints.
    """

    def test_patient_cannot_patch_visit_price(self, api_client, patient, sample_visit):
        """
        If a patient tries to PATCH a visit to change the final_price,
        the serializer should ignore it (fields are read-only).
        """
        api_client.force_authenticate(user=patient.user)
        
        url = reverse("visit-detail", kwargs={"pk": sample_visit.id})
        
        # In DRF, standard ViewSets might allow PATCH.
        # But our serializers shouldn't accept `final_price` as a writable field.
        original_price = sample_visit.final_price
        
        data = {
            "final_price": "10.00",  # Trying to hack the price
            "base_price": "5.00"
        }
        
        response = api_client.patch(url, data)
        
        # It might return 200 (if it just ignores the fields and updates nothing else)
        # or 403 (if it's a completely unauthorized endpoint for patients).
        # What matters is the DB is NOT updated.
        sample_visit.refresh_from_db()
        
        assert sample_visit.final_price == original_price
        assert sample_visit.final_price != "10.00"
