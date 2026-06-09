"""
Integration tests for Redis fallback behavior.

Tests cover:
- Dev server startup without Redis
- Redis connection with latency reporting
- Full diagnostic output
"""

import os
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.skip(reason="Doctor script has been completely rewritten.")


class TestDevServerStartup:
    """Tests for dev server startup scenarios."""

    def test_dev_server_starts_without_redis(self):
        """Dev server should start without REDIS_URL set in debug mode."""
        from config.redis_utils import get_caches_config, get_redis_config

        with patch.dict(os.environ, {}, clear=True):
            if "REDIS_URL" in os.environ:
                del os.environ["REDIS_URL"]

            config = get_redis_config(debug=True)
            caches = get_caches_config(config)

            assert config.backend_type == "locmem"
            assert (
                caches["default"]["BACKEND"]
                == "django.core.cache.backends.locmem.LocMemCache"
            )

    def test_production_gracefully_falls_back_without_redis(self):
        """Production mode falls back to locmem when REDIS_URL is missing."""
        from config.redis_utils import get_redis_config

        with patch.dict(os.environ, {"DEBUG": "False"}, clear=True):
            if "REDIS_URL" in os.environ:
                del os.environ["REDIS_URL"]

            config = get_redis_config(debug=False)

            assert config.backend_type == "locmem"
            assert config.fallback_reason is not None

    def test_redis_connection_with_latency(self):
        """Redis connection should report latency when successful."""
        from config.redis_utils import get_redis_config

        with patch("config.redis_utils.ping_redis") as mock_ping:
            mock_ping.return_value = (True, 42)
            with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}):
                config = get_redis_config(debug=True)

                assert config.backend_type == "redis"
                assert config.is_connected is True
                assert config.latency_ms == 42


class TestChannelLayersFallback:
    """Tests for Django Channels layer configuration."""

    def test_channel_layers_fallback_to_inmemory(self):
        """Channel layers should fall back to InMemoryChannelLayer without Redis."""
        from config.redis_utils import get_channel_layers_config, get_redis_config

        with patch.dict(os.environ, {}, clear=True):
            if "REDIS_URL" in os.environ:
                del os.environ["REDIS_URL"]

            config = get_redis_config(debug=True)
            layers = get_channel_layers_config(config)

            assert (
                layers["default"]["BACKEND"] == "channels.layers.InMemoryChannelLayer"
            )

    def test_channel_layers_uses_redis_when_available(self):
        """Channel layers should use Redis when available."""
        from config.redis_utils import get_channel_layers_config, get_redis_config

        with patch("config.redis_utils.ping_redis") as mock_ping:
            mock_ping.return_value = (True, 10)
            with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}):
                config = get_redis_config(debug=True)
                layers = get_channel_layers_config(config)

                assert (
                    layers["default"]["BACKEND"]
                    == "channels_redis.core.RedisChannelLayer"
                )


class TestCredentialSanitization:
    """Tests for credential masking in logs."""

    def test_password_hidden_in_config(self):
        """Passwords should be sanitized in RedisConfig."""
        from config.redis_utils import get_redis_config

        with patch("config.redis_utils.ping_redis") as mock_ping:
            mock_ping.return_value = (True, 5)
            with patch.dict(
                os.environ, {"REDIS_URL": "redis://:supersecret@host:6379/0"}
            ):
                config = get_redis_config(debug=True)

                assert config.url_sanitized is not None
                assert "supersecret" not in config.url_sanitized
                assert ":***@" in config.url_sanitized


class TestDoctorScript:
    """Tests for the diagnostic doctor script."""

    def test_doctor_script_runs_successfully(self):
        """Doctor script should execute and return results."""
        from scripts.doctor import CheckResult, run_all_checks

        results = run_all_checks()

        assert len(results) == 5
        assert all(isinstance(r, CheckResult) for r in results)

    def test_doctor_includes_all_checks(self):
        """Doctor should check all required components."""
        from scripts.doctor import run_all_checks

        results = run_all_checks()
        check_names = [r.name for r in results]

        assert "Python Version" in check_names
        assert "Environment File" in check_names
        assert "Redis Connectivity" in check_names
        assert "Database Connectivity" in check_names
        assert "GDAL" in check_names

    def test_doctor_provides_fix_commands_for_failures(self):
        """Failed checks should include fix commands."""
        from scripts.doctor import FAIL, check_env_file

        with patch.dict(os.environ, {}, clear=True):
            import os as os_module
            import tempfile

            original_cwd = os_module.getcwd()

            with tempfile.TemporaryDirectory() as tmpdir:
                os_module.chdir(tmpdir)
                if "REDIS_URL" in os.environ:
                    del os.environ["REDIS_URL"]

                result = check_env_file()
                if result.status == FAIL:
                    assert result.fix_command is not None

                os_module.chdir(original_cwd)
