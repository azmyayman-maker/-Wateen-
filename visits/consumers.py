"""
WebSocket consumers for the visits app.

Contains the TestConsumer for validating WebSocket infrastructure.
"""

import logging

from channels.generic.websocket import JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings

from users.models import CustomUser
from visits.models import Visit

logger = logging.getLogger(__name__)


class TestConsumer(JsonWebsocketConsumer):
    """
    A simple WebSocket consumer for infrastructure validation.

    Accepts connections and responds to {"type": "ping"} with {"type": "pong"}.
    This consumer is used to verify the Channels/Redis/ASGI stack is working.
    """

    def connect(self):
        """Accept the WebSocket connection if allowed."""
        user = self.scope.get("user")
        is_authenticated = user and user.is_authenticated

        if settings.DEBUG or is_authenticated:
            self.accept()
            logger.info("TestConsumer: WebSocket connection accepted")
        else:
            self.close()
            logger.warning(
                "TestConsumer: WebSocket connection rejected (DEBUG=%s, authenticated=%s)",
                settings.DEBUG,
                is_authenticated,
            )

    def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info("TestConsumer: WebSocket disconnected (code=%s)", close_code)

    def receive_json(self, content, **_kwargs):
        """
        Handle incoming JSON messages.

        Responds to {"type": "ping"} with {"type": "pong"}.
        Unknown message types are logged and ignored.
        """
        if not isinstance(content, dict):
            logger.warning(
                "TestConsumer: Non-dict JSON payload received: %s",
                type(content).__name__,
            )
            return

        message_type = content.get("type")

        if message_type == "ping":
            self.send_json({"type": "pong"})
        else:
            logger.warning(
                "TestConsumer: Unknown message type received: %s", message_type
            )


class PatientConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user and user.is_authenticated and hasattr(user, "patient_profile"):
            self.patient_id = user.patient_profile.id
            self.group_name = f"patient_{self.patient_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("PatientConsumer: connected patient %s", self.patient_id)
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def visit_update(self, event):
        data = event.get("data")
        if not data:
            logger.warning("PatientConsumer: visit_update event missing 'data' payload")
            return
        await self.send_json({"type": "visit_update", "data": data})


class NurseConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user and user.is_authenticated and hasattr(user, "nurse_profile"):
            self.nurse_id = user.nurse_profile.id
            self.group_name = f"nurse_{self.nurse_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("NurseConsumer: connected nurse %s", self.nurse_id)
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def visit_request(self, event):
        await self.send_json(event["data"])

    async def visit_cancelled(self, event):
        await self.send_json(event["data"])


class AgencyConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for Agency Administrators.
    Listens to messages on the agency_{agency_id} group.
    """

    async def connect(self):
        user = self.scope.get("user")
        # Ensure user is authenticated and has an agency_id claim
        # The agency_id is stored in the user profile or directly in the token scope
        # In our implementation, we added agency_id to the token, which JWTAuthMiddleware
        # should put into the scope or we can check the user's profile.

        # Check for agency_id in scope (set by JWTAuthMiddleware if it reads claims)
        # or check user.role and related profile.
        agency_id = self.scope.get("agency_id")

        has_permission = False
        if user and user.is_authenticated:
            # Re-verifying the dynamic properties on user
            if getattr(user, "is_superadmin", False):
                has_permission = True
            elif getattr(user, "is_agency_admin", False):
                # Optionally check if user.agency.id matches the connected agency_id
                if str(getattr(user, "agency_id", "")) == str(agency_id):
                    has_permission = True

        if has_permission and agency_id:
            self.agency_id = agency_id
            self.group_name = f"agency_{self.agency_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("AgencyConsumer: connected agency %s", self.agency_id)
        else:
            logger.warning(
                "AgencyConsumer: rejected connection for user %s. Agency ID: %s",
                user,
                agency_id,
            )
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def visit_new(self, event):
        """Called when a new visit is assigned to the agency."""
        data = event.get("data")
        if not data:
            logger.warning("AgencyConsumer: visit_new missing 'data'")
            return
        await self.send_json(data)

    async def visit_update(self, event):
        """Called for any status changes of visits belonging to this agency."""
        data = event.get("data")
        if not data:
            logger.warning("AgencyConsumer: visit_update missing 'data'")
            return
        await self.send_json(data)


class DashboardMetricsConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for live dashboard metrics (T025/US3).
    Sends real-time stats to the agency admin dashboard every 15 seconds.
    """

    async def connect(self):
        user = self.scope.get("user")
        agency_id = self.scope.get("agency_id")

        if not (user and user.is_authenticated and agency_id):
            await self.close()
            return

        self.agency_id = agency_id
        self.group_name = f"dashboard_{agency_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("DashboardMetricsConsumer: connected agency %s", agency_id)

        # Send initial stats immediately
        await self._send_metrics()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **_kwargs):
        """Handle refresh requests from the client."""
        msg_type = content.get("type") if isinstance(content, dict) else None
        if msg_type == "refresh":
            await self._send_metrics()

    async def metrics_update(self, event):
        """Receive server-side push of new metrics."""
        await self.send_json(event.get("data", {}))

    async def _send_metrics(self):
        """Compute and push agency dashboard metrics."""
        from channels.db import database_sync_to_async
        from visits.services.dashboard import AgencyDashboardService
        from users.models import AgencyProfile

        @database_sync_to_async
        def _get_data():
            try:
                agency = AgencyProfile.objects.get(id=self.agency_id)
                data = AgencyDashboardService.get_overview_data(agency)
                # Convert timestamp/Decimal to JSON-safe types
                data["timestamp"] = str(data["timestamp"])
                return data
            except AgencyProfile.DoesNotExist:
                return {"error": "Agency not found"}

        data = await _get_data()
        await self.send_json({"type": "metrics", "data": data})


class NurseGPSConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for nurse GPS location streaming (T020-T025/US3).
    Receives GPS pings from nurse PWA, validates, rate-limits,
    writes to Redis only (PostGIS deferred to Celery Beat), and broadcasts to visit room.
    """

    async def connect(self):
        user = self.scope.get("user")
        if user and user.is_authenticated and hasattr(user, "nurse_profile"):
            self.nurse_id = user.nurse_profile.id
            self._last_gps_time = 0.0  # T020: Rate limiting
            self.group_name = f"nurse_gps_{self.nurse_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("NurseGPSConsumer: connected nurse %s", self.nurse_id)
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **_kwargs):
        """T020-T025: Handle GPS ping from nurse device with validation."""
        import time
        import json
        from decimal import Decimal
        from django.core.cache import cache
        from django.utils import timezone
        from channels.db import database_sync_to_async

        if not isinstance(content, dict):
            return

        # T021: Payload size guard - reject payloads > 1KB
        payload_size = len(json.dumps(content))
        if payload_size > 1024:
            await self.send_json(
                {
                    "type": "gps_ack",
                    "success": False,
                    "error": "Payload too large",
                }
            )
            return

        lat = content.get("latitude")
        lng = content.get("longitude")

        if lat is None or lng is None:
            await self.send_json({"error": "Missing latitude/longitude"})
            return

        try:
            lat_decimal = Decimal(str(lat)).quantize(Decimal("0.000001"))
            lng_decimal = Decimal(str(lng)).quantize(Decimal("0.000001"))
            
            # T022.1: Bounds validation
            if not (-90 <= lat_decimal <= 90 and -180 <= lng_decimal <= 180):
                await self.send_json({"error": "Coordinates out of range"})
                return
                
            lat = float(lat_decimal)
            lng = float(lng_decimal)
        except (ValueError, TypeError):
            await self.send_json({"error": "Invalid coordinates"})
            return

        # T020: Rate limiting - max 1 ping per 2 seconds (Issue #2: Redis-based for safety)
        rate_limit_key = f"gps_rate_limit:{self.nurse_id}"
        if not cache.add(rate_limit_key, "1", timeout=2):
            await self.send_json(
                {
                    "type": "gps_ack",
                    "success": False,
                    "rate_limited": True,
                    "retry_after_ms": 2000,
                }
            )
            return
        # Removed instance-level self._last_gps_time check

        # T023: Redis-only write (no PostGIS)
        timestamp = timezone.now().isoformat()
        redis_key = f"nurse_gps:{self.nurse_id}"
        cache.set(
            redis_key,
            {
                "latitude": lat,
                "longitude": lng,
                "timestamp": timestamp,
            },
            timeout=120,
        )

        # T024: Broadcast to visit room
        await self._broadcast_to_visit_room(lat, lng, timestamp)

        # T025: Update Redis cache with nurse coordinates
        await self._update_visit_cache(lat, lng)

        await self.send_json(
            {
                "type": "gps_ack",
                "success": True,
                "latitude": lat,
                "longitude": lng,
            }
        )

    async def _get_active_visit_id(self):
        """Shared helper to get active visit ID for the nurse."""

        @database_sync_to_async
        def _query():
            from visits.models import Visit, VisitStatus

            return (
                Visit.objects.filter(
                    nurse_id=self.nurse_id,
                    status__in=[VisitStatus.EN_ROUTE, VisitStatus.IN_PROGRESS],
                )
                .values_list("id", flat=True)
                .first()
            )

        return await _query()

    async def _broadcast_to_visit_room(self, lat: float, lng: float, timestamp: str):
        """T024: Broadcast GPS to active visit room."""
        try:
            visit_id = await self._get_active_visit_id()
            if visit_id:
                await self.channel_layer.group_send(
                    f"visit_{visit_id}",
                    {
                        "type": "gps_update",
                        "data": {
                            "visit_id": str(visit_id),
                            "nurse_id": str(self.nurse_id),
                            "latitude": lat,
                            "longitude": lng,
                            "timestamp": timestamp,
                        },
                    },
                )
        except Exception as e:
            logger.warning("NurseGPSConsumer: Failed to broadcast to visit room: %s", e)

    async def _update_visit_cache(self, lat: float, lng: float):
        """T025: Update Redis cache with nurse coordinates."""
        try:
            visit_id = await self._get_active_visit_id()
            if visit_id:
                import json

                cache_key = f"visit_status:{visit_id}"
                cached = cache.get(cache_key)
                if cached:
                    if isinstance(cached, str):
                        cached = json.loads(cached)
                    if isinstance(cached, dict):
                        if "nurse" not in cached:
                            cached["nurse"] = {}
                        cached["nurse"]["latitude"] = lat
                        cached["nurse"]["longitude"] = lng
                        cache.set(cache_key, json.dumps(cached), timeout=120)
        except Exception as e:
            logger.warning("NurseGPSConsumer: Failed to update visit cache: %s", e)


class AgencyDashboardConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for Agency Admin dashboard (T025/US3).
    Provides real-time dashboard metrics for a specific agency.
    URL: ws/agency/<uuid:agency_id>/dashboard/
    """

    async def connect(self):
        user = self.scope.get("user")
        agency_id = self.scope.get("agency_id")
        try:
            url_agency_id = self.scope["url_route"]["kwargs"].get("agency_id")
        except KeyError:
            url_agency_id = None

        if not (
            user
            and getattr(user, "is_authenticated", False)
            and getattr(user, "is_agency_admin", False)
            and agency_id
        ):
            await self.close(code=4401)
            return

        if url_agency_id and str(agency_id) != str(url_agency_id):
            await self.close(code=4003)
            return

        self.agency_id = agency_id
        self.group_name = f"agency_{agency_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("AgencyDashboardConsumer: connected agency %s", agency_id)

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        """Handle incoming JSON messages from the client."""
        msg_type = content.get("type")
        if msg_type == "ping":
            await self.send_json({"type": "pong"})

    async def metrics_update(self, event):
        """Receive server-side push of new metrics."""
        await self.send_json(event.get("data", {}))

    async def visit_new(self, event):
        """
        Called when a new visit is dispatched to the agency.
        Broadcasts new visit request to dashboard subscribers.
        """
        data = event.get("data")
        if not data:
            logger.warning("AgencyDashboardConsumer: visit_new missing 'data'")
            return
        await self.send_json({"type": "visit_new", "data": data})

    async def visit_update(self, event):
        """
        Called when a visit status changes for this agency.
        Broadcasts status update to dashboard subscribers.
        """
        data = event.get("data")
        if not data:
            logger.warning("AgencyDashboardConsumer: visit_update missing 'data'")
            return
        await self.send_json({"type": "visit_update", "data": data})


class VisitConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for Visit real-time updates (T025).
    URL: ws/visits/<uuid:visit_id>/

    Authorization: User must be the Patient, Nurse assigned to the Visit,
    or the Agency Admin for the Visit's agency.
    """

    async def connect(self):
        user = self.scope.get("user")
        try:
            visit_id = self.scope["url_route"]["kwargs"].get("visit_id")
        except KeyError:
            visit_id = None

        if not (user and user.is_authenticated):
            await self.close(code=4401)
            return

        if not visit_id:
            await self.close(code=4003)
            return

        is_authorized = await self._verify_visit_access(user, visit_id)
        if not is_authorized:
            await self.close(code=4003)
            return

        self.visit_id = visit_id
        self.group_name = f"visit_{visit_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("VisitConsumer: connected to visit %s", visit_id)

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        """Handle incoming JSON messages from the client."""
        msg_type = content.get("type")
        if msg_type == "ping":
            await self.send_json({"type": "pong"})

    async def visit_update(self, event):
        """Receive visit status updates."""
        await self.send_json(event.get("data", {}))

    async def visit_state_change(self, event):
        """
        Called when visit status changes (e.g., ACCEPTED -> EN_ROUTE).
        Broadcasts state change to all subscribers of this visit room.
        """
        data = event.get("data")
        if not data:
            logger.warning("VisitConsumer: visit_state_change missing 'data'")
            return
        await self.send_json({"type": "visit_update", "data": data})

    async def gps_update(self, event):
        """
        Called when nurse location is updated.
        Broadcasts GPS coordinates to visit subscribers (patient, nurse, agency admin).
        """
        data = event.get("data")
        if not data:
            logger.warning("VisitConsumer: gps_update missing 'data'")
            return
        await self.send_json({"type": "gps_update", "data": data})

    @database_sync_to_async
    def _verify_visit_access(self, user: CustomUser, visit_id: str) -> bool:
        try:
            visit = Visit.objects.select_related("patient", "nurse", "agency").get(
                id=visit_id
            )
        except Visit.DoesNotExist:
            return False

        if (
            getattr(user, "is_agency_admin", False)
            and visit.agency_id
            and str(getattr(user, "agency_id", "")) == str(visit.agency_id)
        ):
            return True

        if getattr(user, "is_patient", False):
            try:
                if hasattr(user, "patient_profile") and str(visit.patient_id) == str(
                    user.patient_profile.id
                ):
                    return True
            except Exception:
                pass

        if getattr(user, "is_nurse", False):
            try:
                if hasattr(user, "nurse_profile") and str(visit.nurse_id) == str(
                    user.nurse_profile.id
                ):
                    return True
            except Exception:
                pass

        return False
