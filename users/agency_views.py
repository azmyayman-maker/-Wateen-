from typing import Any

from django.db import transaction
from django.db.models import Prefetch, QuerySet
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status, exceptions, serializers
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import AgencyProfile, AgencyStatus, KYCDocument, KYCAuditLog
from .permissions import IsSuperAdmin, IsAgencyAdmin, IsAgencyAdminAnyStatus
from .services.notifications import (
    AgencyNotificationService,
    send_kyc_review_email_task,
)
from .services.kyc_review_service import AgencyKYCService
from .agency_serializers import (
    AgencyRegistrationSerializer,
    AgencyApprovalSerializer,
    KYCDocumentUpdateSerializer,
    KYCDocumentSerializer,
    KYCAuditLogSerializer,
    KYCQueueSerializer,
    KYCReviewSerializer,
)


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request, handling proxies.
    
    Only trusts X-Forwarded-For when the immediate peer IP (REMOTE_ADDR)
    is in settings.TRUSTED_PROXIES to prevent client spoofing.
    """
    from django.conf import settings
    remote_addr = request.META.get('REMOTE_ADDR', '')
    trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', [])
    
    if remote_addr in trusted_proxies:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
    return remote_addr


class AgencyRegisterView(generics.CreateAPIView):
    """
    POST /api/v1/agency/register/
    Public endpoint for a new agency to apply for the platform.
    Accepts application/json and multipart/form-data for file uploads.
    """
    queryset = AgencyProfile.objects.all()
    serializer_class = AgencyRegistrationSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, JSONParser]


class AgencyApprovalView(generics.UpdateAPIView):
    """
    PATCH /api/v1/admin/agencies/<id>/approve/
    SuperAdmin endpoint to approve or reject an agency application.
    """
    queryset = AgencyProfile.objects.all()
    serializer_class = AgencyApprovalSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        if not (user.is_superadmin or user.is_superuser):
            return Response(
                {"detail": "Only superusers can approve agencies."},
                status=status.HTTP_403_FORBIDDEN
            )

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        if not (user.is_superadmin or user.is_superuser):
            return Response(
                {"detail": "Only superusers can approve agencies."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().put(request, *args, **kwargs)


class AgencyKYCResubmitView(generics.CreateAPIView):
    """
    POST /api/v1/agency/kyc/resubmit/
    Agency-authenticated endpoint for resubmitting a rejected (or updated) document.
    When documents are resubmitted for a REJECTED agency, it transitions back to PENDING.
    """
    serializer_class = KYCDocumentUpdateSerializer
    permission_classes = [IsAuthenticated, IsAgencyAdminAnyStatus]
    parser_classes = [MultiPartParser]

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        user = self.request.user

        # Guard: misconfigured agency-admin without a linked AgencyProfile
        if not getattr(user, 'agency', None):
            raise exceptions.PermissionDenied(
                _("Your account is not linked to an agency.")
            )

        agency = user.agency
        ip_address = get_client_ip(self.request)
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:500]

        # Wrap in atomic transaction
        with transaction.atomic():
            # 1. Save the new document version
            serializer.save(agency=agency)

            # 2. Handle resubmission status transition and audit log via service
            AgencyKYCService.handle_resubmission(
                agency=agency,
                reviewer=user,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        # 3. Re-trigger SuperAdmin notification (deferred until DB commit)
        transaction.on_commit(
            lambda: AgencyNotificationService.notify_superadmins_of_new_registration(
                agency_id=str(agency.id),
                manager_name=agency.manager_name,
            )
        )




class AgencyKYCDocumentsListView(generics.ListAPIView):
    """
    GET /api/v1/agency/kyc/documents/
    Agency-authenticated endpoint for viewing all submitted KYC docs and their status.
    """
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsAuthenticated, IsAgencyAdminAnyStatus]

    def get_queryset(self) -> "QuerySet[KYCDocument]":
        user = self.request.user
        return KYCDocument.objects.filter(agency=user.agency)


class KYCAuditLogListView(generics.ListAPIView):
    """
    GET /api/v1/admin/agencies/<agency_id>/kyc-audit-logs/
    Read-only endpoint for SuperAdmins to view the immutable audit trail of an agency.
    """
    serializer_class = KYCAuditLogSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_queryset(self) -> "QuerySet[KYCAuditLog]":
        agency_id = self.kwargs.get('agency_id')
        return KYCAuditLog.objects.filter(agency_id=agency_id).select_related('reviewer')


class KYCQueueListView(generics.ListAPIView):
    """
    GET /api/v1/admin/kyc-queue/
    SuperAdmin endpoint to list all PENDING agencies with their KYC documents, in oldest-first order (FIFO).
    """
    serializer_class = KYCQueueSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_queryset(self) -> "QuerySet[AgencyProfile]":

        return AgencyProfile.objects.filter(
            status=AgencyStatus.PENDING
        ).prefetch_related(
            Prefetch(
                'kyc_documents',
                queryset=KYCDocument.objects.all()
            )
        ).order_by('created_at', 'id')


class KYCReviewView(generics.UpdateAPIView):
    """
    POST /api/v1/admin/agencies/<uuid:pk>/review/
    SuperAdmin endpoint to approve or reject a pending agency KYC application.
    
    Uses select_for_update() for concurrency control and transaction.atomic()
    for atomic status change + audit log creation.
    """
    serializer_class = KYCReviewSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = AgencyProfile.objects.all()
    http_method_names = ['post']

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.update(request, *args, **kwargs)

    def get_object(self) -> AgencyProfile:
        """
        Override to use select_for_update() for concurrency control.
        """
        pk = self.kwargs.get('pk')
        try:
            # Use select_for_update to lock the row during the transaction
            return AgencyProfile.objects.select_for_update().get(pk=pk)
        except AgencyProfile.DoesNotExist:
            raise exceptions.NotFound(_("Agency not found."))

    @transaction.atomic
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Process the review action using the KYC service.
        The service handles status validation, transitions, and audit logging.
        """
        agency = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']
        notes = serializer.validated_data.get('notes', '')

        # Get client IP and user agent for audit log (Law 151/2020)
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        # Delegate b2b logic to the service
        try:
            result = AgencyKYCService.review_agency(
                agency=agency,
                reviewer=request.user,
                action=action,
                notes=notes,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        # Schedule email notification via Celery on transaction commit
        transaction.on_commit(
            lambda: send_kyc_review_email_task.delay(
                agency_id=str(agency.id),
                action=action,
                notes=notes,
            )
        )

        message = (
            _("Agency approved successfully.")
            if action == 'APPROVE'
            else _("Agency rejected. The agency has been notified.")
        )

        return Response(
            {
                "id": str(agency.id),
                "status": agency.status,
                "action": action,
                "audit_log_id": str(result.audit_log.id),
                "message": message,
            },
            status=status.HTTP_200_OK,
        )

