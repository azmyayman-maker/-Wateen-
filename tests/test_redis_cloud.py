"""
Tests for Redis Cloud integration.

These tests verify the Redis Cloud connectivity and functionality
for caching and channel layers.
"""

import os
import uuid
import pytest
from unittest.mock import patch, MagicMock


def is_redis_available() -> bool:
    """Check if Redis is available for testing."""
    from config.redis_utils import ping_redis
    from django.conf import settings

    redis_url = os.environ.get("REDIS_URL") or getattr(
        settings.CACHES.get("default", {}), "get", lambda x: None
    )("LOCATION")
    if not redis_url:
        return False
    connected, _ = ping_redis(redis_url)
    return connected


@pytest.fixture(scope="module", autouse=True)
def skip_if_redis_not_available():
    """Skip all Redis-dependent tests if Redis is not configured."""
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        pytest.skip("REDIS_URL not configured - skipping Redis-dependent tests")


class TestRedisCloudConnection:
    """Tests for Redis Cloud connection configuration."""

    def test_redis_url_from_environment(self):
        """Test that REDIS_URL is read from environment."""
        # This test verifies the settings configuration
        from django.conf import settings

        # Check that CACHES uses REDIS_URL
        cache_location = settings.CACHES["default"]["LOCATION"]
        # It should either be the REDIS_URL or the default
        assert "redis://" in cache_location or "rediss://" in cache_location

    def test_channel_layer_uses_redis_url(self):
        """Test that channel layer uses REDIS_URL."""
        from django.conf import settings

        channel_config = settings.CHANNEL_LAYERS["default"]
        assert channel_config["BACKEND"] == "channels_redis.core.RedisChannelLayer"

        hosts = channel_config["CONFIG"]["hosts"]
        # Hosts should be a list containing the REDIS_URL
        assert isinstance(hosts, list)
        assert len(hosts) > 0


class TestRedisCacheOperations:
    """Tests for Redis cache operations."""

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        from django.core.cache import cache

        test_key = "test_cache_key"
        test_value = "test_cache_value"

        # Set value
        cache.set(test_key, test_value, 60)

        # Get value
        result = cache.get(test_key)
        assert result == test_value

        # Cleanup
        cache.delete(test_key)

    def test_cache_delete(self):
        """Test cache delete operation."""
        from django.core.cache import cache

        test_key = "test_delete_key"
        test_value = "test_delete_value"

        # Set value
        cache.set(test_key, test_value, 60)

        # Delete
        cache.delete(test_key)

        # Verify deleted
        result = cache.get(test_key)
        assert result is None

    def test_cache_expiration(self):
        """Test cache expiration."""
        from django.core.cache import cache
        import time

        test_key = "test_expire_key"
        test_value = "test_expire_value"

        # Set with 1 second timeout
        cache.set(test_key, test_value, 1)

        # Verify exists
        assert cache.get(test_key) == test_value

        # Wait for expiration
        time.sleep(2)

        # Should be expired
        result = cache.get(test_key)
        assert result is None

    def test_cache_key_prefix(self):
        """Test that cache keys use the configured prefix."""
        from django.conf import settings

        key_prefix = settings.CACHES["default"].get("KEY_PREFIX", "")
        assert key_prefix == "wateen"


class TestConnectionPoolConfiguration:
    """Tests for connection pool configuration."""

    def test_connection_pool_max_connections(self):
        """Test that connection pool has max_connections configured."""
        from django.conf import settings

        pool_kwargs = settings.CACHES["default"]["OPTIONS"].get(
            "CONNECTION_POOL_KWARGS", {}
        )

        # Should have max_connections set to 50
        assert pool_kwargs.get("max_connections") == 50


class TestChannelLayerOperations:
    """Tests for channel layer operations."""

    def test_channel_layer_send_and_receive(self):
        """Test basic channel layer send and receive."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        # Use unique channel name to avoid cross-test collisions
        test_channel = f"test_channel_{uuid.uuid4().hex}"
        test_message = {"type": "test.message", "text": "hello"}

        # Send message
        async_to_sync(channel_layer.send)(test_channel, test_message)

        # Receive message
        result = async_to_sync(channel_layer.receive)(test_channel)

        assert result == test_message

    def test_channel_layer_group(self):
        """Test channel layer group operations."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        # Use unique names to avoid cross-test collisions
        test_group = f"test_group_{uuid.uuid4().hex}"
        test_channel = f"test_group_channel_{uuid.uuid4().hex}"
        test_message = {"type": "test.message", "text": "group hello"}

        # Add channel to group
        async_to_sync(channel_layer.group_add)(test_group, test_channel)

        # Send to group
        async_to_sync(channel_layer.group_send)(test_group, test_message)

        # Receive from channel
        result = async_to_sync(channel_layer.receive)(test_channel)

        assert result["type"] == test_message["type"]
        assert result["text"] == test_message["text"]

        # Cleanup
        async_to_sync(channel_layer.group_discard)(test_group, test_channel)


class TestGracefulDegradation:
    """Tests for graceful degradation when Redis is unavailable."""

    @pytest.mark.skip(reason="Requires Redis to be unavailable")
    def test_cache_fallback_on_connection_error(self):
        """Test that cache operations handle connection errors gracefully."""
        # This test would require mocking Redis to be unavailable
        # In practice, this is tested in integration tests
        pass

    @pytest.mark.skip(reason="Requires Redis to be unavailable")
    def test_channel_layer_unavailable_notification(self):
        """Test that WebSocket features are disabled when Redis is unavailable."""
        # This test would require mocking Redis to be unavailable
        # In practice, this is tested in integration tests
        pass


class TestManagementCommand:
    """Tests for the test_redis management command."""

    def test_command_exists(self):
        """Test that the test_redis command exists."""
        from django.core.management import get_commands

        commands = get_commands()
        assert "test_redis" in commands

    @pytest.mark.skipif(not is_redis_available(), reason="Redis not available")
    def test_command_output_on_success(self):
        """Test command output when Redis is available."""
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()

        call_command("test_redis", stdout=out)
        output = out.getvalue()
        assert "Redis Connected Successfully" in output or "Cache: OK" in output
