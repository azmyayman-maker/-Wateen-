from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from visits.models import Visit, VisitStatus
from users.models import NurseProfile, VerificationStatus
from users.permissions import IsAgencyAdminOrSuperAdmin
from .serializers import (
    VisitResponseSerializer, 
    VisitQueueSerializer,
    AvailableNurseSerializer
)

class ManualDispatchView(generics.GenericAPIView):
    """
    POST /api/v1/agency/{agency_id}/dispatch/manual/
    Allows an Agency Admin to manually assign a specific nurse to a visit.
    
    Fields:
    - visit_id: UUID
    - nurse_id: UUID
    """
    permission_classes = [IsAuthenticated, IsAgencyAdminOrSuperAdmin]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        agency_id = self.kwargs.get('agency_id')
        
        # Object-level check: Agency admin can only dispatch for their own agency
        if not user.is_superadmin:
            user_agency = getattr(user, 'agency', None)
            if not user_agency or str(user_agency.id) != str(agency_id):
                return Response(
                    {"detail": "You can only dispatch visits for your own agency."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        visit_id = request.data.get('visit_id')
        nurse_id = request.data.get('nurse_id')

        if not all([visit_id, nurse_id]):
            return Response({"detail": "visit_id and nurse_id are required."}, status=400)

        try:
            with transaction.atomic():
                visit = Visit.objects.select_for_update().get(
                    id=visit_id, agency_id=agency_id
                )
                nurse = NurseProfile.objects.select_for_update().get(
                    user_id=nurse_id, agency_id=agency_id
                )

                if visit.status != VisitStatus.PENDING_AGENCY:
                    return Response(
                        {"detail": f"Visit is not in a dispatchable state ({visit.status})."},
                        status=409,
                    )

                if not nurse.is_available:
                    return Response(
                        {"detail": "Nurse is currently offline or busy."},
                        status=400,
                    )

                # Assign and transition atomically
                visit.nurse = nurse
                visit.save(update_fields=['nurse'])
                visit.transition_to(VisitStatus.PENDING_NURSE)
        except (Visit.DoesNotExist, NurseProfile.DoesNotExist):
            return Response({"detail": "Visit or Nurse not found in this agency."}, status=404)
        
        # Broadcast to nurse
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f"nurse_{nurse.user_id}",
            {
                "type": "visit.request",
                "data": {
                    "visit": VisitResponseSerializer(visit).data,
                    "manual": True
                }
            }
        )

        return Response({
            "detail": "Nurse assigned successfully.",
            "visit_status": visit.status
        })


class VisitQueueView(generics.ListAPIView):
    """
    GET /api/v1/visits/queue/
    """
    permission_classes = [IsAuthenticated, IsAgencyAdminOrSuperAdmin]
    serializer_class = VisitQueueSerializer

    def get_queryset(self):
        user = self.request.user
        
        # SuperAdmin can optionally filter by agency or see all if not filtering
        if user.is_superadmin:
            agency_id = self.request.query_params.get('agency_id')
            if agency_id:
                return Visit.objects.filter(agency_id=agency_id, status=VisitStatus.PENDING_AGENCY)
            return Visit.objects.filter(status=VisitStatus.PENDING_AGENCY)
        
        # Regular Agency Admin
        user_agency = getattr(user, 'agency', None)
        if not user_agency:
            return Visit.objects.none()
            
        return Visit.objects.filter(agency=user_agency, status=VisitStatus.PENDING_AGENCY)


class AvailableNursesView(generics.ListAPIView):
    """
    GET /api/v1/visits/available-nurses/
    """
    permission_classes = [IsAuthenticated, IsAgencyAdminOrSuperAdmin]
    serializer_class = AvailableNurseSerializer

    def get_queryset(self):
        user = self.request.user
        
        if user.is_superadmin:
            agency_id = self.request.query_params.get('agency_id')
            if agency_id:
                return NurseProfile.objects.filter(
                    agency_id=agency_id, 
                    is_available=True, 
                    verification_status=VerificationStatus.VERIFIED
                )
            return NurseProfile.objects.filter(
                is_available=True, 
                verification_status=VerificationStatus.VERIFIED
            )
            
        user_agency = getattr(user, 'agency', None)
        if not user_agency:
            return NurseProfile.objects.none()
            
        return NurseProfile.objects.filter(
            agency=user_agency, 
            is_available=True, 
            verification_status=VerificationStatus.VERIFIED
        )
