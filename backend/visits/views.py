import logging

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import OperationalError, transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import NurseProfile, UserRole
from visits.services.visit import NoCoverageError, RequestVisitService

from .models import ServiceType, Visit, VisitStatus
from .serializers import (
    NursePendingVisitSerializer,
    NurseRespondSerializer,
    NurseToggleSerializer,
    VisitRequestSerializer,
    VisitResponseSerializer,
)

logger = logging.getLogger(__name__)


# ─── Patient-Side Views ───────────────────────────────────────────────────────


class PatientRequestVisitView(APIView):
    """
    POST /api/v1/visits/request/

    Accepts patient visit request, executes atomic generation and triggers Celery dispatch task.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != UserRole.PATIENT:
            return Response(
                {"detail": _("فقط المرضى يمكنهم طلب زيارة.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = VisitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            patient_profile = request.user.patient_profile
        except AttributeError:
            return Response(
                {"detail": _("ملف المريض غير موجود.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        location = Point(
            serializer.validated_data["longitude"],
            serializer.validated_data["latitude"],
            srid=4326,
        )

        service_type = serializer.validated_data.get("service_type")
        if not service_type:
            service_type = ServiceType.objects.first()
            if not service_type:
                return Response(
                    {"detail": _("لا توجد أنواع خدمات متاحة بشكل افتراضي.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        service = RequestVisitService()

        distance_km = serializer.validated_data.get("distance_km")

        try:
            visit = service.execute(
                patient=patient_profile,
                service_type=service_type,
                location=location,
                distance_km=distance_km,  # Fetched from request or defaults to 5.0km
            )
        except NoCoverageError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(
                {"detail": list(e.messages) if hasattr(e, "messages") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            VisitResponseSerializer(visit).data, status=status.HTTP_201_CREATED
        )


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

        return Response(
            {
                "is_online": is_online,
                "message": _("تم تحديث الحالة بنجاح."),
            }
        )


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

        # Get pending visits — B2B2C: nurses see PENDING_NURSE visits from their agency
        if nurse_profile.agency is None:
            return Response(
                {"detail": _("الممرض/ة ليست تابعة لأي وكالة.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pending_visits = (
            Visit.objects.filter(
                status=VisitStatus.PENDING_NURSE,
                agency=nurse_profile.agency,  # Only show visits from nurse's agency
            )
            .select_related(
                "patient__user",
                "service_type",
                "agency",
            )
            .order_by("-created_at")[:20]
        )

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
            # B2B2C: Nurse can accept visits in PENDING_NURSE status
            if visit.status != VisitStatus.PENDING_NURSE:
                return Response(
                    {
                        "detail": str(
                            _("لا يمكن قبول هذه الزيارة — الحالة الحالية: {}")
                        ).format(visit.status)
                    },
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
                if visit.status != VisitStatus.PENDING_NURSE:
                    return Response(
                        {
                            "detail": str(
                                _("لا يمكن قبول هذه الزيارة — الحالة الحالية: {}")
                            ).format(visit.status)
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                # B2B2C: Assign nurse and transition directly to ACCEPTED
                visit.nurse = nurse_profile
                visit.save(update_fields=["nurse"])
                visit.transition_to(VisitStatus.ACCEPTED)

            # Broadcast acceptance to the patient (outside transaction)
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            from .serializers import VisitResponseSerializer

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"patient_{visit.patient.id}",
                {
                    "type": "visit.update",
                    "data": {
                        "type": "visit_accepted",
                        "visit": VisitResponseSerializer(visit).data,
                        "nurse": {"name": request.user.get_full_name(), "phone": None},
                    },
                },
            )

            return Response(
                {
                    "visit_id": str(visit.id),
                    "status": visit.status,
                    "message": _("تم قبول الزيارة بنجاح."),
                }
            )

        elif action == "decline":
            # Decline is a no-op — the visit stays PENDING for other nurses
            return Response(
                {
                    "detail": _("تم رفض الطلب."),
                    "visit": {
                        "id": str(visit.id),
                        "status": visit.status,
                    },
                },
                status=status.HTTP_200_OK,
            )


class NurseRespondOfferView(APIView):
    """
    POST /api/v1/visits/nurse/respond-offer/

    Accept or reject a DispatchOffer (T020).
    Uses select_for_update() for race-condition-safe acceptance.
    On ACCEPT: transitions visit → ACCEPTED, expires other offers.
    On REJECT: marks offer REJECTED.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.db import transaction
        from django.utils import timezone

        from visits.models import DispatchOffer, OfferStatus
        from visits.serializers import NurseRespondOfferSerializer

        serializer = NurseRespondOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        offer_id = serializer.validated_data["offer_id"]
        action = serializer.validated_data["action"]

        # Verify the requester is the nurse in the offer
        user = request.user
        if user.role != "NURSE":
            return Response(
                {"detail": _("فقط الممرضات يمكنهن الرد على العروض.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            nurse_profile = user.nurse_profile
        except AttributeError:
            return Response(
                {"detail": _("ملف الممرضة غير موجود.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            offer = DispatchOffer.objects.get(id=offer_id, nurse=nurse_profile)
        except DispatchOffer.DoesNotExist:
            return Response(
                {"detail": _("العرض غير موجود أو لا ينتمي لك.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if offer has expired
        if offer.status == OfferStatus.EXPIRED:
            return Response(
                {"detail": _("العرض منتهي الصلاحية.")},
                status=status.HTTP_410_GONE,
            )

        if offer.status != OfferStatus.PENDING:
            return Response(
                {"detail": _("العرض تم الرد عليه بالفعل.")},
                status=status.HTTP_409_CONFLICT,
            )

        # Check if offer has timed out
        now = timezone.now()
        if now > offer.expires_at:
            offer.status = OfferStatus.EXPIRED
            offer.save(update_fields=["status"])
            return Response(
                {"detail": _("العرض منتهي الصلاحية.")},
                status=status.HTTP_410_GONE,
            )

        if action == "reject":
            offer.status = OfferStatus.REJECTED
            offer.responded_at = now
            offer.save(update_fields=["status", "responded_at"])

            # EARLY RE-ROUTE: If no more PENDING offers, re-route immediately
            from visits.tasks import re_route_visit

            visit = offer.visit
            if not DispatchOffer.objects.filter(
                visit=visit, status=OfferStatus.PENDING
            ).exists():
                logger.info(
                    f"All offers rejected/expired for visit {visit.id}. Immediate re-route triggered."
                )
                re_route_visit.delay(str(visit.id), str(visit.agency_id))

            return Response(
                {"detail": _("تم رفض العرض.")},
                status=status.HTTP_200_OK,
            )

        # ── ACCEPT flow with race condition guard ──
        try:
            with transaction.atomic():
                # Lock the offer row with nowait=True to instantly reject concurrent requests
                locked_offer = DispatchOffer.objects.select_for_update(nowait=True).get(
                    id=offer_id, status=OfferStatus.PENDING
                )

                # Accept this offer
                locked_offer.status = OfferStatus.ACCEPTED
                locked_offer.responded_at = now
                locked_offer.save(update_fields=["status", "responded_at"])

                # Transition the visit
                visit = locked_offer.visit
                visit.nurse = nurse_profile
                visit.transition_to(VisitStatus.ACCEPTED)
                visit.save(update_fields=["nurse", "status", "updated_at"])

                # Expire all other offers for this visit
                DispatchOffer.objects.filter(
                    visit=visit, status=OfferStatus.PENDING
                ).exclude(id=offer_id).update(status=OfferStatus.EXPIRED)

        except DispatchOffer.DoesNotExist:
            # Another nurse already accepted — race condition handled
            return Response(
                {"detail": _("العرض لم يعد متاحاً. ممرضة أخرى قبلت الزيارة.")},
                status=status.HTTP_409_CONFLICT,
            )
        except OperationalError:
            # Lock could not be acquired instantly due to nowait=True
            return Response(
                {"detail": _("عفواً، ممرضة أخرى تقوم بقبول هذا العرض الآن.")},
                status=status.HTTP_409_CONFLICT,
            )

        # Notify agency admin via WebSocket
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"agency_{visit.agency_id}",
                {
                    "type": "visit.update",
                    "data": {
                        "visit_id": str(visit.id),
                        "status": "ACCEPTED",
                        "nurse_id": str(nurse_profile.id),
                        "nurse_name": user.get_full_name(),
                    },
                },
            )
        except Exception as e:
            logger.error("Failed to notify agency of offer acceptance: %s", e)

        return Response(
            {
                "detail": _("تم قبول العرض بنجاح."),
                "visit_id": str(visit.id),
                "status": visit.status,
            },
            status=status.HTTP_200_OK,
        )


class VisitStatusView(APIView):
    """
    GET /api/v1/visits/<uuid:visit_id>/status/

    T040: REST polling fallback with Redis cache-first layer.
    Returns current status, nurse location, and last update timestamp.
    Used when WebSocket connection is unavailable.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, visit_id):
        import json

        from django.core.cache import cache

        from visits.models import Visit

        user = request.user

        # T041: Authorization check must still query DB for ownership verification
        # even when serving cached status data
        try:
            visit = Visit.objects.select_related("nurse", "nurse__user", "agency").get(
                id=visit_id
            )
        except Visit.DoesNotExist:
            return Response(
                {"detail": _("الزيارة غير موجودة.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Permission: patient who owns the visit, or the assigned nurse, or agency admin
        is_patient = (
            hasattr(user, "patient_profile")
            and visit.patient_id == user.patient_profile.id
        )
        is_nurse = hasattr(user, "nurse_profile") and visit.nurse_id == getattr(
            user.nurse_profile, "id", None
        )
        is_agency = hasattr(user, "agency") and visit.agency_id == getattr(
            user, "agency_id", None
        )

        if not (is_patient or is_nurse or is_agency or user.is_staff):
            return Response(
                {"detail": _("ليس لديك صلاحية لعرض هذه الزيارة.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        # T040: Try Redis cache first
        cache_key = f"visit_status:{visit_id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            try:
                if isinstance(cached_data, str):
                    data = json.loads(cached_data)
                else:
                    data = cached_data
                return Response(data, status=status.HTTP_200_OK)
            except (json.JSONDecodeError, TypeError):
                pass

        # Cache miss - build response from DB
        data = {
            "visit_id": str(visit.id),
            "status": visit.status,
            "updated_at": visit.updated_at.isoformat() if visit.updated_at else None,
        }

        # Include nurse location if visit is active and nurse is assigned
        if visit.nurse and visit.status in ("EN_ROUTE", "IN_PROGRESS", "ACCEPTED"):
            nurse = visit.nurse
            data["nurse"] = {
                "id": str(nurse.id),
                "name": nurse.user.get_full_name() if nurse.user else "",
                "latitude": nurse.last_location.y
                if getattr(nurse, "last_location", None)
                else None,
                "longitude": nurse.last_location.x
                if getattr(nurse, "last_location", None)
                else None,
            }

            # Try to get ETA from cache
            try:
                eta = cache.get(f"nurse_eta:{nurse.id}:{visit.id}")
                if eta:
                    data["nurse"]["eta_minutes"] = eta
            except Exception:
                pass

        # Repopulate cache for next request
        try:
            cache.set(cache_key, json.dumps(data, default=str), timeout=120)
        except Exception:
            pass

        return Response(data, status=status.HTTP_200_OK)


class VisitTransitionView(APIView):
    """
    POST /api/v1/visits/<uuid:visit_id>/transition/

    T046: Nurse transitions a visit to the next status stage.
    Valid transitions: ACCEPTED → EN_ROUTE → IN_PROGRESS → COMPLETED
    Permission: Only the assigned nurse can transition.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, visit_id):
        from visits.models import Visit

        new_status = request.data.get("new_status")
        if not new_status:
            return Response(
                {"detail": _("الحالة الجديدة مطلوبة.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            visit = Visit.objects.select_related("nurse", "nurse__user").get(
                id=visit_id
            )
        except Visit.DoesNotExist:
            return Response(
                {"detail": _("الزيارة غير موجودة.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only the assigned nurse can transition
        if not (
            hasattr(request.user, "nurse_profile")
            and visit.nurse_id == request.user.nurse_profile.id
        ):
            return Response(
                {"detail": _("غير مصرح لك بتحديث هذه الزيارة.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            visit.transition_to(new_status)
        except ValidationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Broadcast visit update via WebSocket
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"patient_{visit.patient_id}",
                    {
                        "type": "visit_update",
                        "data": {
                            "visit_id": str(visit.id),
                            "status": visit.status,
                            "updated_at": str(visit.updated_at),
                        },
                    },
                )
        except Exception:
            pass  # Non-blocking

        return Response(
            {
                "visit_id": str(visit.id),
                "status": visit.status,
                "detail": _("تم تحديث حالة الزيارة بنجاح."),
            },
            status=status.HTTP_200_OK,
        )
