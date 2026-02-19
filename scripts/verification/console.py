"""
Console Output Formatter

Formats verification results for console output with status indicators.
"""

from typing import Optional
from .models import (
    VerificationResult,
    VerificationStatus,
    DatabaseVerificationResult,
    CacheVerificationResult,
)


ICONS = {
    VerificationStatus.PASS: "✓",
    VerificationStatus.FAIL: "✗",
    VerificationStatus.WARNING: "⚠",
}

COLORS = {
    VerificationStatus.PASS: "\033[92m",
    VerificationStatus.FAIL: "\033[91m",
    VerificationStatus.WARNING: "\033[93m",
    "reset": "\033[0m",
    "dim": "\033[90m",
    "bold": "\033[1m",
}


def colorize(text: str, color: str) -> str:
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def format_status(status: VerificationStatus) -> str:
    icon = ICONS.get(status, "?")
    color = COLORS.get(status, "")
    return f"{color}{icon}{COLORS['reset']}"


def print_header(title: str) -> None:
    line = "─" * 30
    print(f"{COLORS['dim']}{line}{COLORS['reset']}")
    print(f"{COLORS['bold']}{title}{COLORS['reset']}")
    print(f"{COLORS['dim']}{line}{COLORS['reset']}")


def print_footer(
    status: VerificationStatus, duration_ms: float, json_path: Optional[str] = None
) -> None:
    line = "─" * 30
    status_str = format_status(status)
    status_text = status.value.upper()

    print(f"{COLORS['dim']}{line}{COLORS['reset']}")
    print(f"Overall: {status_str} {status_text} ({duration_ms:.0f}ms)")
    if json_path:
        print(f"Report: {json_path}")


def print_database_result(result: DatabaseVerificationResult) -> None:
    status = format_status(result.status)
    print(
        f"[{status}] Database: {result.status.value.upper()} ({result.latency_ms:.0f}ms)"
    )

    if result.postgis_version:
        print(f"    PostGIS: {result.postgis_version}")

    if result.crud_status:
        crud = result.crud_status
        c = "✓" if crud.create else "✗"
        r = "✓" if crud.read else "✗"
        u = "✓" if crud.update else "✗"
        d = "✓" if crud.delete else "✗"
        print(f"    CRUD: create {c} read {r} update {u} delete {d}")
        if crud.error:
            print(f"    {COLORS[VerificationStatus.FAIL]}CRUD Error: {crud.error}{COLORS['reset']}")

    if result.error:
        print(f"    {COLORS[VerificationStatus.FAIL]}{result.error}{COLORS['reset']}")


def print_cache_result(result: CacheVerificationResult) -> None:
    status = format_status(result.status)
    print(
        f"[{status}] Cache: {result.status.value.upper()} ({result.latency_ms:.0f}ms)"
    )

    if result.operations:
        ops = result.operations
        s = "✓" if ops.set else "✗"
        g = "✓" if ops.get else "✗"
        d = "✓" if ops.delete else "✗"
        print(f"    Operations: set {s} get {g} delete {d}")
        if ops.error:
            print(f"    {COLORS[VerificationStatus.FAIL]}Operations Error: {ops.error}{COLORS['reset']}")

    if result.pubsub_status:
        ps = result.pubsub_status
        sub = "✓" if ps.subscribe else "✗"
        pub = "✓" if ps.publish else "✗"
        rec = "✓" if ps.receive else "✗"
        print(f"    Pub/Sub: subscribe {sub} publish {pub} receive {rec}")
        if ps.error:
            print(f"    {COLORS[VerificationStatus.FAIL]}PubSub Error: {ps.error}{COLORS['reset']}")

    if result.error:
        print(f"    {COLORS[VerificationStatus.FAIL]}{result.error}{COLORS['reset']}")


def print_result(result: VerificationResult) -> None:
    if isinstance(result, DatabaseVerificationResult):
        print_database_result(result)
    elif isinstance(result, CacheVerificationResult):
        print_cache_result(result)
    else:
        status = format_status(result.status)
        print(
            f"[{status}] {result.component}: {result.status.value.upper()} ({result.latency_ms:.0f}ms)"
        )
        if result.error:
            print(
                f"    {COLORS[VerificationStatus.FAIL]}{result.error}{COLORS['reset']}"
            )
