from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from users.models import AgencyProfile
from users.permissions import IsAgencyAdminOrSuperAdmin
from visits.services.dashboard import AgencyDashboardService


class AgencyDashboardOverviewView(generics.GenericAPIView):
    """
    GET /api/v1/agency/{agency_id}/dashboard/overview
    Provides statistics and real-time counts for the agency dashboard.
    """

    permission_classes = [IsAuthenticated, IsAgencyAdminOrSuperAdmin]

    def get(self, request: Request, *args, **kwargs) -> Response:
        agency_id = self.kwargs.get("agency_id")

        # Verify agency exists
        try:
            agency = AgencyProfile.objects.get(id=agency_id)
        except AgencyProfile.DoesNotExist:
            return Response({"detail": "Agency not found."}, status=404)

        self.check_object_permissions(request, agency)

        data = AgencyDashboardService.get_overview_data(agency)

        return Response(data)
