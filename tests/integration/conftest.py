"""
Shared pytest fixtures for KYC security and integration tests.
Provides isolated tenants (agencies), documents, and authenticated clients for various roles.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from users.models import (
    AgencyProfile,
    AgencyStatus,
    CustomUser,
    KYCDocument,
    KYCDocumentType,
    UserRole,
)

@pytest.fixture(autouse=True)
def override_storage(settings):
    """Ensure all tests use in-memory storage, never S3."""
    settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'
    # Also override static files storage just in case
    settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# =====================================================================
# Users and Authentication Clients
# =====================================================================

@pytest.fixture
def superadmin_user():
    return CustomUser.objects.create_superuser(
        national_id="29001011234567",
        phone_number="01000000000",
        password="password123",
        role=UserRole.SUPERADMIN,
    )

@pytest.fixture
def superadmin_client(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    return client

@pytest.fixture
def unauthenticated_client():
    return APIClient()

@pytest.fixture
def patient_user():
    return CustomUser.objects.create_user(
        national_id="30001011234568",
        phone_number="01111111111",
        password="password123",
        role=UserRole.PATIENT,
        first_name_ar="المريض",
        last_name_ar="اختبار",
    )

@pytest.fixture
def patient_client(patient_user):
    client = APIClient()
    client.force_authenticate(user=patient_user)
    return client

@pytest.fixture
def nurse_user(agency_a):
    return CustomUser.objects.create_user(
        national_id="30001011234569",
        phone_number="01222222222",
        password="password123",
        role=UserRole.NURSE,
        first_name_ar="ممرض",
        last_name_ar="اختبار",
        agency=agency_a,
    )

@pytest.fixture
def nurse_client(nurse_user):
    client = APIClient()
    client.force_authenticate(user=nurse_user)
    return client

# =====================================================================
# Tenant Isolation (Agency A vs Agency B)
# =====================================================================

@pytest.fixture
def agency_a():
    return AgencyProfile.objects.create(
        manager_name="مدير أ",
        commercial_registry="CR-11111",
        moh_license_number="MOH-11111",
        tax_id="TAX-11111",
        status=AgencyStatus.PENDING,
    )

@pytest.fixture
def agency_a_admin(agency_a):
    return CustomUser.objects.create_user(
        national_id="30001011231111",
        phone_number="01000001111",
        password="password123",
        role=UserRole.AGENCY_ADMIN,
        agency=agency_a,
    )

@pytest.fixture
def agency_a_client(agency_a_admin):
    client = APIClient()
    client.force_authenticate(user=agency_a_admin)
    return client

@pytest.fixture
def agency_b():
    return AgencyProfile.objects.create(
        manager_name="مدير ب",
        commercial_registry="CR-22222",
        moh_license_number="MOH-22222",
        tax_id="TAX-22222",
        status=AgencyStatus.PENDING,
    )

@pytest.fixture
def agency_b_admin(agency_b):
    return CustomUser.objects.create_user(
        national_id="30001011232222",
        phone_number="01000002222",
        password="password123",
        role=UserRole.AGENCY_ADMIN,
        agency=agency_b,
    )

@pytest.fixture
def agency_b_client(agency_b_admin):
    client = APIClient()
    client.force_authenticate(user=agency_b_admin)
    return client

# =====================================================================
# KYC Documents
# =====================================================================

@pytest.fixture
def mock_file():
    def _create_file(name="test.pdf"):
        return SimpleUploadedFile(name, b"file_content", content_type="application/pdf")
    return _create_file

@pytest.fixture
def agency_a_documents(agency_a, mock_file):
    return {
        "commercial": KYCDocument.objects.create(
            agency=agency_a,
            document_type=KYCDocumentType.COMMERCIAL_REGISTRY,
            file=mock_file("cr_a.pdf"),
            version=1
        ),
        "license": KYCDocument.objects.create(
            agency=agency_a,
            document_type=KYCDocumentType.MOH_LICENSE,
            file=mock_file("moh_a.pdf"),
            version=1
        ),
        "tax": KYCDocument.objects.create(
            agency=agency_a,
            document_type=KYCDocumentType.TAX_ID,
            file=mock_file("tax_a.pdf"),
            version=1
        ),
    }

@pytest.fixture
def agency_b_documents(agency_b, mock_file):
    return {
        "commercial": KYCDocument.objects.create(
            agency=agency_b,
            document_type=KYCDocumentType.COMMERCIAL_REGISTRY,
            file=mock_file("cr_b.pdf"),
            version=1
        ),
        "license": KYCDocument.objects.create(
            agency=agency_b,
            document_type=KYCDocumentType.MOH_LICENSE,
            file=mock_file("moh_b.pdf"),
            version=1
        ),
        "tax": KYCDocument.objects.create(
            agency=agency_b,
            document_type=KYCDocumentType.TAX_ID,
            file=mock_file("tax_b.pdf"),
            version=1
        ),
    }
