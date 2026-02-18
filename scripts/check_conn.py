#!/usr/bin/env python
"""
Network Connectivity Verification Script

Verifies DNS resolution and port access for Redis and Postgres hosts.
This script performs raw socket connections to verify network connectivity
before the application attempts to use these services.

Usage:
    python scripts/check_conn.py
"""

import os
import socket
import sys
from urllib.parse import urlparse


def mask_password_from_url(url: str) -> str:
    """Safely mask password in a URL using urllib.parse."""
    try:
        parsed = urlparse(url)
        if parsed.password:
            # Replace password with asterisks
            netloc = parsed.netloc
            if parsed.username and parsed.password:
                # Reconstruct netloc with masked password
                masked_netloc = netloc.replace(parsed.password, "*****", 1)
                # Reconstruct URL with masked netloc
                masked_url = parsed._replace(netloc=masked_netloc).geturl()
                return masked_url
        return url
    except Exception:
        # Fallback: return URL without exposing sensitive parts
        return "[URL masked due to parsing error]"


def parse_redis_url(url: str) -> tuple[str, int]:
    """Extract host and port from Redis URL."""
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    return host, port


def parse_postgres_url(url: str) -> tuple[str, int]:
    """Extract host and port from PostgreSQL URL."""
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    return host, port


def check_socket_connection(host: str, port: int, timeout: float = 5.0) -> tuple[bool, str]:
    """
    Attempt a raw socket connection to verify network connectivity.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            return True, f"[OK] Connection successful to {host}:{port}"
        else:
            return False, f"[FAIL] Connection failed to {host}:{port} (error code: {result})"
    except socket.gaierror as e:
        return False, f"[FAIL] DNS resolution failed for {host}: {e}"
    except socket.timeout:
        return False, f"[FAIL] Connection timed out to {host}:{port}"
    except OSError as e:
        return False, f"[FAIL] Network error for {host}:{port}: {e}"


def check_dns_resolution(host: str) -> tuple[bool, str]:
    """Verify DNS resolution for a hostname."""
    try:
        ip = socket.gethostbyname(host)
        return True, f"[OK] DNS resolved {host} -> {ip}"
    except socket.gaierror as e:
        return False, f"[FAIL] DNS resolution failed for {host}: {e}"


def main():
    """Run connectivity checks for all configured services."""
    print("=" * 60)
    print("Network Connectivity Verification")
    print("=" * 60)
    print()

    # Load environment variables
    from decouple import config

    results = []

    # Check Redis
    print("[Redis Check]")
    redis_url = config("REDIS_URL", default="")
    if redis_url:
        try:
            host, port = parse_redis_url(redis_url)
            masked_url = mask_password_from_url(redis_url)
            print(f"  URL: {masked_url}")
            print(f"  Host: {host}, Port: {port}")

            # DNS check
            dns_ok, dns_msg = check_dns_resolution(host)
            print(f"  {dns_msg}")
            results.append(("Redis DNS", dns_ok))

            # Socket check
            conn_ok, conn_msg = check_socket_connection(host, port)
            print(f"  {conn_msg}")
            results.append(("Redis Connection", conn_ok))
        except Exception as e:
            print(f"  [FAIL] Error parsing Redis URL: {e}")
            results.append(("Redis", False))
    else:
        print("  [WARN] REDIS_URL not configured (will use in-memory fallback)")
        results.append(("Redis", True))  # Not an error if not configured
    print()

    # Check PostgreSQL/Neon
    print("[PostgreSQL/Neon Check]")
    database_url = config("DATABASE_URL", default="")
    if database_url:
        try:
            # Handle both postgres:// and postgresql:// schemes
            normalized_url = database_url.replace("postgresql://", "postgres://")
            host, port = parse_postgres_url(normalized_url)
            # Safely mask password using urllib.parse
            masked_url = mask_password_from_url(database_url)
            print(f"  URL: {masked_url}")
            print(f"  Host: {host}, Port: {port}")

            # DNS check
            dns_ok, dns_msg = check_dns_resolution(host)
            print(f"  {dns_msg}")
            results.append(("PostgreSQL DNS", dns_ok))

            # Socket check
            conn_ok, conn_msg = check_socket_connection(host, port, timeout=10.0)
            print(f"  {conn_msg}")
            results.append(("PostgreSQL Connection", conn_ok))
        except Exception as e:
            print(f"  [FAIL] Error parsing DATABASE_URL: {e}")
            results.append(("PostgreSQL", False))
    else:
        print("  [FAIL] DATABASE_URL not configured")
        results.append(("PostgreSQL", False))
    print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"  Passed: {passed}/{total}")

    for name, ok in results:
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {name}")

    print()

    if passed == total:
        print("[OK] All connectivity checks passed!")
        return 0
    else:
        print("[FAIL] Some connectivity checks failed. Please verify:")
        print("  1. Network connectivity (internet access)")
        print("  2. Firewall rules allow outbound connections")
        print("  3. Service credentials are correct")
        print("  4. Service instances are running (Redis Cloud, Neon)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
