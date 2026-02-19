"""
Infrastructure Tests

Tests for PostgreSQL/PostGIS and Redis connectivity and functionality.
Supports both console and JSON output modes.
"""

import json
import os
import tempfile
import pytest
from django.db import connection
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@pytest.fixture
def json_output_path():
    """Create a temporary path for JSON output if needed."""
    if os.environ.get("VERIFICATION_OUTPUT") == "json":
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            yield f.name
        os.unlink(f.name)
    else:
        yield None


@pytest.mark.django_db
def test_postgres_connection_and_extension(json_output_path=None):
    """Verify primary database connection and PostGIS extension."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        assert row[0] == 1, "Database connection failed"

        cursor.execute("SELECT postgis_version();")
        version_row = cursor.fetchone()
        assert version_row is not None, "PostGIS extension not found"
        print(f"PostGIS Version: {version_row[0]}")


def test_redis_cache_connection(json_output_path=None):
    """Verify Redis cache connection."""
    cache.set("infra_test_key", "infra_test_value", 10)
    value = cache.get("infra_test_key")
    assert value == "infra_test_value", "Redis cache set/get failed"
    cache.delete("infra_test_key")


@pytest.mark.asyncio
async def test_redis_channel_layer():
    """Verify Redis Channel Layer (Async)."""
    channel_layer = get_channel_layer()
    channel_name = "infra_test_channel"
    message = {"type": "test.message", "text": "hello infra"}

    await channel_layer.send(channel_name, message)
    received = await channel_layer.receive(channel_name)

    assert received["text"] == message["text"], "Channel layer send/receive failed"


class TestVerificationScripts:
    """Tests for verification scripts with JSON output."""

    @pytest.mark.django_db
    def test_database_verification_script(self, tmp_path):
        """Test database verification produces valid JSON output."""
        json_path = tmp_path / "db_verification.json"
        os.environ["VERIFICATION_OUTPUT"] = "json"
        os.environ["VERIFICATION_JSON_PATH"] = str(json_path)

        from scripts.verification.config import get_config

        config = get_config()

        assert config.should_output_json()
        assert config.json_path == str(json_path)

    def test_cache_verification_script(self, tmp_path):
        """Test cache verification produces valid JSON output."""
        json_path = tmp_path / "cache_verification.json"
        os.environ["VERIFICATION_OUTPUT"] = "json"
        os.environ["VERIFICATION_JSON_PATH"] = str(json_path)

        from scripts.verification.config import get_config

        config = get_config()

        assert config.should_output_json()
        assert config.json_path == str(json_path)

    def test_verification_config_defaults(self):
        """Test verification config has correct defaults."""
        os.environ.pop("VERIFICATION_TIMEOUT", None)
        os.environ.pop("VERIFICATION_OUTPUT", None)
        os.environ.pop("VERIFICATION_LATENCY_THRESHOLD", None)

        from scripts.verification.config import VerificationConfig

        config = VerificationConfig.from_env()

        assert config.timeout_seconds == 5
        assert config.output_format == "both"
        assert config.latency_threshold_ms == 100
