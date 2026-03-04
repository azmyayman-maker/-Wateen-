from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import GEOSGeometry

from .models import AgencyProfile
from .permissions import IsAgencyAdminOrSuperAdmin

class AgencyCoverageUpdateView(generics.UpdateAPIView):
    """
    POST /api/v1/agency/{agency_id}/coverage/
    Updates the physical coverage polygon for an Agency.
    Accepts GeoJSON representation of the polygon.
    """
    queryset = AgencyProfile.objects.all()
    # In reality we'd have a specific serializer, but we can do a simple custom method
    permission_classes = [IsAuthenticated, IsAgencyAdminOrSuperAdmin]
    
    def update(self, request, *args, **kwargs):
        # RBAC Check: Ensure the user belongs to the agency or is superadmin
        user = request.user
        agency_id = self.kwargs.get('pk')
        
        # SuperAdmins can update any agency's coverage
        if not user.is_superadmin:
            # Agency admins can only update their own agency
            user_agency = getattr(user, 'agency', None)
            if not user_agency or str(user_agency.id) != str(agency_id):
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
            # Convert GeoJSON dict/string to GEOSGeometry
            import json
            if isinstance(geojson_data, dict):
                geojson_data = json.dumps(geojson_data)
                
            geom = GEOSGeometry(geojson_data)
            
            # Basic validation
            if geom.geom_type != 'Polygon' and geom.geom_type != 'MultiPolygon':
                return Response(
                    {"detail": "Geometry must be a Polygon or MultiPolygon."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            agency.coverage_polygon = geom
            agency.save(update_fields=['coverage_polygon', 'updated_at'])
            
            return Response(
                {"detail": "Coverage area updated successfully."}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"detail": f"Invalid GeoJSON format: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # Use POST instead of PATCH as per the spec definition
    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
