import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import AgencyProfile
from .permissions import IsAgencyAdminOrSuperAdmin
from .agency_serializers import AgencyProfileSerializer
from visits.tasks import re_evaluate_pending_visits
from visits.models import Visit, VisitStatus

class AgencyCoverageUpdateView(generics.GenericAPIView):
    """
    GET, POST, PUT, DELETE for /api/v1/agencies/{agency_id}/coverage/
    """
    queryset = AgencyProfile.objects.all()
    serializer_class = AgencyProfileSerializer
    permission_classes = [IsAuthenticated, IsAgencyAdminOrSuperAdmin]

    def _check_permission(self, request, agency_id):
        user = request.user
        if not user.is_superadmin:
            user_agency = getattr(user, 'agency', None)
            if not user_agency or str(user_agency.id) != str(agency_id):
                return False
        return True

    def get(self, request, *args, **kwargs):
        agency_id = self.kwargs.get('pk')
        if not self._check_permission(request, agency_id):
            return Response(
                {"detail": "Forbidden. You can only view your own agency's coverage."},
                status=status.HTTP_403_FORBIDDEN
            )
        agency = self.get_object()
        poly = agency.coverage_polygon
        if not poly:
            return Response({"detail": "Coverage polygon not found."}, status=status.HTTP_404_NOT_FOUND)

        # Compute properties
        geom_clone = poly.clone()
        try:
            from django.conf import settings
            target_srid = getattr(settings, 'WATEEN_DEFAULT_UTM_SRID', 32636)
            geom_clone.transform(target_srid)
            area_km2 = geom_clone.area / 1_000_000.0
        except Exception:
            area_km2 = 0.0

        centroid = poly.centroid
        
        if poly.geom_type == 'Polygon':
            vertex_count = len(poly.exterior_ring.coords)
        elif poly.geom_type == 'MultiPolygon':
            vertex_count = sum(len(p.exterior_ring.coords) for p in poly)
        else:
            vertex_count = 0

        # GeoJSON feature format
        return Response({
            "type": "Feature",
            "geometry": json.loads(poly.geojson),
            "properties": {
                "area_km2": round(area_km2, 2),
                "centroid": {"lat": centroid.y, "lng": centroid.x},
                "vertex_count": vertex_count
            }
        }, status=status.HTTP_200_OK)

    def update_coverage(self, request, *args, **kwargs):
        agency_id = self.kwargs.get('pk')
        if not self._check_permission(request, agency_id):
            return Response(
                {"detail": "Forbidden. You can only update your own agency's coverage."},
                status=status.HTTP_403_FORBIDDEN
            )
               
        agency = self.get_object()
        geojson_data = request.data.get('coverage_polygon')
        
        if not geojson_data:
            return Response(
                {"detail": "coverage_polygon (GeoJSON) is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            if isinstance(geojson_data, dict):
                geojson_data = json.dumps(geojson_data)
                
            geom = GEOSGeometry(geojson_data)
        except Exception as e:
            return Response(
                {"detail": f"Invalid GeoJSON format: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer()
        try:
            geom = serializer.validate_coverage_polygon(geom)
        except ValidationError as e:
            return Response({"detail": str(e.detail[0] if isinstance(e.detail, list) else e.detail)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            agency.coverage_polygon = geom
            agency.save(update_fields=['coverage_polygon', 'updated_at'])
            transaction.on_commit(lambda aid=str(agency.id): re_evaluate_pending_visits.delay(aid))
            
        return Response(
            {"detail": "Coverage area updated successfully."}, 
            status=status.HTTP_200_OK
        )

    def put(self, request, *args, **kwargs):
        return self.update_coverage(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.update_coverage(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        agency_id = self.kwargs.get('pk')
        if not self._check_permission(request, agency_id):
            return Response(
                {"detail": "Forbidden. You can only update your own agency's coverage."},
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():
            agency = AgencyProfile.objects.select_for_update().get(pk=agency_id)
            if not agency.coverage_polygon:
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            active_visits_exist = Visit.objects.filter(
                agency=agency, 
                status__in=[VisitStatus.ACCEPTED, VisitStatus.EN_ROUTE, VisitStatus.IN_PROGRESS]
            ).exists()
            
            if active_visits_exist:
                return Response(
                    {"detail": "Cannot delete coverage polygon. Agency has active visits."},
                    status=status.HTTP_409_CONFLICT
                )
                
            agency.coverage_polygon = None
            agency.save(update_fields=['coverage_polygon', 'updated_at'])
            transaction.on_commit(lambda aid=str(agency.id): re_evaluate_pending_visits.delay(aid))
            
        return Response(status=status.HTTP_204_NO_CONTENT)
