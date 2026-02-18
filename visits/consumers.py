"""
WebSocket consumers for the visits app.

Contains the TestConsumer for validating WebSocket infrastructure.
"""

import logging

from channels.generic.websocket import JsonWebsocketConsumer
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
