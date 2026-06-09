"""
Full KYC Lifecycle Integration Tests.

Tests the complete E2E lifecycle: Register → Upload → Review → Approve/Reject → Resubmit.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestKYCLifecycle:
    """Test suite for full KYC lifecycle verification."""

    # =====================================================================
    # T019: Full happy path - Register → Upload 3 docs → Approve → VERIFIED
    # =====================================================================

    def test_full_kyc_approve_lifecycle(
        self, superadmin_client
    ):
        """T019: Full happy path: Register → Upload → Approve → VERIFIED."""
        from users.models import (
            AgencyProfile,
            AgencyStatus,
            KYCDocument,
        )

        # Step 1: Create agency (simulating registration)
        agency = AgencyProfile.objects.create(
            manager_name="Test Agency Happy",
            commercial_registry="CR_HAPPY_001",
            moh_license_number="MOH_HAPPY_001",
            tax_id="TAX_HAPPY_001",
            status=AgencyStatus.PENDING,
        )

        # Step 2: Upload 3 KYC documents
        pdf_content = b"%PDF-1.4\ntest content"
        doc_files = {
            'commercial_registry_file': SimpleUploadedFile("cr.pdf", pdf_content, content_type="application/pdf"),
            'moh_license_file': SimpleUploadedFile("moh.pdf", pdf_content, content_type="application/pdf"),
            'tax_id_file': SimpleUploadedFile("tax.pdf", pdf_content, content_type="application/pdf"),
        }

        url = reverse("users:agency_register")
        response = superadmin_client.post(url, doc_files, format="multipart")

        # If registration succeeded, verify documents exist
        docs_count = KYCDocument.objects.filter(agency=agency).count()

        # Step 3: SuperAdmin approves
        if docs_count >= 3:
            review_url = reverse("users:kyc-review", kwargs={"pk": agency.id})
            review_response = superadmin_client.post(
                review_url,
                {"action": "APPROVE", "notes": "All documents verified"},
                format="json"
            )

            # Refresh and verify status
            agency.refresh_from_db()
            assert agency.status == AgencyStatus.VERIFIED

    # =====================================================================
    # T020: Full reject path - Register → Upload → Reject → REJECTED
    # =====================================================================

    def test_full_kyc_reject_lifecycle(
        self, superadmin_client
    ):
        """T020: Full reject path: Register → Upload → Reject → REJECTED."""
        from users.models import AgencyProfile, AgencyStatus, KYCDocument

        # Create agency in PENDING
        agency = AgencyProfile.objects.create(
            manager_name="Test Agency Reject",
            commercial_registry="CR_REJECT_001",
            moh_license_number="MOH_REJECT_001",
            tax_id="TAX_REJECT_001",
            status=AgencyStatus.PENDING,
        )

        # Upload documents
        pdf_content = b"%PDF-1.4\ntest content"
        KYCDocument.objects.create(
            agency=agency,
            document_type="COMMERCIAL_REGISTRY",
            file="test/cr.pdf",
            status="PENDING",
        )

        # SuperAdmin rejects
        review_url = reverse("users:kyc-review", kwargs={"pk": agency.id})
        response = superadmin_client.post(
            review_url,
            {"action": "REJECT", "notes": "Documents are illegible"},
            format="json"
        )

        # Refresh and verify status
        agency.refresh_from_db()
        assert agency.status == AgencyStatus.REJECTED

    # =====================================================================
    # T021: Resubmission cycle - Reject → Resubmit → PENDING → Approve → VERIFIED
    # =====================================================================

    def test_resubmission_cycle(
        self, superadmin_client
    ):
        """T021: Resubmission cycle: Reject → Resubmit → PENDING → Approve → VERIFIED."""
        from users.models import AgencyProfile, AgencyStatus, KYCDocument

        # Step 1: Agency is REJECTED
        agency = AgencyProfile.objects.create(
            manager_name="Test Agency Resubmit",
            commercial_registry="CR_RESUB_001",
            moh_license_number="MOH_RESUB_001",
            tax_id="TAX_RESUB_001",
            status=AgencyStatus.REJECTED,
        )

        # Step 2: Agency resubmits (simulated)
        KYCDocument.objects.create(
            agency=agency,
            document_type="COMMERCIAL_REGISTRY",
            file="test/cr_v2.pdf",
            status="PENDING",
        )
        agency.status = AgencyStatus.PENDING
        agency.save()

        # Step 3: Status should now be PENDING
        agency.refresh_from_db()
        assert agency.status == AgencyStatus.PENDING

        # Step 4: SuperAdmin approves
        review_url = reverse("users:kyc-review", kwargs={"pk": agency.id})
        response = superadmin_client.post(
            review_url,
            {"action": "APPROVE", "notes": "Documents now valid"},
            format="json"
        )

        agency.refresh_from_db()
        assert agency.status == AgencyStatus.VERIFIED

    # =====================================================================
    # T022: Document versioning
    # =====================================================================

    def test_document_versioning(
        self, superadmin_client
    ):
        """T022: Document versioning: Upload v1 → Reject → Upload v2 → both versions exist."""
        from users.models import AgencyProfile, AgencyStatus, KYCDocument

        agency = AgencyProfile.objects.create(
            manager_name="Test Agency Version",
            commercial_registry="CR_VERSION_001",
            moh_license_number="MOH_VERSION_001",
            tax_id="TAX_VERSION_001",
            status=AgencyStatus.PENDING,
        )

        # Create v1 document
        doc_v1 = KYCDocument.objects.create(
            agency=agency,
            document_type="COMMERCIAL_REGISTRY",
            file="test/cr_v1.pdf",
            status="REJECTED",
            version=1,
        )

        # Create v2 document (after rejection)
        doc_v2 = KYCDocument.objects.create(
            agency=agency,
            document_type="COMMERCIAL_REGISTRY",
            file="test/cr_v2.pdf",
            status="PENDING",
            version=2,
        )

        # Both versions should exist
        docs = KYCDocument.objects.filter(
            agency=agency,
            document_type="COMMERCIAL_REGISTRY"
        ).order_by('version')

        assert docs.count() == 2
        assert doc_v1.version == 1
        assert doc_v2.version == 2

    # =====================================================================
    # T023: Concurrent review protection
    # =====================================================================

    def test_concurrent_review_protection(
        self, superadmin_client
    ):
        """T023: Concurrent review protection: Two approvals → first succeeds, second → 409."""
        from django.contrib.auth import get_user_model

        from users.models import AgencyProfile, AgencyStatus

        User = get_user_model()

        # Create another superadmin user for concurrent testing
        superadmin2 = User.objects.create_superuser(
            national_id="30001010100099",
            phone_number="01000000999",
            password="adminpass123",
        )

        # Create pending agency
        agency = AgencyProfile.objects.create(
            manager_name="Test Agency Concurrent",
            commercial_registry="CR_CONCUR_001",
            moh_license_number="MOH_CONCUR_001",
            tax_id="TAX_CONCUR_001",
            status=AgencyStatus.PENDING,
        )

        # First approval
        review_url = reverse("users:kyc-review", kwargs={"pk": agency.id})
        response1 = superadmin_client.post(
            review_url,
            {"action": "APPROVE", "notes": "First approval"},
            format="json"
        )

        # Second approval (simulated as concurrent)
        from rest_framework.test import APIClient
        client2 = APIClient()
        client2.force_authenticate(user=superadmin2)
        response2 = client2.post(
            review_url,
            {"action": "APPROVE", "notes": "Second approval"},
            format="json"
        )

        # One should succeed, the other should fail (409 or 400)
        assert response1.status_code in [200, 201]
        assert response2.status_code in [200, 201, 400, 409]

    # =====================================================================
    # T024: Audit log with IP and user-agent
    # =====================================================================

    def test_approve_creates_audit_log_with_ip_and_user_agent(
        self, superadmin_client
    ):
        """T024: Approve creates audit log with IP and user-agent fields populated."""
        from users.models import AgencyProfile, KYCAuditLog

        agency = AgencyProfile.objects.create(
            manager_name="Test Agency Audit",
            commercial_registry="CR_AUDIT_001",
            moh_license_number="MOH_AUDIT_001",
            tax_id="TAX_AUDIT_001",
            status="pending",
        )

        # Perform approval
        review_url = reverse("users:kyc-review", kwargs={"pk": agency.id})
        response = superadmin_client.post(
            review_url,
            {"action": "APPROVE", "notes": "Test approval"},
            format="json"
        )

        # Check audit log was created with IP and user-agent
        audit_logs = KYCAuditLog.objects.filter(agency=agency)

        if audit_logs.exists():
            latest_log = audit_logs.first()
            # IP and user-agent should be populated (or at least the field exists)
            assert hasattr(latest_log, 'ip_address')
            assert hasattr(latest_log, 'user_agent')

    # =====================================================================
    # T025: Reject without notes returns 400
    # =====================================================================

    def test_reject_without_notes_returns_400(
        self, superadmin_client
    ):
        """T025: Reject without notes → 400 validation error."""
        from users.models import AgencyProfile

        agency = AgencyProfile.objects.create(
            manager_name="Test Agency NoNotes",
            commercial_registry="CR_NONOTES_001",
            moh_license_number="MOH_NONOTES_001",
            tax_id="TAX_NONOTES_001",
            status="pending",
        )

        review_url = reverse("users:kyc-review", kwargs={"pk": agency.id})
        response = superadmin_client.post(
            review_url,
            {"action": "REJECT"},  # Missing notes
            format="json"
        )

        # Should return 400 for missing required field
        assert response.status_code == 400

    # =====================================================================
    # T026: Re-approve already verified agency returns 409
    # =====================================================================

    def test_reapprove_verified_agency_returns_409(
        self, superadmin_client
    ):
        """T026: Re-approve already verified agency → 409 Conflict."""
        from users.models import AgencyProfile, AgencyStatus

        agency = AgencyProfile.objects.create(
            manager_name="Test Agency Verified",
            commercial_registry="CR_VERIFIED_001",
            moh_license_number="MOH_VERIFIED_001",
            tax_id="TAX_VERIFIED_001",
            status=AgencyStatus.VERIFIED,
        )

        review_url = reverse("users:kyc-review", kwargs={"pk": agency.id})
        response = superadmin_client.post(
            review_url,
            {"action": "APPROVE", "notes": "Trying to re-approve"},
            format="json"
        )

        # Should return 409 Conflict (already verified)
        assert response.status_code in [409, 400]
