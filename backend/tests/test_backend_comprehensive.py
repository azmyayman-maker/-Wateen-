"""
Comprehensive Backend Test Suite — Based on TestSprite Plan
=============================================================
Covers: Authentication, Profile, Visit Management (TC001–TC010).
All assertions aligned with actual API contracts.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

# ---------------------------------------------------------------------------
# Valid Egyptian National IDs for testing
#   Format: [2|3][YY][MM][DD][GOV-2][SEQ-4][CHECK-1]
#   Governorate codes: 01,02,03,04,11-19,21-29,31-35
# ---------------------------------------------------------------------------
VALID_NID_1 = "29001011234567"  # century=2, 1990-01-01, gov=12
VALID_NID_2 = "29501021345678"  # century=2, 1995-01-02, gov=13
VALID_PHONE_1 = "01012345678"
VALID_PHONE_2 = "01112345678"
DEFAULT_PASSWORD = "Str0ng!Pass#99"


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def api_client():
    """Unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory to create a user with valid Egyptian national ID."""
    def _create(
        national_id=VALID_NID_1,
        phone=VALID_PHONE_1,
        password=DEFAULT_PASSWORD,
        role="PATIENT",
    ):
        return User.objects.create_user(
            national_id=national_id,
            phone_number=phone,
            password=password,
            role=role,
        )
    return _create


def _obtain_tokens(client, national_id=VALID_NID_1, password=DEFAULT_PASSWORD):
    """Helper: obtain JWT access + refresh tokens."""
    resp = client.post(
        reverse("users:token_obtain_pair"),
        {"national_id": national_id, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK, f"Login failed: {resp.data}"
    return resp.data["access"], resp.data["refresh"]


# ===========================================================================
# TC001–TC007 — Authentication & Profile
# ===========================================================================

@pytest.mark.django_db
class TestAuthFlows:
    """Tests aligned with the TestSprite backend test plan (TC001-TC007)."""

    # -----------------------------------------------------------------------
    # TC001 — Register with valid data
    # -----------------------------------------------------------------------
    def test_tc001_register_valid(self, api_client):
        url = reverse("users:register")
        data = {
            "national_id": VALID_NID_1,
            "phone_number": VALID_PHONE_1,
            "password": DEFAULT_PASSWORD,
            "password_confirm": DEFAULT_PASSWORD,
            "role": "PATIENT",
        }
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_201_CREATED
        # Response shape: {user: {...}, tokens: {access, refresh}}
        assert "user" in resp.data
        assert "tokens" in resp.data
        assert resp.data["user"]["role"] == "PATIENT"
        assert "access" in resp.data["tokens"]
        assert "refresh" in resp.data["tokens"]

    # -----------------------------------------------------------------------
    # TC001-extra — Register with missing fields
    # -----------------------------------------------------------------------
    def test_tc001_register_missing_fields(self, api_client):
        url = reverse("users:register")
        resp = api_client.post(url, {})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # -----------------------------------------------------------------------
    # TC001-extra — Register with mismatched passwords
    # -----------------------------------------------------------------------
    def test_tc001_register_password_mismatch(self, api_client):
        url = reverse("users:register")
        data = {
            "national_id": VALID_NID_1,
            "phone_number": VALID_PHONE_1,
            "password": DEFAULT_PASSWORD,
            "password_confirm": "DifferentPassword!1",
        }
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # -----------------------------------------------------------------------
    # TC001-extra — Register with invalid national ID
    # -----------------------------------------------------------------------
    def test_tc001_register_invalid_national_id(self, api_client):
        url = reverse("users:register")
        data = {
            "national_id": "12345",  # Too short / invalid
            "phone_number": VALID_PHONE_1,
            "password": DEFAULT_PASSWORD,
            "password_confirm": DEFAULT_PASSWORD,
        }
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # -----------------------------------------------------------------------
    # TC001-extra — Register duplicate national ID
    # -----------------------------------------------------------------------
    def test_tc001_register_duplicate_national_id(self, api_client, create_user):
        create_user()
        url = reverse("users:register")
        data = {
            "national_id": VALID_NID_1,
            "phone_number": VALID_PHONE_2,
            "password": DEFAULT_PASSWORD,
            "password_confirm": DEFAULT_PASSWORD,
        }
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # -----------------------------------------------------------------------
    # TC002 — Login valid credentials
    # -----------------------------------------------------------------------
    def test_tc002_login_valid(self, api_client, create_user):
        create_user()
        url = reverse("users:token_obtain_pair")
        resp = api_client.post(url, {
            "national_id": VALID_NID_1,
            "password": DEFAULT_PASSWORD,
        })
        assert resp.status_code == status.HTTP_200_OK
        assert "access" in resp.data
        assert "refresh" in resp.data

    # -----------------------------------------------------------------------
    # TC003 — Login invalid credentials
    # -----------------------------------------------------------------------
    def test_tc003_login_invalid(self, api_client, create_user):
        create_user()
        url = reverse("users:token_obtain_pair")
        resp = api_client.post(url, {
            "national_id": VALID_NID_1,
            "password": "WrongPassword!1",
        })
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    # -----------------------------------------------------------------------
    # TC004 — Token refresh
    # -----------------------------------------------------------------------
    def test_tc004_token_refresh(self, api_client, create_user):
        create_user()
        _, refresh = _obtain_tokens(api_client)
        url = reverse("users:token_refresh")
        resp = api_client.post(url, {"refresh": refresh})
        assert resp.status_code == status.HTTP_200_OK
        assert "access" in resp.data

    # -----------------------------------------------------------------------
    # TC004-extra — Token refresh with invalid token
    # -----------------------------------------------------------------------
    def test_tc004_token_refresh_invalid(self, api_client):
        url = reverse("users:token_refresh")
        resp = api_client.post(url, {"refresh": "invalid-token"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    # -----------------------------------------------------------------------
    # TC005 — Change password
    # -----------------------------------------------------------------------
    def test_tc005_change_password(self, api_client, create_user):
        user = create_user()
        new_pw = "NewStr0ng!Pass#77"
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("users:change_password")
        resp = client.post(url, {
            "old_password": DEFAULT_PASSWORD,
            "new_password": new_pw,
            "new_password_confirm": new_pw,
        })
        assert resp.status_code == status.HTTP_200_OK

        # Verify old password is rejected
        client.logout()
        login_url = reverse("users:token_obtain_pair")
        resp_old = client.post(login_url, {
            "national_id": VALID_NID_1,
            "password": DEFAULT_PASSWORD,
        })
        assert resp_old.status_code == status.HTTP_401_UNAUTHORIZED

        # Verify new password works
        resp_new = client.post(login_url, {
            "national_id": VALID_NID_1,
            "password": new_pw,
        })
        assert resp_new.status_code == status.HTTP_200_OK

    # -----------------------------------------------------------------------
    # TC005-extra — Change password with wrong old password
    # -----------------------------------------------------------------------
    def test_tc005_change_password_wrong_old(self, api_client, create_user):
        user = create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("users:change_password")
        resp = client.post(url, {
            "old_password": "WrongOld!1",
            "new_password": "NewStr0ng!Pass#77",
            "new_password_confirm": "NewStr0ng!Pass#77",
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # -----------------------------------------------------------------------
    # TC006 — Logout
    # -----------------------------------------------------------------------
    def test_tc006_logout(self, api_client, create_user):
        create_user()
        access, refresh = _obtain_tokens(api_client)
        url = reverse("users:logout")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = api_client.post(url, {"refresh": refresh})
        assert resp.status_code == status.HTTP_200_OK

    # -----------------------------------------------------------------------
    # TC006-extra — Logout without auth
    # -----------------------------------------------------------------------
    def test_tc006_logout_no_auth(self, api_client):
        url = reverse("users:logout")
        resp = api_client.post(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    # -----------------------------------------------------------------------
    # TC007 — Get profile
    # -----------------------------------------------------------------------
    def test_tc007_get_profile(self, api_client, create_user):
        user = create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("users:profile")
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["national_id"] == VALID_NID_1
        assert resp.data["role"] == "PATIENT"

    # -----------------------------------------------------------------------
    # TC007-extra — Get profile without auth
    # -----------------------------------------------------------------------
    def test_tc007_get_profile_no_auth(self, api_client):
        url = reverse("users:profile")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ===========================================================================
# TC008–TC010 — Visit Management
# ===========================================================================

@pytest.mark.django_db
@pytest.mark.gis
class TestVisitFlows:
    """Tests for the visit request API (TC008-TC010)."""

    # -----------------------------------------------------------------------
    # TC008 — Valid visit request
    # -----------------------------------------------------------------------
    def test_tc008_visit_request_valid(self, api_client, create_user):
        user = create_user(role="PATIENT")
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("visits:visit_request")
        data = {
            "latitude": 30.0444,
            "longitude": 31.2357,
            "service_type": "WOUND_CARE",
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert "id" in resp.data
        assert resp.data["status"] == "PENDING"

    # -----------------------------------------------------------------------
    # TC009 — Visit request without auth
    # -----------------------------------------------------------------------
    def test_tc009_visit_request_no_auth(self, api_client):
        url = reverse("visits:visit_request")
        data = {"latitude": 30.0444, "longitude": 31.2357}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    # -----------------------------------------------------------------------
    # TC010 — Visit request with invalid coordinates
    # -----------------------------------------------------------------------
    def test_tc010_visit_request_invalid_lat(self, api_client, create_user):
        user = create_user(role="PATIENT")
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("visits:visit_request")
        data = {
            "latitude": 95.0000,   # > 90 → invalid
            "longitude": 31.2357,
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # -----------------------------------------------------------------------
    # TC010-extra — Visit request by non-patient role
    # -----------------------------------------------------------------------
    def test_tc010_visit_request_by_nurse(self, api_client, create_user):
        user = create_user(
            national_id=VALID_NID_2,
            phone=VALID_PHONE_2,
            role="NURSE",
        )
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("visits:visit_request")
        data = {"latitude": 30.0444, "longitude": 31.2357}
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# ===========================================================================
# Model-level tests — Visit state machine
# ===========================================================================

@pytest.mark.django_db
@pytest.mark.gis
class TestVisitStateMachine:
    """Tests for the Visit.transition_to() state machine."""

    def _create_visit(self, create_user):
        from django.contrib.gis.geos import Point

        from visits.models import Visit
        user = create_user()
        profile = user.patient_profile
        return Visit.objects.create(
            patient=profile,
            location=Point(31.2357, 30.0444, srid=4326),
            service_type="CHECK_UP",
        )

    def test_valid_transition_pending_to_matched(self, create_user):
        visit = self._create_visit(create_user)
        assert visit.status == "PENDING"
        visit.transition_to("MATCHED")
        visit.refresh_from_db()
        assert visit.status == "MATCHED"

    def test_valid_full_lifecycle(self, create_user):
        visit = self._create_visit(create_user)
        for next_status in ["MATCHED", "ACCEPTED", "ON_WAY", "ARRIVED", "IN_PROGRESS", "COMPLETED"]:
            visit.transition_to(next_status)
        visit.refresh_from_db()
        assert visit.status == "COMPLETED"

    def test_invalid_transition_pending_to_completed(self, create_user):
        from django.core.exceptions import ValidationError
        visit = self._create_visit(create_user)
        with pytest.raises(ValidationError):
            visit.transition_to("COMPLETED")

    def test_cancel_from_any_active_state(self, create_user):
        visit = self._create_visit(create_user)
        visit.transition_to("MATCHED")
        visit.transition_to("CANCELLED")
        visit.refresh_from_db()
        assert visit.status == "CANCELLED"

    def test_cannot_transition_from_terminal(self, create_user):
        from django.core.exceptions import ValidationError
        visit = self._create_visit(create_user)
        visit.transition_to("CANCELLED")
        with pytest.raises(ValidationError):
            visit.transition_to("PENDING")
