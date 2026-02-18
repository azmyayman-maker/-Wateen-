#!/usr/bin/env python
"""
Wateen Environment Diagnostics Script

Run this script to diagnose your development environment setup.
Checks Python version, environment file, Redis, database, and GDAL.

Usage:
    python scripts/doctor.py

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
    2 - Configuration error
"""

import os
import sys
import time
import socket
from pathlib import Path
from typing import NamedTuple, Optional, List


class CheckResult(NamedTuple):
    """Result of a single diagnostic check."""

    name: str
    status: str  # 'pass', 'fail', 'warning'
    message: str
    fix_command: Optional[str] = None
    latency_ms: Optional[int] = None


PASS = "pass"
FAIL = "fail"
WARNING = "warning"


def check_python_version() -> CheckResult:
    """Check that Python version is 3.11 or higher."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 11:
        return CheckResult(
            name="Python Version",
            status=PASS,
            message=f"{version_str} (Required: 3.11+)",
        )

    return CheckResult(
        name="Python Version",
        status=FAIL,
        message=f"{version_str} (Required: 3.11+)",
        fix_command="Install Python 3.11 or higher from https://www.python.org/downloads/",
    )


def check_env_file() -> CheckResult:
    """Check that .env file exists."""
    env_path = Path(".env")

    if env_path.exists():
        return CheckResult(
            name="Environment File",
            status=PASS,
            message=".env found",
        )

    return CheckResult(
        name="Environment File",
        status=FAIL,
        message=".env not found",
        fix_command="Copy .env.example to .env and configure your environment variables",
    )


def check_redis() -> CheckResult:
    """Check Redis connectivity."""
    redis_url = os.environ.get("REDIS_URL")

    if not redis_url:
        return CheckResult(
            name="Redis Connectivity",
            status=WARNING,
            message="REDIS_URL not configured",
            fix_command="Set REDIS_URL environment variable (optional for development)",
        )

    parsed = _parse_redis_url(redis_url)
    if not parsed:
        return CheckResult(
            name="Redis Connectivity",
            status=FAIL,
            message="Invalid REDIS_URL format",
            fix_command="Ensure REDIS_URL format is: redis://[:password@]host[:port][/db]",
        )

    host, port = parsed

    try:
        start = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        result = sock.connect_ex((host, port))
        sock.close()
        latency_ms = int((time.perf_counter() - start) * 1000)

        if result == 0:
            return CheckResult(
                name="Redis Connectivity",
                status=PASS,
                message=f"Connected to {host}:{port}",
                latency_ms=latency_ms,
            )

        return CheckResult(
            name="Redis Connectivity",
            status=FAIL,
            message=f"Connection refused to {host}:{port}",
            fix_command="Ensure Redis server is running and accessible",
        )

    except socket.error as e:
        return CheckResult(
            name="Redis Connectivity",
            status=FAIL,
            message=f"Connection error: {e}",
            fix_command="Check network connectivity and Redis server status",
        )


def _parse_redis_url(url: str) -> Optional[tuple]:
    """Parse Redis URL to extract host and port."""
    try:
        from urllib.parse import urlparse

        if url.startswith("rediss://"):
            url = "https://" + url[9:]
        elif url.startswith("redis://"):
            url = "http://" + url[8:]
        else:
            return None

        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379

        return (host, port)
    except Exception:
        return None


def check_database() -> CheckResult:
    """Check database connectivity."""
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        return CheckResult(
            name="Database Connectivity",
            status=WARNING,
            message="DATABASE_URL not configured",
            fix_command="Set DATABASE_URL environment variable",
        )

    try:
        import dj_database_url
        import django
        from django.conf import settings

        if not settings.configured:
            settings.configure(
                DEBUG=True,
                DATABASES={
                    "default": dj_database_url.config(
                        default=database_url,
                        conn_max_age=600,
                    )
                },
                INSTALLED_APPS=[],
            )
            django.setup()

        from django.db import connection

        start = time.perf_counter()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        latency_ms = int((time.perf_counter() - start) * 1000)

        return CheckResult(
            name="Database Connectivity",
            status=PASS,
            message="Connected",
            latency_ms=latency_ms,
        )

    except ImportError:
        return CheckResult(
            name="Database Connectivity",
            status=FAIL,
            message="dj-database-url not installed",
            fix_command="pip install dj-database-url",
        )
    except Exception as e:
        return CheckResult(
            name="Database Connectivity",
            status=FAIL,
            message=f"Connection failed: {str(e)[:50]}",
            fix_command="Check DATABASE_URL format and database server status",
        )


def check_gdal() -> CheckResult:
    """Check GDAL availability."""
    if os.name == "nt":
        if os.environ.get("GDAL_LIBRARY_PATH"):
            gdal_path = os.environ["GDAL_LIBRARY_PATH"]
            if Path(gdal_path).exists():
                return CheckResult(
                    name="GDAL",
                    status=PASS,
                    message=f"Available at {gdal_path}",
                )

            return CheckResult(
                name="GDAL",
                status=WARNING,
                message=f"GDAL_LIBRARY_PATH set but file not found: {gdal_path}",
                fix_command="Verify GDAL installation or reinstall OSGeo4W",
            )

        common_paths = [
            r"C:\OSGeo4W\bin\gdal304.dll",
            r"C:\OSGeo4W\bin\gdal303.dll",
            r"C:\OSGeo4W\bin\gdal302.dll",
            r"C:\Program Files\QGIS 3.28\bin\gdal304.dll",
            r"C:\Program Files\QGIS 3.34\bin\gdal304.dll",
        ]

        for path in common_paths:
            if Path(path).exists():
                return CheckResult(
                    name="GDAL",
                    status=PASS,
                    message=f"Found at {path}",
                )

        return CheckResult(
            name="GDAL",
            status=WARNING,
            message="Not found on Windows",
            fix_command="Install OSGeo4W from https://trac.osgeo.org/osgeo4w/ or set GDAL_LIBRARY_PATH",
        )

    try:
        from osgeo import gdal

        version = gdal.__version__
        return CheckResult(
            name="GDAL",
            status=PASS,
            message=f"Available (version {version})",
        )
    except ImportError:
        return CheckResult(
            name="GDAL",
            status=WARNING,
            message="Not installed",
            fix_command="Install GDAL via your system package manager (apt install gdal-bin / brew install gdal)",
        )


def run_all_checks() -> List[CheckResult]:
    """Run all diagnostic checks."""
    return [
        check_python_version(),
        check_env_file(),
        check_redis(),
        check_database(),
        check_gdal(),
    ]


def format_result(result: CheckResult) -> str:
    """Format a single check result for display."""
    status_icons = {
        PASS: "[PASS]",
        FAIL: "[FAIL]",
        WARNING: "[WARN]",
    }

    icon = status_icons[result.status]
    lines = [f"{icon} {result.name}: {result.message}"]

    if result.latency_ms is not None:
        lines[0] += f" ({result.latency_ms}ms)"

    if result.fix_command:
        lines.append(f"   Fix: {result.fix_command}")

    return "\n".join(lines)


def main():
    """Run diagnostics and display results."""
    print("=" * 70)
    print("Wateen Environment Diagnostics")
    print("=" * 70)
    print()

    results = run_all_checks()

    for result in results:
        print(format_result(result))
        print()

    passed = sum(1 for r in results if r.status == PASS)
    failed = sum(1 for r in results if r.status == FAIL)
    warnings = sum(1 for r in results if r.status == WARNING)

    print("-" * 70)
    print(f"Summary: {passed} passed, {failed} failed, {warnings} warning(s)")
    print("-" * 70)

    if failed > 0:
        sys.exit(1)
    elif warnings > 0:
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
