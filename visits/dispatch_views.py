from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from visits.models import Visit, VisitStatus
from users.models import NurseProfile
from users.permissions import IsAgencyAdminOrSuperAdmin
from .serializers import VisitResponseSerializer

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
                    id=nurse_id, agency_id=agency_id
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
            f"nurse_{nurse.id}",
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
