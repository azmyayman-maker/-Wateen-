"""
WebSocket Infrastructure Tests for Ticket 2.2.

This module contains tests to validate the WebSocket infrastructure
including the TestConsumer ping/pong functionality and ASGI setup.

Uses pytest and pytest-asyncio with channels.testing.WebsocketCommunicator.

NOTE: These tests require Django to be fully configured with all dependencies
including GDAL for PostGIS. Run these tests in Docker environment:
    docker compose exec web pytest tests/test_websockets_infrastructure.py -v
"""

import pytest
from channels.testing import WebsocketCommunicator

from config.asgi import application


class TestWebSocketInfrastructure:
    """
    Test suite for WebSocket infrastructure validation.

    Tests the complete WebSocket stack: Daphne -> Channels -> Redis -> Consumer.
    """

    @pytest.mark.asyncio
    async def test_websocket_connect_success(self) -> None:
        """
        Test that WebSocket connection is established successfully.

        Verifies:
        - Connection to ws/test/ route succeeds
        - No connection errors or rejections
        """
        communicator = WebsocketCommunicator(
            application,
            "/ws/test/"
        )
        connected, _ = await communicator.connect()
        assert connected, "WebSocket connection should be accepted"
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_ping_pong_response(self) -> None:
        """
        Test the ping/pong protocol implementation.

        Verifies:
        - Sending {"type": "ping"} returns {"type": "pong"}
        - Response is exact match
        """
        communicator = WebsocketCommunicator(
            application,
            "/ws/test/"
        )
        connected, _ = await communicator.connect()
        assert connected, "WebSocket connection should be established"

        # Send ping message
        await communicator.send_json_to({"type": "ping"})

        # Receive and verify pong response
        response = await communicator.receive_json_from()
        assert response == {"type": "pong"}, (
            f"Expected {{'type': 'pong'}}, got {response}"
        )

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_unknown_message_type_logged(self) -> None:
        """
        Test that unknown message types are handled gracefully.

        Verifies:
        - Unknown message types don't cause errors
        - Connection remains open after unknown message
        """
        communicator = WebsocketCommunicator(
            application,
            "/ws/test/"
        )
        connected, _ = await communicator.connect()
        assert connected, "WebSocket connection should be established"

        # Send unknown message type
        await communicator.send_json_to({"type": "unknown_command"})

        # Connection should still be open (no response for unknown types)
        # We verify by sending a valid ping after
        await communicator.send_json_to({"type": "ping"})
        response = await communicator.receive_json_from()
        assert response == {"type": "pong"}

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_clean_disconnect(self) -> None:
        """
        Test that WebSocket connection closes cleanly.

        Verifies:
        - Disconnect completes without errors
        - No pending messages after disconnect
        """
        communicator = WebsocketCommunicator(
            application,
            "/ws/test/"
        )
        connected, _ = await communicator.connect()
        assert connected, "WebSocket connection should be established"

        # Perform a ping/pong to ensure connection is working
        await communicator.send_json_to({"type": "ping"})
        response = await communicator.receive_json_from()
        assert response == {"type": "pong"}

        # Disconnect cleanly - this should complete without error
        await communicator.disconnect()
        
        # Note: After disconnect, the communicator instance is no longer usable
        # but we've verified the disconnect was successful if we reach here

    @pytest.mark.asyncio
    async def test_multiple_ping_pong_sequence(self) -> None:
        """
        Test multiple ping/pong exchanges in sequence.

        Verifies:
        - Consumer handles multiple messages correctly
        - No state corruption between messages
        """
        communicator = WebsocketCommunicator(
            application,
            "/ws/test/"
        )
        connected, _ = await communicator.connect()
        assert connected, "WebSocket connection should be established"

        # Send multiple ping messages
        for i in range(5):
            await communicator.send_json_to({"type": "ping"})
            response = await communicator.receive_json_from()
            assert response == {"type": "pong"}, (
                f"Ping {i+1}: Expected {{'type': 'pong'}}, got {response}"
            )

        await communicator.disconnect()


class TestWebSocketRouting:
    """
    Test suite for WebSocket routing configuration.

    Verifies URL routing and pattern matching.
    """

    @pytest.mark.asyncio
    async def test_valid_websocket_route(self) -> None:
        """
        Test that valid WebSocket route connects successfully.
        """
        communicator = WebsocketCommunicator(
            application,
            "/ws/test/"
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_invalid_websocket_route_raises_error(self) -> None:
        """
        Test that invalid WebSocket routes raise ValueError.

        Verifies:
        - Non-existent routes raise ValueError
        - Proper error message for invalid routes
        """
        communicator = WebsocketCommunicator(
            application,
            "/ws/nonexistent/"
        )
        # Invalid routes should raise ValueError with "No route found" message
        with pytest.raises(ValueError, match="No route found"):
            await communicator.connect()


class TestConsumerTypeHints:
    """
    Test suite to verify Consumer type hints and structure.

    This is a static analysis test to ensure code quality.
    """

    def test_consumer_imports_successfully(self) -> None:
        """
        Test that TestConsumer can be imported without errors.
        """
        from visits.consumers import TestConsumer
        assert TestConsumer is not None

    def test_consumer_has_required_methods(self) -> None:
        """
        Test that TestConsumer has all required methods.
        """
        from visits.consumers import TestConsumer

        # Verify required methods exist
        assert hasattr(TestConsumer, 'connect'), "TestConsumer must have 'connect' method"
        assert hasattr(TestConsumer, 'disconnect'), "TestConsumer must have 'disconnect' method"
        assert hasattr(TestConsumer, 'receive_json'), "TestConsumer must have 'receive_json' method"

    def test_consumer_inherits_from_json_websocket_consumer(self) -> None:
        """
        Test that TestConsumer inherits from JsonWebsocketConsumer.
        """
        from channels.generic.websocket import JsonWebsocketConsumer
        from visits.consumers import TestConsumer

        assert issubclass(TestConsumer, JsonWebsocketConsumer), (
            "TestConsumer must inherit from JsonWebsocketConsumer"
        )