# Data Model: Infrastructure Resilience Upgrade

**Date**: 2026-02-18
**Feature**: 001-redis-resilience

## Overview

This feature does not introduce new database models. It configures runtime behavior for caching, channels, and geospatial support. The "data model" here represents configuration states and diagnostic results.

## Entities

### 1. Redis Connection Status

Represents the current state of Redis connectivity at application startup.

| Attribute | Type | Description |
|-----------|------|-------------|
| `url_configured` | boolean | Whether REDIS_URL env var is set |
| `url_sanitized` | string | URL with password masked (for logging) |
| `is_connected` | boolean | Result of connectivity ping |
| `latency_ms` | integer | Ping latency in milliseconds (null if failed) |
| `backend_type` | enum | `redis` or `locmem` |
| `fallback_reason` | string | Why fallback activated (null if using Redis) |

**State Transitions**:
```
[No URL] → Check DEBUG → [LocMem if DEBUG=True, Error if DEBUG=False]
[URL Set] → Ping → [Redis if success, LocMem/Error if fail]
```

### 2. Environment Check Result

Represents a single diagnostic check performed by the doctor script.

| Attribute | Type | Description |
|-----------|------|-------------|
| `check_name` | string | Name of the check (e.g., "Redis Connectivity") |
| `status` | enum | `pass`, `fail`, `warning` |
| `message` | string | Human-readable result description |
| `fix_command` | string | Command or instruction to resolve failure |
| `latency_ms` | integer | Latency for connectivity checks (optional) |

**Checks Performed**:
1. Python Version
2. Environment File
3. Redis Connectivity
4. Database Connectivity
5. GDAL Availability

### 3. GDAL Configuration

Represents GDAL library detection and configuration state.

| Attribute | Type | Description |
|-----------|------|-------------|
| `platform` | string | Operating system (windows, linux, darwin) |
| `library_path` | string | Detected or configured GDAL path |
| `detection_source` | enum | `env_var`, `auto_detect`, `not_found` |
| `is_available` | boolean | Whether GDAL can be imported |
| `warning_displayed` | boolean | Whether missing GDAL warning was shown |

**Detection Priority**:
1. `GDAL_LIBRARY_PATH` environment variable
2. Common OSGeo4W paths (Windows only)
3. System library paths (Linux/macOS)
4. Mark as not found

## Relationships

```
Redis Connection Status ─────┐
                             │
                             ▼
                    Application Startup
                             ▲
                             │
GDAL Configuration ──────────┘

Environment Check Result (1..N) ─── Doctor Script Output
```

## Validation Rules

### Redis Configuration
- If `DEBUG=False` and `is_connected=False` and `url_configured=True`: Application MUST fail to start
- If `DEBUG=False` and `url_configured=False`: Application MUST fail to start
- `url_sanitized` MUST NOT contain password substring

### GDAL Configuration
- If `platform=windows` and `is_available=False`: Warning MUST be displayed
- Warning MUST include reference to `scripts/doctor.py`

### Diagnostic Checks
- Each check MUST have a `fix_command` if `status=fail`
- `latency_ms` MUST be present for connectivity checks
