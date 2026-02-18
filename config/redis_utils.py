"""
Redis configuration utilities for Wateen.

Provides functions for:
- Sanitizing Redis URLs (hiding passwords in logs)
- Pinging Redis servers (connectivity testing)
- Determining cache/backend configuration (Redis vs in-memory fallback)
"""

import os
import re
import socket
import ssl
from typing import NamedTuple, Optional

from decouple import config as decouple_config


class RedisConfig(NamedTuple):
    """Redis configuration result."""

    backend_type: str
    url: Optional[str]
    url_sanitized: Optional[str]
    is_connected: bool
    latency_ms: Optional[int]
    fallback_reason: Optional[str]


def sanitize_redis_url(url: Optional[str]) -> str:
    """
    Remove password from Redis URL for safe logging.

    Args:
        url: Redis connection URL (e.g., redis://:password@host:port/db)

    Returns:
        URL with password masked (e.g., redis://:***@host:port/db)

    Examples:
        >>> sanitize_redis_url("redis://localhost:6379/0")
        'redis://localhost:6379/0'
        >>> sanitize_redis_url("redis://:secret@host:6379/0")
        'redis://:***@host:6379/0'
    """
    if not url:
        return ""
    return re.sub(r"://([^:]*):([^@]+)@", r"://\1:***@", url)


def ping_redis(url: str, timeout: float = 1.0) -> tuple[bool, Optional[int]]:
    """
    Test Redis connectivity with a lightweight socket ping.

    Args:
        url: Redis connection URL
        timeout: Maximum time to wait for connection (seconds)

    Returns:
        Tuple of (is_connected, latency_ms)
        - is_connected: True if Redis responded
        - latency_ms: Connection latency in milliseconds, or None if failed
    """
    if not url:
        return False, None

    try:
        parsed = _parse_redis_url(url)
        if not parsed:
            return False, None

        host, port = parsed

        import time

        start = time.perf_counter()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        latency_ms = int((time.perf_counter() - start) * 1000)

        if result == 0:
            return True, latency_ms
        return False, None

    except (socket.error, OSError, ValueError):
        return False, None


def _parse_redis_url(url: str) -> Optional[tuple[str, int]]:
    """
    Parse Redis URL to extract host and port.

    Args:
        url: Redis connection URL

    Returns:
        Tuple of (host, port) or None if parsing fails
    """
    try:
        if url.startswith("rediss://"):
            url = "https://" + url[9:]
        elif url.startswith("redis://"):
            url = "http://" + url[8:]
        else:
            return None

        from urllib.parse import urlparse

        parsed = urlparse(url)

        host = parsed.hostname or "localhost"
        port = parsed.port or 6379

        return (host, port)
    except Exception:
        return None


def get_redis_config(debug: bool = False) -> RedisConfig:
    """
    Determine Redis configuration based on environment and connectivity.

    This is the main entry point for Redis configuration. It:
    1. Checks if REDIS_URL environment variable is set
    2. If set, attempts to ping the server
    3. Returns appropriate configuration (Redis or in-memory fallback)

    Args:
        debug: Whether DEBUG mode is enabled (affects fallback behavior)

    Returns:
        RedisConfig with backend selection and status information
    """
    redis_url = os.environ.get("REDIS_URL")
    redis_url_sanitized = sanitize_redis_url(redis_url) if redis_url else None

    if not redis_url:
        return RedisConfig(
            backend_type="locmem",
            url=None,
            url_sanitized=None,
            is_connected=False,
            latency_ms=None,
            fallback_reason="REDIS_URL not configured",
        )

    is_connected, latency_ms = ping_redis(redis_url)

    if is_connected:
        return RedisConfig(
            backend_type="redis",
            url=redis_url,
            url_sanitized=redis_url_sanitized,
            is_connected=True,
            latency_ms=latency_ms,
            fallback_reason=None,
        )

    return RedisConfig(
        backend_type="locmem",
        url=redis_url,
        url_sanitized=redis_url_sanitized,
        is_connected=False,
        latency_ms=None,
        fallback_reason=f"Redis unreachable at {redis_url_sanitized}",
    )


def get_caches_config(redis_config: RedisConfig) -> dict:
    """
    Generate Django CACHES configuration based on Redis config.

    Args:
        redis_config: Result from get_redis_config()

    Returns:
        Django CACHES dictionary
    """
    if redis_config.backend_type == "redis" and redis_config.url:
        # Determine if SSL is needed (rediss:// URLs)
        url = redis_config.url
        connection_pool_kwargs = {
            "max_connections": 50,
        }
        
        if url.startswith("rediss://"):
            # SSL configuration for Redis Cloud and other SSL-enabled Redis servers
            # Make SSL verification configurable via REDIS_SSL_VERIFY env var
            # Options: "REQUIRED" (default, secure) or "NONE" (insecure, for some cloud providers)
            verify_mode = decouple_config("REDIS_SSL_VERIFY", default="REQUIRED", cast=str).upper()
            connection_pool_kwargs["ssl_cert_reqs"] = (
                ssl.CERT_NONE if verify_mode == "NONE" else ssl.CERT_REQUIRED
            )
        
        return {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": url,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "CONNECTION_POOL_KWARGS": connection_pool_kwargs,
                    "IGNORE_EXCEPTIONS": True,
                },
                "KEY_PREFIX": "wateen",
            }
        }

    return {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "wateen-dev-cache",
        }
    }


def get_channel_layers_config(redis_config: RedisConfig) -> dict:
    """
    Generate Django CHANNEL_LAYERS configuration based on Redis config.

    Args:
        redis_config: Result from get_redis_config()

    Returns:
        Django CHANNEL_LAYERS dictionary
    """
    if redis_config.backend_type == "redis" and redis_config.url:
        # Determine if SSL is needed (rediss:// URLs)
        url = redis_config.url
        connection_kwargs = {}
        
        if url.startswith("rediss://"):
            # SSL configuration for Redis Cloud and other SSL-enabled Redis servers
            # Make SSL verification configurable via REDIS_SSL_VERIFY env var
            # Options: "REQUIRED" (default, secure) or "NONE" (insecure, for some cloud providers)
            verify_mode = decouple_config("REDIS_SSL_VERIFY", default="REQUIRED", cast=str).upper()
            connection_kwargs["ssl_cert_reqs"] = (
                ssl.CERT_NONE if verify_mode == "NONE" else ssl.CERT_REQUIRED
            )
        
        return {
            "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {
                    "hosts": [url],
                    **connection_kwargs,
                },
            }
        }

    return {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
