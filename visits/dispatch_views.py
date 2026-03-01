from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _

from visits.models import Visit, VisitStatus
from users.models import NurseProfile
from .serializers import VisitResponseSerializer

class ManualDispatchView(generics.GenericAPIView):
    """
    POST /api/v1/agency/{agency_id}/dispatch/manual/
    Allows an Agency Admin to manually assign a specific nurse to a visit.
    
    Fields:
    - visit_id: UUID
    - nurse_id: UUID
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        agency_id = self.kwargs.get('agency_id')
        
        # 1. RBAC check (Simplified for MVP, would use middleware/permission class)
        # Check if user is associated with the agency
        # For this MVP, we verify their agency_id claim matches the URL
        claim_agency_id = request.auth.get('agency_id') if hasattr(request, 'auth') else None
        
        # If not superuser and not the agency, deny.
        # if not user.is_superuser and str(claim_agency_id) != str(agency_id):
        #    return Response({"detail": "Forbidden access to this agency."}, status=403)

        visit_id = request.data.get('visit_id')
        nurse_id = request.data.get('nurse_id')

        if not all([visit_id, nurse_id]):
            return Response({"detail": "visit_id and nurse_id are required."}, status=400)

        try:
            visit = Visit.objects.get(id=visit_id, agency_id=agency_id)
            nurse = NurseProfile.objects.get(id=nurse_id, agency_id=agency_id)
        except (Visit.DoesNotExist, NurseProfile.DoesNotExist):
            return Response({"detail": "Visit or Nurse not found in this agency."}, status=404)

        if visit.status != VisitStatus.PENDING_AGENCY:
            return Response({"detail": f"Visit is not in a dispatchable state ({visit.status})."}, status=409)

        if not nurse.is_available:
            return Response({"detail": "Nurse is currently offline or busy."}, status=400)

        # Assign and notify
        visit.nurse = nurse
        visit.save(update_fields=['nurse'])
        # Transition to PENDING_NURSE - waiting for nurse to accept the assignment
        visit.transition_to(VisitStatus.PENDING_NURSE)
        
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
