from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from users.models import UserRole, PatientProfile, NurseProfile
from .models import Visit, VisitStatus
from .serializers import (
    VisitRequestSerializer,
    VisitResponseSerializer,
    NurseToggleSerializer,
    NurseRespondSerializer,
    NursePendingVisitSerializer,
)
from .services import create_visit_request, broadcast_visit_request

import logging

logger = logging.getLogger(__name__)


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
            service_type=serializer.validated_data.get("service_type"),
        )

        response_serializer = VisitResponseSerializer(visit)

        broadcast_visit_request(visit)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# ─── Nurse-Side Views ─────────────────────────────────────────────────────────


class NurseToggleAvailabilityView(APIView):
    """
    POST /api/v1/visits/nurse/toggle/

    Toggles nurse's online/offline availability.
    When going online, updates the nurse's GPS coordinates in Redis for geospatial matching.
    When going offline, removes the nurse from the Redis geospatial index.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != UserRole.NURSE:
            return Response(
                {"detail": _("فقط الممرضون يمكنهم تبديل الحالة.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = NurseToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            nurse_profile = request.user.nurse_profile
        except NurseProfile.DoesNotExist:
            return Response(
                {"detail": _("لم يتم العثور على ملف الممرض.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_online = serializer.validated_data["is_online"]

        # Update availability in the database
        nurse_profile.is_available = is_online

        if is_online:
            lat = serializer.validated_data["latitude"]
            lng = serializer.validated_data["longitude"]

            # Update location in PostGIS
            from django.contrib.gis.geos import Point
            nurse_profile.last_location = Point(lng, lat, srid=4326)

            # Update location in Redis for fast geospatial queries
            try:
                from .services.matching import GeoMatchingService
                geo_service = GeoMatchingService()
                geo_service.update_nurse_location(
                    nurse_id=nurse_profile.pk,
                    lat=lat,
                    lng=lng,
                )
            except Exception as e:
                logger.warning("Redis geo update failed: %s", e)
        else:
            # Remove from Redis geospatial index
            try:
                from .services.matching import GeoMatchingService
                geo_service = GeoMatchingService()
                geo_service.remove_nurse(nurse_id=nurse_profile.pk)
            except Exception as e:
                logger.warning("Redis geo removal failed: %s", e)

        nurse_profile.save()

        return Response({
            "is_online": is_online,
            "message": _("تم تحديث الحالة بنجاح."),
        })


class NursePendingVisitsView(APIView):
    """
    GET /api/v1/visits/nurse/pending/

    Returns pending visit requests that can be served by this nurse.
    Uses geospatial radius search when available, falls back to DB query.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != UserRole.NURSE:
            return Response(
                {"detail": _("فقط الممرضون يمكنهم الوصول لهذه البيانات.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            nurse_profile = request.user.nurse_profile
        except NurseProfile.DoesNotExist:
            return Response(
                {"detail": _("لم يتم العثور على ملف الممرض.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get pending visits — ordered by most recent first
        pending_visits = Visit.objects.filter(
            status=VisitStatus.PENDING,
        ).select_related(
            "patient__user",
            "service_type",
        ).order_by("-created_at")[:20]

        serializer = NursePendingVisitSerializer(pending_visits, many=True)
        return Response(serializer.data)


class NurseRespondVisitView(APIView):
    """
    POST /api/v1/visits/nurse/respond/

    Accept or decline a visit request.
    On accept: transitions visit PENDING → MATCHED → ACCEPTED, assigns nurse.
    On decline: no-op (keeps PENDING for other nurses to pick up).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != UserRole.NURSE:
            return Response(
                {"detail": _("فقط الممرضون يمكنهم الرد على الطلبات.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = NurseRespondSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        visit_id = serializer.validated_data["visit_id"]
        action = serializer.validated_data["action"]

        try:
            visit = Visit.objects.select_related("patient__user", "service_type").get(
                id=visit_id,
            )
        except Visit.DoesNotExist:
            return Response(
                {"detail": _("لم يتم العثور على الزيارة.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if action == "accept":
            if visit.status != VisitStatus.PENDING:
                return Response(
                    {"detail": str(_("لا يمكن قبول هذه الزيارة — الحالة الحالية: {}")).format(visit.status)},
                    status=status.HTTP_409_CONFLICT,
                )

            try:
                nurse_profile = request.user.nurse_profile
            except NurseProfile.DoesNotExist:
                return Response(
                    {"detail": _("لم يتم العثور على ملف الممرض.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Use atomic transaction to prevent race condition
            # Nurse assignment must be persisted before status transitions
            with transaction.atomic():
                # Select for update to prevent concurrent modifications
                visit = Visit.objects.select_for_update().get(id=visit_id)
                
                # Re-check status after acquiring lock
                if visit.status != VisitStatus.PENDING:
                    return Response(
                        {"detail": str(_("لا يمكن قبول هذه الزيارة — الحالة الحالية: {}")).format(visit.status)},
                        status=status.HTTP_409_CONFLICT,
                    )
                
                # Transition PENDING → MATCHED → ACCEPTED and assign nurse atomically
                visit.nurse = nurse_profile
                visit.save(update_fields=["nurse"])
                visit.transition_to(VisitStatus.MATCHED)
                visit.transition_to(VisitStatus.ACCEPTED)

            # Broadcast acceptance to the patient (outside transaction)
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            from .serializers import VisitResponseSerializer
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"patient_{visit.patient.id}",
                {
                    "type": "visit.update",
                    "data": {
                        "type": "visit_accepted",
                        "visit": VisitResponseSerializer(visit).data,
                        "nurse": {
                            "name": request.user.get_full_name(),
                            "phone": f"******{str(request.user.phone_number)[-4:]}" if request.user.phone_number else None
                        }
                    }
                }
            )

            return Response({
                "visit_id": str(visit.id),
                "status": visit.status,
                "message": _("تم قبول الزيارة بنجاح."),
            })

        elif action == "decline":
            # Decline is a no-op — the visit stays PENDING for other nurses
            return Response({
                "visit_id": str(visit.id),
                "status": visit.status,
                "message": _("تم رفض الطلب."),
            })
