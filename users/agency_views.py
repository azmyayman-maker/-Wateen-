from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status, exceptions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import AgencyProfile, KYCDocument
from .agency_serializers import (
    AgencyRegistrationSerializer,
    AgencyApprovalSerializer,
    KYCDocumentUpdateSerializer,
    KYCDocumentSerializer
)


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
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        # Additional SuperAdmin role check could go here if not fully covered by RBAC middleware
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


class AgencyKYCResubmitView(generics.CreateAPIView):
    """
    POST /api/v1/agency/kyc/resubmit/
    Agency-authenticated endpoint for resubmitting a rejected (or updated) document.
    """
    serializer_class = KYCDocumentUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def perform_create(self, serializer):
        # Restricted to Agency Admins for their OWN agency
        user = self.request.user
        if not user.is_agency_admin or not user.agency:
            raise exceptions.PermissionDenied(
                _("Only assigned agency administrators can resubmit documents.")
            )

        # 1. Inject agency context from the authenticated user
        serializer.save(agency=user.agency)

        # 2. Re-trigger SuperAdmin notification for the update
        from .services.notifications import AgencyNotificationService
        AgencyNotificationService.notify_superadmins_of_new_registration(
            agency_id=str(user.agency.id),
            manager_name=user.agency.manager_name
        )


class AgencyKYCDocumentsListView(generics.ListAPIView):
    """
    GET /api/v1/agency/kyc/documents/
    Agency-authenticated endpoint for viewing all submitted KYC docs and their status.
    """
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_agency_admin or not user.agency:
            raise exceptions.PermissionDenied(
                _("You must be an agency admin to access these documents.")
            )
        return KYCDocument.objects.filter(agency=user.agency)
