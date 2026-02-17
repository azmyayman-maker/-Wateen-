from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

from users.models import UserRole, PatientProfile
from .serializers import VisitRequestSerializer, VisitResponseSerializer
from .services import create_visit_request


class VisitRequestView(APIView):
    """
    POST /api/v1/visits/request/

    Creates a new visit request for an authenticated patient.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check that the user is a patient
        if request.user.role != UserRole.PATIENT:
            return Response(
                {"detail": _("فقط المرضى يمكنهم طلب زيارة.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = VisitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get patient profile
        try:
            patient_profile = request.user.patient_profile
        except PatientProfile.DoesNotExist:
            return Response(
                {"detail": _("لم يتم العثور على ملف المريض.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        visit = create_visit_request(
            patient_profile=patient_profile,
            latitude=serializer.validated_data["latitude"],
            longitude=serializer.validated_data["longitude"],
            service_type=serializer.validated_data.get("service_type", ""),
        )

        response_serializer = VisitResponseSerializer(visit)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
