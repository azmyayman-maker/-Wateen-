import uuid
from datetime import timedelta
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser, AgencyProfile, NurseInvitation, NurseProfile, UserRole, InvitationStatus
from visits.tests.conftest import AgencyProfileFactory

@pytest.fixture
def agency_admin_user(db):
    user = CustomUser.objects.create_user(
        national_id="29001010112345",
        phone_number="01011111111",
        password="Password123!",
        role=UserRole.AGENCY_ADMIN
    )
    agency = AgencyProfileFactory(
        manager_name="Manager 1",
        status="verified"
    )
    user.agency = agency
    user.save()
    return user

@pytest.fixture
def agency_admin_user_2(db):
    user = CustomUser.objects.create_user(
        national_id="29002020212345",
        phone_number="01022222222",
        password="Password123!",
        role=UserRole.AGENCY_ADMIN
    )
    agency = AgencyProfileFactory(
        manager_name="Manager 2",
        status="verified"
    )
    user.agency = agency
    user.save()
    return user

@pytest.fixture
def unverified_agency_admin(db):
    user = CustomUser.objects.create_user(
        national_id="29003030312345",
        phone_number="01033333333",
        password="Password123!",
        role=UserRole.AGENCY_ADMIN
    )
    agency = AgencyProfileFactory(
        manager_name="Manager 3",
        status="pending"
    )
    user.agency = agency
    user.save()
    return user

@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestNurseInvitationFlow:

    def test_invite_nurse_success(self, api_client, agency_admin_user):
        """Test that a verified AGENCY_ADMIN can invite a nurse."""
        api_client.force_authenticate(user=agency_admin_user)
        url = reverse("users:invite_nurse")
        data = {"phone": "01099999999"}
        response = api_client.post(url, data, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert NurseInvitation.objects.count() == 1
        invitation = NurseInvitation.objects.first()
        assert invitation.agency == agency_admin_user.agency
        assert invitation.phone == data["phone"]
        assert invitation.status == InvitationStatus.PENDING

    def test_invite_nurse_unverified_agency(self, api_client, unverified_agency_admin):
        """Test that an unverified AGENCY_ADMIN cannot invite a nurse."""
        api_client.force_authenticate(user=unverified_agency_admin)
        url = reverse("users:invite_nurse")
        data = {"phone": "01099999999"}
        response = api_client.post(url, data, secure=True)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invite_nurse_patient_user(self, api_client, db):
        """Test that a PATIENT cannot invite a nurse."""
        patient = CustomUser.objects.create_user(
            national_id="29004040412345",
            phone_number="01044444444",
            password="Password123!",
            role=UserRole.PATIENT
        )
        api_client.force_authenticate(user=patient)
        url = reverse("users:invite_nurse")
        data = {"phone": "01099999999"}
        response = api_client.post(url, data, secure=True)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invite_nurse_nurse_user(self, api_client, agency_admin_user):
        """Test that a NURSE cannot invite a nurse."""
        nurse_user = CustomUser.objects.create_user(
            national_id="29007071212345",
            phone_number="01077777777",
            password="Password123!",
            role=UserRole.NURSE
        )
        NurseProfile.objects.create(
            user=nurse_user,
            agency=agency_admin_user.agency,
            syndicate_number="SYN-999"
        )
        api_client.force_authenticate(user=nurse_user)
        url = reverse("users:invite_nurse")
        data = {"phone": "01099999999"}
        response = api_client.post(url, data, secure=True)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestNurseAcceptanceFlow:
    
    @pytest.fixture
    def valid_invitation(self, agency_admin_user):
        return NurseInvitation.objects.create(
            agency=agency_admin_user.agency,
            phone="01099999999",
            expires_at=timezone.now() + timedelta(hours=72)
        )

    def test_accept_invitation_success(self, api_client, valid_invitation):
        url = reverse("users:accept_invitation")
        data = {
            "token": str(valid_invitation.token),
            "password": "StrongPassword123!",
            "phone": "01099999999",
            "email": "nurse@example.com",
            "national_id": "29001011234567",
            "syndicate_number": "SYN-12345",
            "full_name": "Fatima Ahmed"
        }
        response = api_client.post(url, data, secure=True)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify db changes
        valid_invitation.refresh_from_db()
        assert valid_invitation.status == InvitationStatus.ACCEPTED
        user = CustomUser.objects.get(national_id=data["national_id"])
        assert user.role == UserRole.NURSE
        profile = NurseProfile.objects.get(user=user)
        assert profile.agency == valid_invitation.agency
        assert user.first_name_ar == "Fatima"
        assert user.last_name_ar == "Ahmed"

    def test_accept_invitation_expired(self, api_client, valid_invitation):
        valid_invitation.expires_at = timezone.now() - timedelta(hours=1)
        valid_invitation.save()

        url = reverse("users:accept_invitation")
        data = {
            "token": str(valid_invitation.token),
            "password": "StrongPassword123!",
            "phone": "01099999999",
            "email": "nurse@example.com",
            "national_id": "29001011234567",
            "syndicate_number": "SYN-12345",
            "full_name": "Fatima Ahmed"
        }
        response = api_client.post(url, data, secure=True)
        assert response.status_code == status.HTTP_410_GONE
        assert "expired" in response.data["detail"].lower()
        
        valid_invitation.refresh_from_db()
        assert valid_invitation.status == InvitationStatus.EXPIRED

    def test_accept_invitation_duplicate_national_id_atomic_rollback(self, api_client, valid_invitation):
        """
        To test atomic rollback, we will attempt to create a nurse with an already existing national_id.
        The user creation might succeed (if we caught the DB error for user), or fail.
        If NurseProfile creation fails, the User should not exist.
        """
        # Create user with same national_id to force IntegrityError during User creation
        CustomUser.objects.create_user(
            national_id="29001011234567",
            phone_number="01088888888",
            password="StrongPassword123!",
            role=UserRole.PATIENT
        )

        url = reverse("users:accept_invitation")
        data = {
            "token": str(valid_invitation.token),
            "password": "StrongPassword123!",
            "phone": "01099999999",
            "email": "another@example.com",
            "national_id": "29001011234567", # Same national_id
            "syndicate_number": "SYN-12345",
            "full_name": "Fatima Ahmed"
        }
        
        users_count_before = CustomUser.objects.count()
        response = api_client.post(url, data, secure=True)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Transaction should have rolled back, no new users or profiles created
        assert CustomUser.objects.count() == users_count_before
        assert NurseProfile.objects.count() == 0
        
        valid_invitation.refresh_from_db()
        assert valid_invitation.status == InvitationStatus.PENDING # Token still valid since it failed

    def test_accept_invitation_invalid_token(self, api_client):
        url = reverse("users:accept_invitation")
        data = {
            "token": str(uuid.uuid4()),
            "password": "StrongPassword123!",
            "phone": "01099999999",
            "email": "nurse@example.com",
            "national_id": "29001011234567",
            "syndicate_number": "SYN-12345",
            "full_name": "Fatima Ahmed"
        }
        response = api_client.post(url, data, secure=True)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Invalid or already consumed" in response.data["detail"]
