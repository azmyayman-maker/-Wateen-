"""
Wateen Zero-Trace Seeding — Integrity Tests
=============================================
Validates the seed/nuke lifecycle:
  1. Seeder creates expected entities with correct counts
  2. Visit locations are spatially contained within agency polygons
  3. Nuke removes ALL test data with zero residual
  4. Nuke does NOT touch non-test (production) data

These tests require a PostGIS-enabled database (Docker environment).
"""

from io import StringIO

import pytest
from django.core.management import call_command

from users.models import (
    AgencyProfile,
    CustomUser,
    NurseProfile,
    UserRole,
)
from users.utils.seed_helpers import TEST_EMAIL_DOMAIN
from visits.models import Transaction, Visit

# ─────────────────────────────────────────────────────────────────────────────
# Test Configuration
# ─────────────────────────────────────────────────────────────────────────────
SEED_AGENCIES = 2
SEED_NURSES_PER_AGENCY = 3
SEED_VISITS_PER_NURSE = 5


@pytest.fixture
def seed_test_data(db):
    """Run the seeder with a small batch and return stdout output."""
    out = StringIO()
    call_command(
        "seed_wateen_data",
        agencies=SEED_AGENCIES,
        nurses_per_agency=SEED_NURSES_PER_AGENCY,
        visits_per_nurse=SEED_VISITS_PER_NURSE,
        batch_size=100,
        stdout=out,
    )
    return out.getvalue()


@pytest.fixture
def real_user(db):
    """Create a non-test 'production' user that must survive the nuke."""
    return CustomUser.objects.create_user(
        national_id="29901011234567",
        phone_number="01012345678",
        email="real-user@wateen.health",
        role=UserRole.PATIENT,
        first_name_ar="مستخدم",
        last_name_ar="حقيقي",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Seeder creates expected entity counts
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.django_db(transaction=True)
@pytest.mark.gis
class TestSeedCreation:
    """Verify the seeder generates the correct number of entities."""

    def test_seed_creates_agencies(self, seed_test_data):
        count = AgencyProfile.objects.filter(
            commercial_registry__startswith="TEST-CR-"
        ).count()
        assert count == SEED_AGENCIES, f"Expected {SEED_AGENCIES} agencies, got {count}"

    def test_seed_creates_nurse_users(self, seed_test_data):
        expected = SEED_AGENCIES * SEED_NURSES_PER_AGENCY
        count = CustomUser.objects.filter(
            email__endswith=f"@{TEST_EMAIL_DOMAIN}",
            role=UserRole.NURSE,
        ).count()
        assert count == expected, f"Expected {expected} nurse users, got {count}"

    def test_seed_creates_nurse_profiles(self, seed_test_data):
        expected = SEED_AGENCIES * SEED_NURSES_PER_AGENCY
        count = NurseProfile.objects.filter(
            agency__commercial_registry__startswith="TEST-CR-"
        ).count()
        assert count == expected, f"Expected {expected} nurse profiles, got {count}"

    def test_seed_creates_patient_users(self, seed_test_data):
        expected = SEED_AGENCIES * SEED_NURSES_PER_AGENCY
        count = CustomUser.objects.filter(
            email__endswith=f"@{TEST_EMAIL_DOMAIN}",
            role=UserRole.PATIENT,
        ).count()
        assert count == expected, f"Expected {expected} patient users, got {count}"

    def test_seed_creates_visits(self, seed_test_data):
        expected = SEED_AGENCIES * SEED_NURSES_PER_AGENCY * SEED_VISITS_PER_NURSE
        count = Visit.objects.filter(
            agency__commercial_registry__startswith="TEST-CR-"
        ).count()
        assert count == expected, f"Expected {expected} visits, got {count}"

    def test_seed_creates_admin_users(self, seed_test_data):
        count = CustomUser.objects.filter(
            email__endswith=f"@{TEST_EMAIL_DOMAIN}",
            role=UserRole.AGENCY_ADMIN,
        ).count()
        assert count == SEED_AGENCIES, f"Expected {SEED_AGENCIES} admin users, got {count}"

    def test_agencies_have_coverage_polygons(self, seed_test_data):
        agencies = AgencyProfile.objects.filter(
            commercial_registry__startswith="TEST-CR-"
        )
        for agency in agencies:
            assert agency.coverage_polygon is not None, (
                f"Agency {agency.manager_name} has no coverage polygon"
            )
            assert agency.coverage_polygon.valid, (
                f"Agency {agency.manager_name} has invalid polygon"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Spatial integrity — Visit locations inside agency polygons
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.django_db(transaction=True)
@pytest.mark.gis
class TestSpatialIntegrity:
    """Verify all visit locations fall within their agency's coverage polygon."""

    def test_visit_locations_inside_agency_polygons(self, seed_test_data):
        agencies = AgencyProfile.objects.filter(
            commercial_registry__startswith="TEST-CR-"
        ).exclude(coverage_polygon__isnull=True)

        violations = 0
        total_checked = 0

        for agency in agencies:
            visits = Visit.objects.filter(agency=agency).select_related("agency")
            for visit in visits:
                total_checked += 1
                if not agency.coverage_polygon.contains(visit.location):
                    violations += 1

        assert total_checked > 0, "No visits found to check"
        assert violations == 0, (
            f"{violations}/{total_checked} visits are outside their "
            f"agency's coverage polygon"
        )

    def test_nurse_locations_inside_agency_polygons(self, seed_test_data):
        agencies = AgencyProfile.objects.filter(
            commercial_registry__startswith="TEST-CR-"
        ).exclude(coverage_polygon__isnull=True)

        for agency in agencies:
            nurses = NurseProfile.objects.filter(
                agency=agency
            ).exclude(last_location__isnull=True)
            for nurse in nurses:
                assert agency.coverage_polygon.contains(nurse.last_location), (
                    f"Nurse {nurse} location is outside agency polygon"
                )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Nuke removes ALL test data
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.django_db(transaction=True)
@pytest.mark.gis
class TestNukeCleanup:
    """Verify the nuke command removes all test data completely."""

    def test_nuke_removes_all_test_data(self, seed_test_data):
        # Verify data exists before nuke
        assert CustomUser.objects.filter(
            email__endswith=f"@{TEST_EMAIL_DOMAIN}"
        ).count() > 0, "Seeder didn't create any test users"

        # Execute nuke
        out = StringIO()
        call_command(
            "nuke_test_data",
            force=True,
            no_vacuum=True,
            stdout=out,
        )

        # Verify zero-trace
        assert CustomUser.objects.filter(
            email__endswith=f"@{TEST_EMAIL_DOMAIN}"
        ).count() == 0, "Test users remain after nuke"

        assert AgencyProfile.objects.filter(
            commercial_registry__startswith="TEST-CR-"
        ).count() == 0, "Test agencies remain after nuke"

        assert NurseProfile.objects.filter(
            agency__commercial_registry__startswith="TEST-CR-"
        ).count() == 0, "Test nurse profiles remain after nuke"

        assert Visit.objects.filter(
            agency__commercial_registry__startswith="TEST-CR-"
        ).count() == 0, "Test visits remain after nuke"

        assert Transaction.objects.filter(
            agency__commercial_registry__startswith="TEST-CR-"
        ).count() == 0, "Test transactions remain after nuke"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Nuke does NOT touch production data
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.django_db(transaction=True)
@pytest.mark.gis
class TestNukeSafety:
    """Verify the nuke command does not affect non-test data."""

    def test_nuke_preserves_real_users(self, seed_test_data, real_user):
        real_user_id = real_user.id

        # Verify both test and real data exist
        assert CustomUser.objects.filter(
            email__endswith=f"@{TEST_EMAIL_DOMAIN}"
        ).count() > 0

        assert CustomUser.objects.filter(id=real_user_id).exists()

        # Execute nuke
        out = StringIO()
        call_command(
            "nuke_test_data",
            force=True,
            no_vacuum=True,
            stdout=out,
        )

        # Verify real user survived
        assert CustomUser.objects.filter(id=real_user_id).exists(), (
            "CRITICAL: Real user was deleted by nuke command!"
        )

        # Verify real user data is intact
        surviving_user = CustomUser.objects.get(id=real_user_id)
        assert surviving_user.email == "real-user@wateen.health"
        assert surviving_user.national_id == "29901011234567"
