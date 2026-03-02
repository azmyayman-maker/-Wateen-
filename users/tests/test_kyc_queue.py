from unittest.mock import patch

import pytest
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from users.models import (
    AgencyProfile, AgencyStatus, CustomUser, KYCAuditLog,
    KYCDocument, KYCDocumentType,
)

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def superadmin_client():
    client = APIClient()
    user = CustomUser.objects.create_superuser(
        national_id='29001011234567',
        email='superadmin@wateen.com',
        password='password123',
        phone_number='01000000000',
    )
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def agency_admin():
    agency = AgencyProfile.objects.create(
        manager_name='Test Manager',
        status=AgencyStatus.PENDING,
        commercial_registry='12345',
        moh_license_number='67890',
        tax_id='11111',
    )
    return CustomUser.objects.create_user(
        national_id='29001011234568',
        email='admin@agency.com',
        password='password123',
        phone_number='01111111111',
        role='AGENCY_ADMIN',
        first_name_ar='Admin',
        last_name_ar='User',
        agency=agency,
    )


@pytest.fixture
def pending_agency(agency_admin):
    return agency_admin.agency


# ---------------------------------------------------------------------------
# US4 – Immutable Audit Trail
# ---------------------------------------------------------------------------
def test_kyc_audit_log_immutability(pending_agency, superadmin_client):
    log = KYCAuditLog.objects.create(
        agency=pending_agency,
        reviewer=CustomUser.objects.filter(role='SUPERADMIN').first(),
        action='APPROVE',
        notes='Looks good',
    )

    with pytest.raises(PermissionDenied):
        log.notes = 'Changed note'
        log.save()

    with pytest.raises(PermissionDenied):
        log.delete()


def test_kyc_audit_log_list_api(pending_agency, superadmin_client):
    KYCAuditLog.objects.create(
        agency=pending_agency,
        reviewer=CustomUser.objects.filter(role='SUPERADMIN').first(),
        action='APPROVE',
        notes='Everything is verified.',
    )
    url = reverse('users:kyc-audit-logs', kwargs={'agency_id': pending_agency.id})
    response = superadmin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['action'] == 'APPROVE'


def test_kyc_audit_log_list_api_agency_admin(pending_agency, agency_admin):
    client = APIClient()
    client.force_authenticate(user=agency_admin)
    url = reverse('users:kyc-audit-logs', kwargs={'agency_id': pending_agency.id})
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# US1 – KYC Queue (GET /api/v1/admin/kyc-queue/)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage',
)
@patch('users.services.storage.KYCStorageService.get_presigned_url', return_value='http://dummy.url/')
def test_kyc_queue_list_pending_only(mock_presigned, pending_agency, superadmin_client, agency_admin):
    """Only PENDING agencies appear; VERIFIED ones are excluded."""
    # VERIFIED agency – must NOT appear
    AgencyProfile.objects.create(
        manager_name='Verified Manager',
        status=AgencyStatus.VERIFIED,
        commercial_registry='22222',
        moh_license_number='33333',
        tax_id='44444',
    )

    # Attach a KYC doc (InMemoryStorage avoids real S3 calls)
    KYCDocument.objects.create(
        agency=pending_agency,
        document_type=KYCDocumentType.MOH_LICENSE,
        file=SimpleUploadedFile('dummy.pdf', b'file_content', content_type='application/pdf'),
    )

    url = reverse('users:kyc-queue')
    response = superadmin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1

    agency_data = response.data['results'][0]
    assert agency_data['id'] == str(pending_agency.id)
    assert 'kyc_documents' in agency_data
    assert len(agency_data['kyc_documents']) == 1


@patch('users.services.storage.KYCStorageService.get_presigned_url', return_value='http://dummy.url/')
def test_kyc_queue_oldest_first(mock_presigned, pending_agency, superadmin_client):
    """Queue is FIFO: oldest agency first."""
    newer_agency = AgencyProfile.objects.create(
        manager_name='Newer Manager',
        status=AgencyStatus.PENDING,
        commercial_registry='99999',
        moh_license_number='88888',
        tax_id='77777',
    )
    # auto_now_add fields ignore .save(), so use queryset.update()
    future = timezone.now() + timezone.timedelta(hours=1)
    AgencyProfile.objects.filter(pk=newer_agency.pk).update(created_at=future)

    url = reverse('users:kyc-queue')
    response = superadmin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2

    # Oldest first → pending_agency before newer_agency
    assert response.data['results'][0]['id'] == str(pending_agency.id)
    assert response.data['results'][1]['id'] == str(newer_agency.id)


def test_kyc_queue_permission_denied(agency_admin):
    client = APIClient()
    client.force_authenticate(user=agency_admin)
    url = reverse('users:kyc-queue')
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# US2 – Approve Agency (with concurrency control)
# ----------------------------------------------------------------------------
def test_kyc_approve_pending_agency(pending_agency, superadmin_client):
    """SuperAdmin can approve a PENDING agency."""
    url = reverse('users:kyc-review', kwargs={'pk': pending_agency.id})
    response = superadmin_client.post(
        url,
        {'action': 'APPROVE', 'notes': 'All documents verified'},
        format='json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'verified'
    assert response.data['action'] == 'APPROVE'
    
    # Verify agency status updated
    pending_agency.refresh_from_db()
    assert pending_agency.status == AgencyStatus.VERIFIED


def test_kyc_approve_non_pending_agency_conflict(pending_agency, superadmin_client):
    """Approving a non-PENDING agency returns 409 Conflict."""
    # First approve the agency
    pending_agency.status = AgencyStatus.VERIFIED
    pending_agency.save()
    
    url = reverse('users:kyc-review', kwargs={'pk': pending_agency.id})
    response = superadmin_client.post(
        url,
        {'action': 'APPROVE', 'notes': 'Trying to approve again'},
        format='json'
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_kyc_approve_creates_audit_log(pending_agency, superadmin_client):
    """Approving an agency creates an immutable audit log entry."""
    url = reverse('users:kyc-review', kwargs={'pk': pending_agency.id})
    response = superadmin_client.post(
        url,
        {'action': 'APPROVE', 'notes': 'Looks good!'},
        format='json'
    )
    assert response.status_code == status.HTTP_200_OK
    
    audit_log_id = response.data['audit_log_id']
    audit_log = KYCAuditLog.objects.get(id=audit_log_id)
    assert audit_log.action == 'APPROVE'
    assert audit_log.agency_id == pending_agency.id
    assert audit_log.notes == 'Looks good!'


def test_kyc_approve_rbac_denied(agency_admin, pending_agency):
    """Non-SuperAdmin users cannot approve agencies."""
    client = APIClient()
    client.force_authenticate(user=agency_admin)
    url = reverse('users:kyc-review', kwargs={'pk': pending_agency.id})
    response = client.post(
        url,
        {'action': 'APPROVE', 'notes': 'Unauthorized'},
        format='json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# US3 – Reject Agency
# ----------------------------------------------------------------------------
def test_kyc_reject_pending_agency(pending_agency, superadmin_client):
    """SuperAdmin can reject a PENDING agency with notes."""
    url = reverse('users:kyc-review', kwargs={'pk': pending_agency.id})
    response = superadmin_client.post(
        url,
        {'action': 'REJECT', 'notes': 'Missing commercial registry document'},
        format='json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'rejected'
    assert response.data['action'] == 'REJECT'
    
    # Verify agency status updated
    pending_agency.refresh_from_db()
    assert pending_agency.status == AgencyStatus.REJECTED


def test_kyc_reject_without_notes_fails(pending_agency, superadmin_client):
    """Rejecting without notes returns validation error."""
    url = reverse('users:kyc-review', kwargs={'pk': pending_agency.id})
    response = superadmin_client.post(
        url,
        {'action': 'REJECT'},
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'notes' in response.data


def test_kyc_reject_creates_audit_log(pending_agency, superadmin_client):
    """Rejecting an agency creates an immutable audit log entry with notes."""
    url = reverse('users:kyc-review', kwargs={'pk': pending_agency.id})
    response = superadmin_client.post(
        url,
        {'action': 'REJECT', 'notes': 'Documents expired'},
        format='json'
    )
    assert response.status_code == status.HTTP_200_OK
    
    audit_log_id = response.data['audit_log_id']
    audit_log = KYCAuditLog.objects.get(id=audit_log_id)
    assert audit_log.action == 'REJECT'
    assert audit_log.notes == 'Documents expired'


# ---------------------------------------------------------------------------
# US5 – Email Notifications (Celery Task)
# ----------------------------------------------------------------------------
def test_kyc_review_triggers_email_task(pending_agency, superadmin_client):
    """Approving an agency triggers the Celery email task."""
    url = reverse('users:kyc-review', kwargs={'pk': pending_agency.id})
    
    with patch('users.agency_views.send_kyc_review_email_task.delay') as mock_task, \
         patch('django.db.transaction.on_commit', side_effect=lambda f: f()):
        response = superadmin_client.post(
            url,
            {'action': 'APPROVE', 'notes': 'Approved'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_task.assert_called_once()
        call_kwargs = mock_task.call_args[1]
        assert call_kwargs['agency_id'] == str(pending_agency.id)
        assert call_kwargs['action'] == 'APPROVE'


# ---------------------------------------------------------------------------
# US3 Extension – Resubmit after Rejection
# ----------------------------------------------------------------------------
def test_rejected_agency_resubmit_transitions_to_pending(agency_admin):
    """When a rejected agency resubmits documents, status transitions back to PENDING."""
    # First, reject the agency
    agency = agency_admin.agency
    agency.status = AgencyStatus.REJECTED
    agency.save()
    
    # Now submit new documents
    url = reverse('users:agency_kyc_resubmit')
    client = APIClient()
    client.force_authenticate(user=agency_admin)
    
    with override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage'), \
         patch('users.agency_views.AgencyNotificationService.notify_superadmins_of_new_registration'):
        response = client.post(
            url,
            {
                'document_type': KYCDocumentType.COMMERCIAL_REGISTRY,
                'file': SimpleUploadedFile('new_doc.pdf', b'%PDF-1.4\n%EOF\n', content_type='application/pdf'),
            },
            format='multipart'
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify agency is now PENDING
    agency.refresh_from_db()
    assert agency.status == AgencyStatus.PENDING


def test_resubmit_creates_audit_log(agency_admin):
    """Resubmitting documents creates an audit log entry."""
    # First, reject the agency
    agency = agency_admin.agency
    agency.status = AgencyStatus.REJECTED
    agency.save()
    
    # Now submit new documents
    url = reverse('users:agency_kyc_resubmit')
    client = APIClient()
    client.force_authenticate(user=agency_admin)
    
    with override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage'), \
         patch('users.agency_views.AgencyNotificationService.notify_superadmins_of_new_registration'):
        response = client.post(
            url,
            {
                'document_type': KYCDocumentType.COMMERCIAL_REGISTRY,
                'file': SimpleUploadedFile('new_doc.pdf', b'%PDF-1.4\n%EOF\n', content_type='application/pdf'),
            },
            format='multipart'
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify audit log was created
    audit_log = KYCAuditLog.objects.filter(agency=agency, action='RESUBMIT').first()
    assert audit_log is not None
    assert audit_log.notes == 'Documents resubmitted after rejection'
