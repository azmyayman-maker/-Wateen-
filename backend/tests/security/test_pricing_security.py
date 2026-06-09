from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from rest_framework import status

from users.models import CustomUser, PatientProfile, UserRole
from visits.models import ServiceType, Visit, VisitStatus


@pytest.mark.django_db
class TestPricingSecurity:
    """Explicit security verification for price immutability."""

    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        self.client = client
        self.user = CustomUser.objects.create(
            national_id="29012011234567",
            phone_number="+201234567891",
            role=UserRole.PATIENT
        )
        self.patient = PatientProfile.objects.create(user=self.user)
        self.service = ServiceType.objects.create(
            name="Immutability Test Service",
            base_price=Decimal("100.00"),
            expected_duration=30
        )

        self.visit = Visit.objects.create(
            patient=self.patient,
            status=VisitStatus.PENDING_AGENCY,
            location=Point(31.2357, 30.0444, srid=4326),
            service_type=self.service,
            base_price=Decimal("100.00"),
            final_price=Decimal("100.00")
        )
        self.client.force_authenticate(user=self.user)

    def test_patch_price_attempt_returns_fail_or_ignores(self):
        """
        Verify that PATCH /api/v1/visits/{id}/ with a new price:
        1. Returns 405 (since no update endpoint exists for patients)
        2. OR If it exists, verify the price field is NOT updated due to read_only=True and model validation.
        """
        # Note: According to urls.py, there is no generic Visit update endpoint,
        # but we check if someone tried to use a status endpoint or if a generic one exists but isn't listed.
        url = f"/api/v1/visits/{self.visit.id}/" # Generic speculative endpoint

        payload = {"final_price": 5000.00}

        response = self.client.patch(url, payload, format='json')

        # If 404/405, success (no endpoint to hack)
        if response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED]:
            pass
        else:
            # If it somehow works, assert price is still original
            self.visit.refresh_from_db()
            assert self.visit.final_price == Decimal("100.00")

    def test_model_level_enforcement_direct_save(self):
        """Standard check that model save() prevents price hike."""
        self.visit.final_price = Decimal("5000.00")
        with pytest.raises(ValidationError):
            self.visit.save()

        self.visit.refresh_from_db()
        assert self.visit.final_price == Decimal("100.00")
