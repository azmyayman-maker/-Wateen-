"""
WebSocket consumers for the visits app.

Contains the TestConsumer for validating WebSocket infrastructure.
"""

import logging

from channels.generic.websocket import JsonWebsocketConsumer

logger = logging.getLogger(__name__)


class TestConsumer(JsonWebsocketConsumer):
    """
    A simple WebSocket consumer for infrastructure validation.

    Accepts connections and responds to {"type": "ping"} with {"type": "pong"}.
    This consumer is used to verify the Channels/Redis/ASGI stack is working.
    """

    def connect(self):
        """Accept the WebSocket connection."""
        self.accept()
        logger.info("TestConsumer: WebSocket connection accepted")

    def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info("TestConsumer: WebSocket disconnected (code=%s)", close_code)

    def receive_json(self, content, **kwargs):
        """
        Handle incoming JSON messages.

        Responds to {"type": "ping"} with {"type": "pong"}.
        Unknown message types are logged and ignored.
        """
        message_type = content.get('type')

        if message_type == 'ping':
            self.send_json({'type': 'pong'})
        else:
            logger.warning(
                "TestConsumer: Unknown message type received: %s",
                message_type
            )
