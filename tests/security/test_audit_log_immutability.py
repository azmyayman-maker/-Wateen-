"""
Audit Log Immutability Tests.

Tests that KYCAuditLog entries are append-only — no modification or deletion possible.
"""

import pytest
from django.core.exceptions import PermissionDenied
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestAuditLogImmutability:
    """Test suite for audit log immutability enforcement."""

    # =====================================================================
    # T037-T042: API-level immutability (HTTP methods)
    # =====================================================================

    def test_superadmin_put_to_audit_log_returns_405(
        self, superadmin_client, agency_a
    ):
        """T037: SuperAdmin PUT to audit log endpoint → 405."""
        url = reverse("users:kyc-audit-logs", kwargs={"agency_id": agency_a.id})
        response = superadmin_client.put(url, {}, format="json")
        assert response.status_code == 405

    def test_superadmin_patch_to_audit_log_returns_405(
        self, superadmin_client, agency_a
    ):
        """T038: SuperAdmin PATCH to audit log endpoint → 405."""
        url = reverse("users:kyc-audit-logs", kwargs={"agency_id": agency_a.id})
        response = superadmin_client.patch(url, {}, format="json")
        assert response.status_code == 405

    def test_superadmin_delete_to_audit_log_returns_405(
        self, superadmin_client, agency_a
    ):
        """T039: SuperAdmin DELETE to audit log endpoint → 405."""
        url = reverse("users:kyc-audit-logs", kwargs={"agency_id": agency_a.id})
        response = superadmin_client.delete(url)
        assert response.status_code == 405

    def test_agency_admin_put_to_audit_log_returns_403(
        self, agency_a_client, agency_a
    ):
        """T040: Agency Admin PUT to audit log endpoint → 403."""
        url = reverse("users:kyc-audit-logs", kwargs={"agency_id": agency_a.id})
        response = agency_a_client.put(url, {}, format="json")
        assert response.status_code == 403

    def test_agency_admin_patch_to_audit_log_returns_403(
        self, agency_a_client, agency_a
    ):
        """T041: Agency Admin PATCH to audit log endpoint → 403."""
        url = reverse("users:kyc-audit-logs", kwargs={"agency_id": agency_a.id})
        response = agency_a_client.patch(url, {}, format="json")
        assert response.status_code == 403

    def test_agency_admin_delete_to_audit_log_returns_403(
        self, agency_a_client, agency_a
    ):
        """T042: Agency Admin DELETE to audit log endpoint → 403."""
        url = reverse("users:kyc-audit-logs", kwargs={"agency_id": agency_a.id})
        response = agency_a_client.delete(url)
        assert response.status_code == 403

    # =====================================================================
    # T043-T044: Model-level immutability
    # =====================================================================

    def test_model_level_save_on_existing_log_raises_permission_denied(
        self, superadmin_client, superadmin_user
    ):
        """T043: Model-level save() on existing log → PermissionDenied."""
        from users.models import KYCAuditLog, AgencyProfile, AgencyStatus
        
        # Create an audit log entry
        agency = AgencyProfile.objects.create(
            manager_name="Test Agency",
            commercial_registry="CR_TEST_001",
            moh_license_number="MOH_TEST_001",
            tax_id="TAX_TEST_001",
            status=AgencyStatus.VERIFIED,
        )
        
        reviewer = superadmin_user
        
        log_entry = KYCAuditLog.objects.create(
            agency=agency,
            reviewer=reviewer,
            action="APPROVE",
            notes="Test approval",
        )
        
        # Try to modify the existing log
        log_entry.notes = "Modified notes"
        
        with pytest.raises(PermissionDenied):
            log_entry.save()

    def test_model_level_delete_on_existing_log_raises_permission_denied(
        self, superadmin_client, superadmin_user
    ):
        """T044: Model-level delete() on existing log → PermissionDenied."""
        from users.models import KYCAuditLog, AgencyProfile, AgencyStatus
        
        # Create an audit log entry
        agency = AgencyProfile.objects.create(
            manager_name="Test Agency Del",
            commercial_registry="CR_DEL_001",
            moh_license_number="MOH_DEL_001",
            tax_id="TAX_DEL_001",
            status=AgencyStatus.VERIFIED,
        )
        
        reviewer = superadmin_user
        
        log_entry = KYCAuditLog.objects.create(
            agency=agency,
            reviewer=reviewer,
            action="APPROVE",
            notes="Test approval for delete",
        )
        
        # Try to delete the existing log
        with pytest.raises(PermissionDenied):
            log_entry.delete()

    # =====================================================================
    # Additional immutability tests
    # =====================================================================

    def test_new_audit_log_can_be_created(self, superadmin_client, superadmin_user):
        """Verify that creating new audit logs still works."""
        from users.models import KYCAuditLog, AgencyProfile, AgencyStatus
        
        agency = AgencyProfile.objects.create(
            manager_name="Test Agency New",
            commercial_registry="CR_NEW_001",
            moh_license_number="MOH_NEW_001",
            tax_id="TAX_NEW_001",
            status=AgencyStatus.PENDING,
        )
        
        reviewer = superadmin_user
        
        # Creating a new log should work
        log_entry = KYCAuditLog(
            agency=agency,
            reviewer=reviewer,
            action="APPROVE",
            notes="New approval",
        )
        
        # This should succeed (new record)
        log_entry.save()
        
        assert log_entry.pk is not None
        assert log_entry.id is not None
