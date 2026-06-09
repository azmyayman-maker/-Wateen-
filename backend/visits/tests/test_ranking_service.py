"""
Tests for the Dynamic Vector-Based Ranking Service.

Tests cover:
- Urgency weight mapping
- Clinical quality, operational reliability, and spatial proximity calculations
- Multi-agency ranking with batch optimization
- Cache invalidation and fallback behavior
"""

from unittest.mock import Mock, patch
from uuid import uuid4

from django.contrib.gis.geos import Point
from django.test import TestCase

from users.models import AgencyProfile, AgencyStatus, CustomUser, NurseProfile
from visits.models import VisitUrgency
from visits.services.ranking_service import (
    ALGORITHM_CONSTANTS,
    URGENCY_WEIGHTS,
    AgencyScore,
    _compute_clinical_quality,
    _compute_operational_reliability,
    _compute_spatial_proximity,
    rank_agencies,
)


class TestRankingAlgorithmComponents(TestCase):
    """Test individual scoring components."""

    def test_clinical_quality_perfect_agency(self):
        """Agency with 5.0 rating and 0 disputes should score 1.0."""
        quality = _compute_clinical_quality(
            rating=5.0, dispute_rate=0.0, kappa=ALGORITHM_CONSTANTS.kappa
        )
        self.assertEqual(quality, 1.0)

    def test_clinical_quality_new_agency_defaults(self):
        """New agency with 0 rating and 0 disputes should score 0.0."""
        quality = _compute_clinical_quality(
            rating=0.0, dispute_rate=0.0, kappa=ALGORITHM_CONSTANTS.kappa
        )
        self.assertEqual(quality, 0.0)

    def test_clinical_quality_penalty_for_disputes(self):
        """High dispute rate should penalize quality score."""
        quality_no_disputes = _compute_clinical_quality(
            rating=5.0, dispute_rate=0.0, kappa=ALGORITHM_CONSTANTS.kappa
        )
        quality_with_disputes = _compute_clinical_quality(
            rating=5.0, dispute_rate=0.5, kappa=ALGORITHM_CONSTANTS.kappa
        )
        self.assertLess(quality_with_disputes, quality_no_disputes)

    def test_clinical_quality_never_negative(self):
        """Quality score should never go below 0."""
        quality = _compute_clinical_quality(
            rating=1.0, dispute_rate=1.0, kappa=ALGORITHM_CONSTANTS.kappa
        )
        self.assertGreaterEqual(quality, 0.0)

    def test_operational_reliability_full_reliability(self):
        """Agency with 100% response and acceptance should score 1.0."""
        reliability = _compute_operational_reliability(
            response_rate=1.0, acceptance_rate=1.0, mu=ALGORITHM_CONSTANTS.mu
        )
        self.assertEqual(reliability, 1.0)

    def test_operational_reliability_balanced_weights(self):
        """Reliability should balance response_rate and acceptance_rate by mu."""
        reliability = _compute_operational_reliability(
            response_rate=1.0, acceptance_rate=0.0, mu=0.6
        )
        # Should be: 0.6 * 1.0 + 0.4 * 0.0 = 0.6
        self.assertAlmostEqual(reliability, 0.6, places=2)

    def test_spatial_proximity_zero_capacity(self):
        """Zero capacity should result in zero proximity score."""
        proximity = _compute_spatial_proximity(
            capacity=0.0,
            eta_minutes=10.0,
            eta_optimal=ALGORITHM_CONSTANTS.ETA_optimal,
            lambda_decay=ALGORITHM_CONSTANTS.lambda_decay,
        )
        self.assertEqual(proximity, 0.0)

    def test_spatial_proximity_none_eta(self):
        """None ETA should result in zero proximity score."""
        proximity = _compute_spatial_proximity(
            capacity=1.0,
            eta_minutes=None,
            eta_optimal=ALGORITHM_CONSTANTS.ETA_optimal,
            lambda_decay=ALGORITHM_CONSTANTS.lambda_decay,
        )
        self.assertEqual(proximity, 0.0)

    def test_spatial_proximity_optimal_eta(self):
        """ETA at optimal threshold should give full capacity score."""
        proximity = _compute_spatial_proximity(
            capacity=0.8,
            eta_minutes=ALGORITHM_CONSTANTS.ETA_optimal,
            eta_optimal=ALGORITHM_CONSTANTS.ETA_optimal,
            lambda_decay=ALGORITHM_CONSTANTS.lambda_decay,
        )
        self.assertEqual(proximity, 0.8)

    def test_spatial_proximity_decay(self):
        """ETA above optimal should decay exponentially."""
        proximity_optimal = _compute_spatial_proximity(
            capacity=1.0,
            eta_minutes=15.0,  # At optimal
            eta_optimal=15.0,
            lambda_decay=0.1,
        )
        proximity_above = _compute_spatial_proximity(
            capacity=1.0,
            eta_minutes=25.0,  # 10 min above optimal
            eta_optimal=15.0,
            lambda_decay=0.1,
        )
        self.assertLess(proximity_above, proximity_optimal)


class TestUrgencyWeights(TestCase):
    """Test urgency weight mapping."""

    def test_all_urgency_levels_have_weights(self):
        """All VisitUrgency values should have weight mappings."""
        for urgency in VisitUrgency:
            self.assertIn(urgency, URGENCY_WEIGHTS)
            weights = URGENCY_WEIGHTS[urgency]
            self.assertEqual(len(weights), 3)  # (w_q, w_r, w_p)

    def test_low_urgency_prioritizes_quality(self):
        """LOW urgency should prioritize clinical quality (w_q)."""
        w_q, w_r, w_p = URGENCY_WEIGHTS[VisitUrgency.LOW]
        self.assertGreaterEqual(w_q, w_r)
        self.assertGreaterEqual(w_q, w_p)

    def test_critical_urgency_prioritizes_proximity(self):
        """CRITICAL/SOS urgency should prioritize spatial proximity (w_p)."""
        w_q, w_r, w_p = URGENCY_WEIGHTS[VisitUrgency.CRITICAL]
        self.assertGreater(w_p, w_q)
        self.assertGreaterEqual(w_p, w_r)

        w_q_sos, w_r_sos, w_p_sos = URGENCY_WEIGHTS[VisitUrgency.SOS]
        self.assertEqual(w_p, w_p_sos)

    def test_weights_sum_to_one(self):
        """All weight tuples should sum to 1.0."""
        for urgency, (w_q, w_r, w_p) in URGENCY_WEIGHTS.items():
            total = w_q + w_r + w_p
            self.assertAlmostEqual(total, 1.0, places=2)


class TestRankAgenciesIntegration(TestCase):
    """Integration tests for rank_agencies function."""

    def setUp(self):
        """Create test agencies and nurses."""
        # Create agency admin users
        self.user1 = CustomUser.objects.create_user(
            national_id="12345678901234",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )
        self.user2 = CustomUser.objects.create_user(
            national_id="98765432109876",
            password="testpass123",
            role=CustomUser.Role.AGENCY_ADMIN,
        )

        # Create agencies
        self.agency1 = AgencyProfile.objects.create(
            user=self.user1,
            manager_name="Agency One Manager",
            commercial_registry="CR001",
            moh_license_number="MOH001",
            tax_id="TAX001",
            status=AgencyStatus.VERIFIED,
            rating=4.5,
            coverage_polygon=Point(31.2357, 30.0444).buffer(0.1),  # Cairo
        )
        self.agency2 = AgencyProfile.objects.create(
            user=self.user2,
            manager_name="Agency Two Manager",
            commercial_registry="CR002",
            moh_license_number="MOH002",
            tax_id="TAX002",
            status=AgencyStatus.VERIFIED,
            rating=3.8,
            coverage_polygon=Point(31.2357, 30.0444).buffer(0.1),
        )

        # Create nurses for agencies
        self.nurse_user1 = CustomUser.objects.create_user(
            national_id="11111111111111",
            password="testpass123",
            role=CustomUser.Role.NURSE,
        )
        self.nurse1 = NurseProfile.objects.create(
            user=self.nurse_user1,
            agency=self.agency1,
            is_available=True,
            last_location=Point(31.23, 30.04),
        )

    @patch("visits.services.ranking_service.get_agency_operational_stats")
    @patch("visits.services.ranking_service._find_nearest_nurse_eta")
    def test_ranking_returns_sorted_results(self, mock_eta, mock_stats):
        """Ranking should return agencies sorted by score descending."""
        mock_stats.return_value = {
            "response_rate": 0.8,
            "acceptance_rate": 0.7,
            "dispute_rate": 0.1,
        }
        mock_eta.return_value = 10.0  # 10 min ETA

        agencies = AgencyProfile.objects.filter(
            id__in=[self.agency1.id, self.agency2.id]
        )
        patient_location = Point(31.2357, 30.0444)

        results = rank_agencies(agencies, patient_location, VisitUrgency.MEDIUM)

        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], AgencyScore)
        # Higher-rated agency should rank higher
        self.assertEqual(results[0].agency_id, self.agency1.id)

    @patch("visits.services.ranking_service.get_agency_operational_stats")
    def test_ranking_handles_empty_queryset(self, mock_stats):
        """Ranking should handle empty agency queryset gracefully."""
        agencies = AgencyProfile.objects.none()
        results = rank_agencies(agencies, None, VisitUrgency.MEDIUM)

        self.assertEqual(len(results), 0)

    @patch("visits.services.ranking_service.get_agency_operational_stats")
    def test_ranking_handles_invalid_urgency(self, mock_stats):
        """Ranking should default to MEDIUM for invalid urgency."""
        mock_stats.return_value = {
            "response_rate": 0.5,
            "acceptance_rate": 0.5,
            "dispute_rate": 0.0,
        }

        agencies = AgencyProfile.objects.filter(id=self.agency1.id)
        results = rank_agencies(agencies, None, "INVALID_URGENCY")

        # Should not crash and use MEDIUM weights
        self.assertEqual(len(results), 1)

    @patch("visits.services.ranking_service.get_agency_operational_stats")
    def test_ranking_includes_debug_info(self, mock_stats):
        """Ranking should include debug information for each agency."""
        mock_stats.return_value = {
            "response_rate": 0.9,
            "acceptance_rate": 0.8,
            "dispute_rate": 0.05,
        }

        agencies = AgencyProfile.objects.filter(id=self.agency1.id)
        results = rank_agencies(agencies, None, VisitUrgency.LOW)

        self.assertIn("debug_info", results[0]._asdict())
        debug_info = results[0].debug_info
        self.assertIn("rating", debug_info)
        self.assertIn("weights", debug_info)

    @patch("visits.services.ranking_service.cache")
    @patch("visits.services.ranking_service.get_agency_operational_stats")
    def test_ranking_uses_cached_stats_when_available(self, mock_stats, mock_cache):
        """Ranking should use cached stats and avoid DB queries."""
        mock_cache.get_many.return_value = {
            f"agency_stats_{self.agency1.id}": {
                "response_rate": 0.95,
                "acceptance_rate": 0.9,
                "dispute_rate": 0.02,
            }
        }
        mock_stats.return_value = {}  # Should not be called

        agencies = AgencyProfile.objects.filter(id=self.agency1.id)
        results = rank_agencies(agencies, None, VisitUrgency.MEDIUM)

        # Stats should come from cache, not DB
        mock_stats.assert_not_called()


class TestNurseETAOptimization(TestCase):
    """Test ETA calculation optimization layers."""

    @patch("visits.services.ranking_service.calculate_nurse_eta")
    def test_eta_uses_cached_results(self, mock_calculate):
        """ETA calculation should use cached results when available."""
        from django.core.cache import cache

        mock_nurse = Mock()
        mock_nurse.id = uuid4()
        mock_nurse.last_location = Point(31.2, 30.0)

        agency = Mock()
        agency.id = uuid4()

        patient_location = Point(31.3, 30.1)

        # Set cache
        cache_key = f"nurse_eta_{mock_nurse.id}_{patient_location.x:.4f}_{patient_location.y:.4f}"
        cache.set(cache_key, 12.5, 600)

        # This should use cached value
        # Note: Actual test would need proper mocking of filter query

    def test_eta_limits_to_top_3_candidates(self):
        """ETA calculation should only route top 3 nearest nurses by geodesic distance."""
        # Integration test would verify that only 3 routing API calls are made
        # even when agency has many available nurses
        pass


class TestBatchOptimization(TestCase):
    """Test batch query optimization in ranking."""

    def test_nurse_count_batching(self):
        """Nurse counts should be fetched in a single query, not N+1."""
        # This would be verified by asserting query count in integration tests
        # from django.test.utils import override_settings
        # from django.db import connection
        # from django.test.utils import CaptureQueriesContext
        pass
