"""
Tests for the Agency Stats Service.

Tests cover:
- Operational stats computation (response_rate, acceptance_rate, dispute_rate)
- Cache hit/miss behavior
- Default values for new agencies
- Query optimization (single aggregate vs. multiple queries)
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from users.models import AgencyProfile, AgencyStatus, CustomUser
from users.services.agency_stats_service import (
    CACHE_TTL,
    _compute_stats_from_db,
    get_agency_operational_stats,
    refresh_agency_stats,
)
from visits.models import ServiceType, Visit, VisitStatus


class TestComputeStatsFromDB(TestCase):
    """Test stats computation directly from database."""

    def setUp(self):
        """Create test agency with visits."""
        self.user = CustomUser.objects.create_user(
            national_id="12345678901234",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )
        self.agency = AgencyProfile.objects.create(
            user=self.user,
            manager_name="Test Manager",
            commercial_registry="CR001",
            moh_license_number="MOH001",
            tax_id="TAX001",
            status=AgencyStatus.VERIFIED,
        )

        # Create patient for visits
        self.patient_user = CustomUser.objects.create_user(
            national_id="11111111111111",
            password="testpass123",
            role=CustomUser.Role.PATIENT,
        )
        from users.models import PatientProfile

        self.patient = PatientProfile.objects.create(
            user=self.patient_user,
            date_of_birth=timezone.now().date() - timedelta(days=365 * 30),
        )

        # Create nurse
        self.nurse_user = CustomUser.objects.create_user(
            national_id="22222222222222",
            password="testpass123",
            role=CustomUser.Role.NURSE,
        )
        from users.models import NurseProfile

        self.nurse = NurseProfile.objects.create(
            user=self.nurse_user, agency=self.agency
        )

        self.service_type = ServiceType.objects.create(
            name="General Nursing", name_ar="تمريض عام", base_price=Decimal("200.00")
        )

    def test_computes_stats_for_agency_with_visits(self):
        """Should compute response, acceptance, and dispute rates correctly."""
        # Create visits with different statuses
        # 10 total visits
        for i in range(10):
            visit = Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                service_type=self.service_type,
                status=VisitStatus.COMPLETED,
            )
            if i < 8:  # 8 have nurse assigned (response_rate = 0.8)
                visit.nurse = self.nurse
                visit.save()

        stats = _compute_stats_from_db(self.agency.id)

        self.assertEqual(stats["response_rate"], 0.8)
        self.assertEqual(stats["acceptance_rate"], 1.0)  # All completed
        self.assertEqual(stats["dispute_rate"], 0.0)

    def test_handles_cancelled_visits_with_nurse(self):
        """Cancelled visits with nurse assigned should count as disputes."""
        # Create visits
        for i in range(10):
            visit = Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                service_type=self.service_type,
                status=VisitStatus.COMPLETED,
            )

        # Create 2 cancelled visits with nurse (disputes)
        for i in range(2):
            visit = Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                nurse=self.nurse,
                service_type=self.service_type,
                status=VisitStatus.CANCELLED,
            )

        stats = _compute_stats_from_db(self.agency.id)

        # Total: 12, Disputes: 2, Response: 2/12
        self.assertAlmostEqual(stats["dispute_rate"], 2 / 12, places=2)

    def test_handles_agency_with_no_visits(self):
        """Agency with no visits should return default values."""
        new_user = CustomUser.objects.create_user(
            national_id="99999999999999",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )
        new_agency = AgencyProfile.objects.create(
            user=new_user,
            manager_name="New Manager",
            commercial_registry="CR999",
            moh_license_number="MOH999",
            tax_id="TAX999",
            status=AgencyStatus.VERIFIED,
        )

        stats = _compute_stats_from_db(new_agency.id)

        self.assertEqual(stats["response_rate"], 0.5)
        self.assertEqual(stats["acceptance_rate"], 0.5)
        self.assertEqual(stats["dispute_rate"], 0.0)

    def test_uses_last_100_visits_only(self):
        """Should only consider last 100 visits by created_at desc."""
        # Create 200 visits, first 100 pending, last 100 completed
        for i in range(200):
            Visit.objects.create(
                patient=self.patient,
                agency=self.agency,
                service_type=self.service_type,
                status=VisitStatus.COMPLETED
                if i >= 100
                else VisitStatus.PENDING_AGENCY,
            )

        stats = _compute_stats_from_db(self.agency.id)

        # Last 100 are all completed, so acceptance_rate should be 1.0
        self.assertEqual(stats["acceptance_rate"], 1.0)

    def test_handles_database_errors_gracefully(self):
        """Should return defaults on database errors."""
        with patch(
            "users.services.agency_stats_service.Visit.objects.filter"
        ) as mock_filter:
            mock_filter.side_effect = Exception("Database error")

            stats = _compute_stats_from_db(uuid4())

            self.assertEqual(stats["response_rate"], 0.5)
            self.assertEqual(stats["acceptance_rate"], 0.5)
            self.assertEqual(stats["dispute_rate"], 0.0)


class TestGetAgencyOperationalStats(TestCase):
    """Test cache layer for stats retrieval."""

    def setUp(self):
        """Clear cache before each test."""
        cache.clear()

    def test_returns_cached_stats_on_hit(self):
        """Should return cached stats without DB query."""
        agency_id = uuid4()
        cached_stats = {
            "response_rate": 0.9,
            "acceptance_rate": 0.85,
            "dispute_rate": 0.05,
        }
        cache.set(f"agency_stats_{agency_id}", cached_stats, CACHE_TTL)

        stats = get_agency_operational_stats(agency_id)

        self.assertEqual(stats, cached_stats)

    def test_computes_and_caches_on_miss(self):
        """Should compute stats and cache them on cache miss."""
        user = CustomUser.objects.create_user(
            national_id="12345678901234",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )
        agency = AgencyProfile.objects.create(
            user=user,
            manager_name="Test",
            commercial_registry="CR001",
            moh_license_number="MOH001",
            tax_id="TAX001",
            status=AgencyStatus.VERIFIED,
        )

        stats = get_agency_operational_stats(agency.id)

        # Should have computed and cached
        cached = cache.get(f"agency_stats_{agency.id}")
        self.assertIsNotNone(cached)
        self.assertEqual(cached, stats)

    def test_handles_cache_failure_gracefully(self):
        """Should still compute stats even if cache is inaccessible."""
        user = CustomUser.objects.create_user(
            national_id="88888888888888",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )
        agency = AgencyProfile.objects.create(
            user=user,
            manager_name="Test",
            commercial_registry="CR002",
            moh_license_number="MOH002",
            tax_id="TAX002",
            status=AgencyStatus.VERIFIED,
        )

        with patch("users.services.agency_stats_service.cache.get") as mock_get:
            mock_get.side_effect = Exception("Redis error")

            stats = get_agency_operational_stats(agency.id)

            # Should still return stats from DB
            self.assertIn("response_rate", stats)
            self.assertIn("acceptance_rate", stats)


class TestRefreshAgencyStats(TestCase):
    """Test Celery task for cache warming."""

    def setUp(self):
        """Clear cache before each test."""
        cache.clear()

    def test_refreshes_all_verified_agencies(self):
        """Should refresh cache for all verified agencies."""
        agencies = []
        for i in range(3):
            user = CustomUser.objects.create_user(
                national_id=f"1234567890123{i}",
                password="testpass123",
                role=CustomUser.Role.AGENCY_ADMIN,
            )
            agency = AgencyProfile.objects.create(
                user=user,
                manager_name=f"Manager {i}",
                commercial_registry=f"CR00{i}",
                moh_license_number=f"MOH00{i}",
                tax_id=f"TAX00{i}",
                status=AgencyStatus.VERIFIED,
            )
            agencies.append(agency)

        count = refresh_agency_stats()

        self.assertEqual(count, 3)

        # Verify all are cached
        for agency in agencies:
            cached = cache.get(f"agency_stats_{agency.id}")
            self.assertIsNotNone(cached)

    def test_skips_non_verified_agencies(self):
        """Should only cache verified agencies."""
        user1 = CustomUser.objects.create_user(
            national_id="11111111111111",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )
        verified = AgencyProfile.objects.create(
            user=user1,
            manager_name="Verified",
            commercial_registry="CR_V",
            moh_license_number="MOH_V",
            tax_id="TAX_V",
            status=AgencyStatus.VERIFIED,
        )

        user2 = CustomUser.objects.create_user(
            national_id="22222222222222",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )
        pending = AgencyProfile.objects.create(
            user=user2,
            manager_name="Pending",
            commercial_registry="CR_P",
            moh_license_number="MOH_P",
            tax_id="TAX_P",
            status=AgencyStatus.PENDING,
        )

        count = refresh_agency_stats()

        self.assertEqual(count, 1)
        self.assertIsNotNone(cache.get(f"agency_stats_{verified.id}"))
        self.assertIsNone(cache.get(f"agency_stats_{pending.id}"))


class TestQueryCount(TestCase):
    """Verify single-query optimization."""

    def test_single_aggregate_query(self):
        """Stats computation should use exactly 1 query for counting."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        user = CustomUser.objects.create_user(
            national_id="12345678901234",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )
        agency = AgencyProfile.objects.create(
            user=user,
            manager_name="Test",
            commercial_registry="CR_Q",
            moh_license_number="MOH_Q",
            tax_id="TAX_Q",
            status=AgencyStatus.VERIFIED,
        )

        # Create sample visits
        patient_user = CustomUser.objects.create_user(
            national_id="99999999999999",
            password="testpass123",
            role=CustomUser.Role.PATIENT,
        )
        from users.models import PatientProfile

        patient = PatientProfile.objects.create(
            user=patient_user,
            date_of_birth=timezone.now().date() - timedelta(days=365 * 30),
        )

        service_type = ServiceType.objects.create(
            name="Test Service", name_ar="خدمة اختبار", base_price=Decimal("150.00")
        )

        for i in range(5):
            Visit.objects.create(
                patient=patient,
                agency=agency,
                service_type=service_type,
                status=VisitStatus.COMPLETED,
            )

        with CaptureQueriesContext(connection) as ctx:
            stats = _compute_stats_from_db(agency.id)
            queries = ctx.captured_queries

        # Should be exactly 1 query (aggregate), not 4 (count × 4)
        self.assertEqual(len(queries), 1)
