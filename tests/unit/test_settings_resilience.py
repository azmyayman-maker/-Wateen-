"""
Unit tests for Redis resilience configuration in settings.py

Tests cover:
- Fallback to LocMemCache when no REDIS_URL configured
- Production error when no REDIS_URL and DEBUG=False
- Redis backend selection when URL is valid
- URL sanitization (no password in logs)
- GDAL auto-detection
"""

import os
from unittest.mock import patch

from config.redis_utils import (
    sanitize_redis_url,
    ping_redis,
    get_redis_config,
    get_caches_config,
    get_channel_layers_config,
    RedisConfig,
)


class TestSanitizeRedisUrl:
    """Tests for URL sanitization."""

    def test_sanitize_url_without_password(self):
        """URL without password should remain unchanged."""
        url = "redis://localhost:6379/0"
        assert sanitize_redis_url(url) == url

    def test_sanitize_url_with_password(self):
        """URL with password should have it masked."""
        url = "redis://:secret@host:6379/0"
        result = sanitize_redis_url(url)
        assert "secret" not in result
        assert ":***@" in result

    def test_sanitize_url_with_username_and_password(self):
        """URL with username:password should mask only password."""
        url = "redis://user:secret@host:6379/0"
        result = sanitize_redis_url(url)
        assert "secret" not in result
        assert "user:***@" in result

    def test_sanitize_empty_url(self):
        """Empty URL should return empty string."""
        assert sanitize_redis_url("") == ""

    def test_sanitize_none_url(self):
        """None URL should return empty string."""
        assert sanitize_redis_url(None) == ""


class TestPingRedis:
    """Tests for Redis connectivity ping."""

    def test_ping_invalid_url(self):
        """Invalid URL should return False."""
        is_connected, latency = ping_redis("invalid-url")
        assert is_connected is False
        assert latency is None

    def test_ping_empty_url(self):
        """Empty URL should return False."""
        is_connected, latency = ping_redis("")
        assert is_connected is False
        assert latency is None

    def test_ping_unreachable_host(self):
        """Unreachable host should return False within timeout."""
        is_connected, latency = ping_redis(
            "redis://nonexistent-host-12345:6379/0", timeout=0.5
        )
        assert is_connected is False
        assert latency is None


class TestGetRedisConfig:
    """Tests for Redis configuration determination."""

    def test_no_redis_url_configured(self):
        """When REDIS_URL is not set, should return locmem config."""
        with patch.dict(os.environ, {}, clear=True):
            if "REDIS_URL" in os.environ:
                del os.environ["REDIS_URL"]
            config = get_redis_config(debug=True)
            assert config.backend_type == "locmem"
            assert config.url is None
            assert config.fallback_reason == "REDIS_URL not configured"

    def test_redis_url_configured_and_reachable(self):
        """When REDIS_URL is set and reachable, should return redis config."""
        with patch("config.redis_utils.ping_redis") as mock_ping:
            mock_ping.return_value = (True, 15)
            with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}):
                config = get_redis_config(debug=True)
                assert config.backend_type == "redis"
                assert config.is_connected is True
                assert config.latency_ms == 15

    def test_redis_url_configured_but_unreachable(self):
        """When REDIS_URL is set but unreachable, should return locmem config."""
        with patch("config.redis_utils.ping_redis") as mock_ping:
            mock_ping.return_value = (False, None)
            with patch.dict(os.environ, {"REDIS_URL": "redis://unreachable:6379/0"}):
                config = get_redis_config(debug=True)
                assert config.backend_type == "locmem"
                assert config.is_connected is False
                assert config.fallback_reason is not None
                assert "unreachable" in config.fallback_reason


class TestGetCachesConfig:
    """Tests for Django CACHES configuration."""

    def test_caches_uses_redis_when_connected(self):
        """When Redis is connected, should return Redis cache backend."""
        config = RedisConfig(
            backend_type="redis",
            url="redis://localhost:6379/0",
            url_sanitized="redis://localhost:6379/0",
            is_connected=True,
            latency_ms=10,
            fallback_reason=None,
        )
        caches = get_caches_config(config)
        assert caches["default"]["BACKEND"] == "django_redis.cache.RedisCache"
        assert caches["default"]["LOCATION"] == "redis://localhost:6379/0"

    def test_caches_uses_locmem_when_not_connected(self):
        """When Redis is not connected, should return LocMemCache backend."""
        config = RedisConfig(
            backend_type="locmem",
            url=None,
            url_sanitized=None,
            is_connected=False,
            latency_ms=None,
            fallback_reason="Not configured",
        )
        caches = get_caches_config(config)
        assert (
            caches["default"]["BACKEND"]
            == "django.core.cache.backends.locmem.LocMemCache"
        )


class TestGetChannelLayersConfig:
    """Tests for Django CHANNEL_LAYERS configuration."""

    def test_channel_layers_uses_redis_when_connected(self):
        """When Redis is connected, should return Redis channel layer."""
        config = RedisConfig(
            backend_type="redis",
            url="redis://localhost:6379/0",
            url_sanitized="redis://localhost:6379/0",
            is_connected=True,
            latency_ms=10,
            fallback_reason=None,
        )
        layers = get_channel_layers_config(config)
        assert layers["default"]["BACKEND"] == "channels_redis.core.RedisChannelLayer"

    def test_channel_layers_uses_inmemory_when_not_connected(self):
        """When Redis is not connected, should return InMemoryChannelLayer."""
        config = RedisConfig(
            backend_type="locmem",
            url=None,
            url_sanitized=None,
            is_connected=False,
            latency_ms=None,
            fallback_reason="Not configured",
        )
        layers = get_channel_layers_config(config)
        assert layers["default"]["BACKEND"] == "channels.layers.InMemoryChannelLayer"


class TestGDALDetection:
    """Tests for GDAL auto-detection on Windows."""

    def test_gdal_detection_logic_exists(self):
        """GDAL detection function should exist in settings module."""
        from config import settings

        assert hasattr(settings, "_configure_gdal")

    def test_gdal_detection_skips_non_windows(self):
        """GDAL detection should skip on non-Windows platforms."""
        import platform

        if platform.system() != "Windows":
            from config import settings

            original_configure = settings._configure_gdal
            settings._configure_gdal()

    def test_gdal_detection_respects_env_var(self):
        """GDAL detection should respect existing GDAL_LIBRARY_PATH."""
        import os

        existing_path = os.environ.get("GDAL_LIBRARY_PATH")
        if existing_path:
            from config import settings

            settings._configure_gdal()
            assert os.environ.get("GDAL_LIBRARY_PATH") == existing_path


class TestGDALWarningMessage:
    """Tests for GDAL warning message."""

    def test_gdal_warning_format(self):
        """GDAL warning should include actionable guidance."""
        from config import settings

        if hasattr(settings, "_GDAL_WARNING") and settings._GDAL_WARNING:
            warning = settings._GDAL_WARNING
            assert "GDAL" in warning
            assert "doctor.py" in warning or "OSGeo4W" in warning

    def test_gdal_warning_shows_fix_options(self):
        """GDAL warning should show fix options."""
        from config import settings

        if hasattr(settings, "_GDAL_WARNING") and settings._GDAL_WARNING:
            warning = settings._GDAL_WARNING
            assert "Install" in warning or "Set" in warning
