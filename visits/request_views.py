import coreapi
import coreschema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.schemas import AutoSchema
from django.contrib.gis.geos import Point

from visits.models import Visit, ServiceType, VisitStatus
from users.models import AgencyProfile, AgencyStatus
from .serializers import VisitSerializer
from .services.dispatch import DispatchEngine

class VisitRequestSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        fields = super().get_manual_fields(path, method)
        if method == 'POST':
            fields += [
                coreapi.Field(
                    name='service_type_id',
                    required=True,
                    location='form',
                    schema=coreschema.String(description='UUID of the requested service type')
                ),
                coreapi.Field(
                    name='longitude',
                    required=True,
                    location='form',
                    schema=coreschema.Number(description='Longitude of patient location')
                ),
                coreapi.Field(
                    name='latitude',
                    required=True,
                    location='form',
                    schema=coreschema.Number(description='Latitude of patient location')
                ),
            ]
        return fields

class VisitRequestView(generics.CreateAPIView):
    """
    POST /api/v1/visits/request/
    Handles a request for a new home visit from a patient.
    Performs spatial ST_Intersects matching to find eligible agencies 
    whose coverage polygon includes the patient's location.
    """
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    permission_classes = [IsAuthenticated]
    schema = VisitRequestSchema()
    
    def create(self, request, *args, **kwargs):
        user = request.user
        
        if user.role != 'PATIENT':
            return Response({"detail": "Only patients can request visits."}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            patient_profile = user.patient_profile
        except AttributeError:
            return Response({"detail": "Patient profile not found."}, status=status.HTTP_400_BAD_REQUEST)
            
        service_type_id = request.data.get('service_type_id')
        lon = request.data.get('longitude')
        lat = request.data.get('latitude')
        
        if not all([service_type_id, lon, lat]):
            return Response(
                {"detail": "Missing required fields: service_type_id, longitude, latitude."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            service = ServiceType.objects.get(id=service_type_id)
            location_point = Point(float(lon), float(lat), srid=4326)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid coordinates."}, status=status.HTTP_400_BAD_REQUEST)
        except ServiceType.DoesNotExist:
            return Response({"detail": "Service type not found."}, status=status.HTTP_404_NOT_FOUND)
            
        # ── T018: Implement ST_Intersects spatial matching query ──
        # Find verified agencies whose coverage polygon intersects the patient's point
        eligible_agencies = AgencyProfile.objects.filter(
            status=AgencyStatus.VERIFIED,
            coverage_polygon__intersects=location_point
        ).order_by('-rating') # Prefer higher rated agencies first
        
        if not eligible_agencies.exists():
            return Response(
                {"detail": "عذراً، لا توجد شركات تمريض تغطي هذه المنطقة الجغرافية حالياً."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # For MVP Auto-Dispatch (T022 part 1), pick the best active agency.
        # In the full B2B2C architecture, we might create the visit without an assigned agency first,
        # broadcast a websocket message to all eligible agencies, and the first to accept wins (Uber-style pool).
        # Or round-robin it.
        # For simplicity based on the spec "Agency Dispatch Protocol" let's assign it to 
        # the top-rated eligible agency and set state to PENDING_AGENCY.
        assigned_agency = eligible_agencies.first()
        
        visit = Visit.objects.create(
            patient=patient_profile,
            agency=assigned_agency,
            service_type=service,
            location=location_point,
            status=VisitStatus.PENDING_AGENCY,
            base_price=service.base_price,
            final_price=service.base_price, # Calculate distance/surge later
        )
        
        serializer = self.get_serializer(visit)
        
        # NOTE: Websocket broadcast is now handled by DispatchEngine
        dispatch_engine = DispatchEngine()
        dispatch_engine.trigger_dispatch(visit)
        
        # Schedule timeout re-routing task (5 minutes)
        from .tasks import re_route_visit
        re_route_visit.apply_async((visit.id,), countdown=300)
        
        # Initialize Transaction (T027)
        from .services.settlement import SettlementService
        SettlementService.create_transaction_for_visit(visit)
        
        return Response({
            "detail": "Visit request registered and assigned to an agency for review.",
            "visit": serializer.data,
            "assigned_agency": assigned_agency.manager_name
        }, status=status.HTTP_201_CREATED)
