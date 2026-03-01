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
        await self.send_json(event["data"])


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
        
        if user and user.is_authenticated and agency_id:
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
        await self.send_json(event["data"])

    async def visit_update(self, event):
        """Called for any status changes of visits belonging to this agency."""
        await self.send_json(event["data"])
