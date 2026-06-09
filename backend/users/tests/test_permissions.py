from unittest.mock import Mock

import pytest

from users.models import AgencyStatus, UserRole
from users.permissions import (
    IsAgencyAdmin,
    IsNurseOrAbove,
    IsOwnerOrAdmin,
    IsSuperAdmin,
)


class TestPermissionClasses:
    """
    Unit tests for custom DRF permission classes guarding B2B2C API endpoints.
    """

    @pytest.fixture
    def mock_request(self):
        return Mock()

    @pytest.fixture
    def mock_view(self):
        return Mock()

    def test_is_superadmin_permission(self, mock_request, mock_view):
        perm = IsSuperAdmin()

        # User is superadmin
        mock_request.user.role = UserRole.SUPERADMIN
        mock_request.user.is_authenticated = True
        mock_request.user.is_superadmin = True
        assert perm.has_permission(mock_request, mock_view) is True

        # User is patient (not superadmin)
        mock_request.user.role = UserRole.PATIENT
        mock_request.user.is_authenticated = True
        mock_request.user.is_superadmin = False
        assert perm.has_permission(mock_request, mock_view) is False

    def test_is_agency_admin_permission(self, mock_request, mock_view):
        perm = IsAgencyAdmin()

        # Verified agency admin
        mock_request.user.role = UserRole.AGENCY_ADMIN
        mock_request.user.is_authenticated = True
        mock_request.user.is_agency_admin = True
        mock_request.user.agency = Mock(status=AgencyStatus.VERIFIED)
        assert perm.has_permission(mock_request, mock_view) is True

        # Unverified agency admin
        mock_request.user.is_authenticated = True
        mock_request.user.is_agency_admin = True
        mock_request.user.agency = Mock(status=AgencyStatus.PENDING)
        assert perm.has_permission(mock_request, mock_view) is False

        # Nurse role (no agency admin)
        mock_request.user.role = UserRole.NURSE
        mock_request.user.is_authenticated = True
        mock_request.user.is_agency_admin = False
        assert perm.has_permission(mock_request, mock_view) is False

    def test_is_nurse_or_above_permission(self, mock_request, mock_view):
        perm = IsNurseOrAbove()

        # Nurse
        mock_request.user.role = UserRole.NURSE
        mock_request.user.is_authenticated = True
        mock_request.user.is_nurse = True
        mock_request.user.is_agency_admin = False
        mock_request.user.is_superadmin = False
        assert perm.has_permission(mock_request, mock_view) is True

        # Superadmin
        mock_request.user.role = UserRole.SUPERADMIN
        mock_request.user.is_authenticated = True
        mock_request.user.is_nurse = False
        mock_request.user.is_agency_admin = False
        mock_request.user.is_superadmin = True
        assert perm.has_permission(mock_request, mock_view) is True

        # Patient
        mock_request.user.role = UserRole.PATIENT
        mock_request.user.is_authenticated = True
        mock_request.user.is_nurse = False
        mock_request.user.is_agency_admin = False
        mock_request.user.is_superadmin = False
        assert perm.has_permission(mock_request, mock_view) is False

    def test_is_owner_or_admin_permission(self, mock_request, mock_view):
        perm = IsOwnerOrAdmin()
        # Restrict the mock spec so hasattr works correctly for specific attributes
        mock_obj = Mock(spec=['user'])

        # Owner
        mock_obj.user = mock_request.user
        mock_request.user.is_authenticated = True
        mock_request.user.is_superadmin = False
        mock_request.user.is_agency_admin = False
        assert perm.has_object_permission(mock_request, mock_view, mock_obj) is True

        # Not owner, but superadmin
        mock_obj.user = Mock()  # Different user
        mock_request.user.is_authenticated = True
        mock_request.user.is_superadmin = True
        assert perm.has_object_permission(mock_request, mock_view, mock_obj) is True

        # Not owner, not superadmin
        mock_request.user.is_authenticated = True
        mock_request.user.is_superadmin = False
        assert perm.has_object_permission(mock_request, mock_view, mock_obj) is False
