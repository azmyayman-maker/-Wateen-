"""
WebSocket consumers for the visits app.

Contains the TestConsumer for validating WebSocket infrastructure.
"""

import logging

from channels.generic.websocket import JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from django.conf import settings

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
        if user and user.is_authenticated and hasattr(user, 'patient_profile'):
            self.patient_id = user.patient_profile.id
            self.group_name = f"patient_{self.patient_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("PatientConsumer: connected patient %s", self.patient_id)
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
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
        if user and user.is_authenticated and hasattr(user, 'nurse_profile'):
            self.nurse_id = user.nurse_profile.id
            self.group_name = f"nurse_{self.nurse_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("NurseConsumer: connected nurse %s", self.nurse_id)
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
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
            if getattr(user, 'is_superadmin', False):
                has_permission = True
            elif getattr(user, 'is_agency_admin', False):
                # Optionally check if user.agency.id matches the connected agency_id
                if str(getattr(user, 'agency_id', '')) == str(agency_id):
                    has_permission = True
        
        if has_permission and agency_id:
            self.agency_id = agency_id
            self.group_name = f"agency_{self.agency_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("AgencyConsumer: connected agency %s", self.agency_id)
        else:
            logger.warning("AgencyConsumer: rejected connection for user %s. Agency ID: %s", user, agency_id)
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
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
        if hasattr(self, 'group_name'):
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
    WebSocket consumer for nurse GPS location streaming (T028/US3).
    Receives GPS pings from nurse PWA, updates Redis geo index.
    """
    async def connect(self):
        user = self.scope.get("user")
        if user and user.is_authenticated and hasattr(user, 'nurse_profile'):
            self.nurse_id = user.nurse_profile.id
            self.group_name = f"nurse_gps_{self.nurse_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("NurseGPSConsumer: connected nurse %s", self.nurse_id)
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **_kwargs):
        """Handle GPS ping from nurse device."""
        if not isinstance(content, dict):
            return

        lat = content.get("latitude")
        lng = content.get("longitude")

        if lat is None or lng is None:
            await self.send_json({"error": "Missing latitude/longitude"})
            return

        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            await self.send_json({"error": "Invalid coordinates"})
            return

        # Update Redis geo index
        from channels.db import database_sync_to_async

        @database_sync_to_async
        def _update_location():
            from visits.services.matching import GeoMatchingService
            geo = GeoMatchingService()
            return geo.update_nurse_location(self.nurse_id, lat, lng)

        success = await _update_location()
        await self.send_json({
            "type": "gps_ack",
            "success": success,
            "latitude": lat,
            "longitude": lng,
        })
