from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import AgencyProfile
from .agency_serializers import AgencyRegistrationSerializer, AgencyApprovalSerializer

class AgencyRegisterView(generics.CreateAPIView):
    """
    POST /api/v1/agency/register/
    Public endpoint for a new agency to apply for the platform.
    """
    queryset = AgencyProfile.objects.all()
    serializer_class = AgencyRegistrationSerializer
    permission_classes = [AllowAny]


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
