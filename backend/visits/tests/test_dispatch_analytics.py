"""
Tests for the Dispatch Analytics Admin API.

Tests cover:
- SuperAdmin permission enforcement
- Analytics calculations (dispatch success rate, cancellation rate)
- Response time metrics using nurse_assigned_at field
- Edge cases (no visits, partial data)
"""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from users.models import (
    AgencyProfile,
    AgencyStatus,
    CustomUser,
    NurseProfile,
    PatientProfile,
)
from visits.models import ServiceType, Visit, VisitStatus


class TestDispatchAnalyticsAPI(TestCase):
    """Test the DispatchAnalyticsAPIView endpoint."""

    def setUp(self):
        """Create test users and data."""
        # SuperAdmin user
        self.superadmin = CustomUser.objects.create_user(
            national_id="00000000000000",
            password="adminpass123",
            role=CustomUser.Role.SUPERADMIN,
        )

        # Regular admin (should be denied)
        self.agency_admin = CustomUser.objects.create_user(
            national_id="11111111111111",
            password="userpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )

        # Agency for visits
        self.agency = AgencyProfile.objects.create(
            user=self.agency_admin,
            manager_name="Test Agency",
            commercial_registry="CR001",
            moh_license_number="MOH001",
            tax_id="TAX001",
            status=AgencyStatus.VERIFIED,
        )

        # Patient
        self.patient_user = CustomUser.objects.create_user(
            national_id="22222222222222",
            password="patientpass123",
            role=CustomUser.Role.PATIENT,
        )
        self.patient = PatientProfile.objects.create(
            user=self.patient_user,
            date_of_birth=timezone.now().date() - timedelta(days=365 * 30),
        )

        # Nurse
        self.nurse_user = CustomUser.objects.create_user(
            national_id="33333333333333",
            password="nursepass123",
            role=CustomUser.Role.NURSE,
        )
        self.nurse = NurseProfile.objects.create(
            user=self.nurse_user, agency=self.agency
        )

        # Service type
        self.service_type = ServiceType.objects.create(
            name="General Nursing", name_ar="تمريض عام", base_price=Decimal("200.00")
        )

        self.client = APIClient()

    def test_superuser_can_access_endpoint(self):
        """SuperAdmin should have access to analytics."""
        self.client.force_authenticate(user=self.superadmin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("dispatch_success_rate", response.data)

    def test_non_superuser_denied(self):
        """Non-superadmin users should receive 403 Forbidden."""
        self.client.force_authenticate(user=self.agency_admin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_denied(self):
        """Unauthenticated requests should receive 401."""
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_database_returns_zeros(self):
        """With no visits, should return zero values."""
        self.client.force_authenticate(user=self.superadmin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["dispatch_success_rate"], 0.0)
        self.assertEqual(response.data["cancellation_rate"], 0.0)
        self.assertIsNone(response.data["avg_time_to_nurse_assignment"])
        self.assertEqual(response.data["total_visits"], 0)

    def test_dispatch_success_rate_calculation(self):
        """Dispatch success rate = completed / total."""
        # Create 10 visits: 7 completed, 3 pending
        for _ in range(7):
            Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                service_type=self.service_type,
                status=VisitStatus.COMPLETED,
            )

        for _ in range(3):
            Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                service_type=self.service_type,
                status=VisitStatus.PENDING_AGENCY,
            )

        self.client.force_authenticate(user=self.superadmin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        # 7 completed out of 10 total = 70%
        self.assertEqual(response.data["dispatch_success_rate"], 70.0)
        self.assertEqual(response.data["total_visits"], 10)
        self.assertEqual(response.data["completed_visits"], 7)

    def test_cancellation_rate_calculation(self):
        """Cancellation rate = cancelled / total."""
        # Create 20 visits: 15 completed, 5 cancelled
        for _ in range(15):
            Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                service_type=self.service_type,
                status=VisitStatus.COMPLETED,
            )

        for _ in range(5):
            Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                service_type=self.service_type,
                status=VisitStatus.CANCELLED,
            )

        self.client.force_authenticate(user=self.superadmin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        # 5 cancelled out of 20 total = 25%
        self.assertEqual(response.data["cancellation_rate"], 25.0)
        self.assertEqual(response.data["cancelled_visits"], 5)

    def test_avg_time_to_nurse_assignment_with_timestamps(self):
        """Avg time should use nurse_assigned_at field."""
        now = timezone.now()

        # Create visit assigned 30 minutes after creation
        visit1 = Visit.objects.create(
            patient=self.patient,
            agency=self.agency,
            service_type=self.service_type,
            status=VisitStatus.COMPLETED,
            created_at=now - timedelta(hours=2),
            nurse_assigned_at=now - timedelta(hours=2) + timedelta(minutes=30),
        )

        # Create visit assigned 60 minutes after creation
        visit2 = Visit.objects.create(
            patient=self.patient,
            agency=self.agency,
            service_type=self.service_type,
            status=VisitStatus.COMPLETED,
            created_at=now - timedelta(hours=3),
            nurse_assigned_at=now - timedelta(hours=3) + timedelta(minutes=60),
        )

        self.client.force_authenticate(user=self.superadmin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        # Average should be (30 + 60) / 2 = 45 minutes
        self.assertEqual(response.data["avg_time_to_nurse_assignment"], "45m 0s")
        self.assertEqual(response.data["avg_assignment_time_minutes"], 45.0)

    def test_avg_time_excludes_visits_without_nurse_timestamp(self):
        """Visits without nurse_assigned_at should not affect average."""
        now = timezone.now()

        # Visit with nurse_assigned_at
        visit1 = Visit.objects.create(
            patient=self.patient,
            agency=self.agency,
            service_type=self.service_type,
            status=VisitStatus.COMPLETED,
            created_at=now - timedelta(hours=1),
            nurse_assigned_at=now - timedelta(minutes=30),
        )

        # Visit WITHOUT nurse_assigned_at (legacy data)
        visit2 = Visit.objects.create(
            patient=self.patient,
            agency=self.agency,
            service_type=self.service_type,
            status=VisitStatus.COMPLETED,
            nurse=self.nurse,
            created_at=now - timedelta(hours=2),
            # No nurse_assigned_at
        )

        self.client.force_authenticate(user=self.superadmin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        # Only visit1 should contribute to average
        self.assertEqual(response.data["avg_assignment_time_minutes"], 30.0)

    def test_no_nurse_assignments_returns_none(self):
        """If no visits have nurse_assigned_at, should return None."""
        # Create visits without nurse_assigned_at
        for _ in range(5):
            Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                nurse=self.nurse,
                service_type=self.service_type,
                status=VisitStatus.COMPLETED,
            )

        self.client.force_authenticate(user=self.superadmin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        self.assertIsNone(response.data["avg_time_to_nurse_assignment"])
        self.assertIsNone(response.data["avg_assignment_time_minutes"])

    def test_response_includes_all_required_fields(self):
        """Response should include all documented fields."""
        self.client.force_authenticate(user=self.superadmin)
        url = reverse("visits:dispatch_analytics")
        response = self.client.get(url)

        expected_fields = [
            "dispatch_success_rate",
            "cancellation_rate",
            "avg_time_to_nurse_assignment",
            "avg_assignment_time_minutes",
            "total_visits",
            "completed_visits",
            "cancelled_visits",
        ]

        for field in expected_fields:
            self.assertIn(field, response.data)
