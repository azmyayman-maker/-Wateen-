# Research: Infrastructure Resilience Upgrade

**Date**: 2026-02-18
**Feature**: 001-redis-resilience

## Research Tasks

### 1. Redis Fallback Strategy

**Question**: How should the system handle Redis unavailability?

**Decision**: Implement a hybrid strategy with health-check-based fallback.

**Rationale**:
- Developers frequently work offline or without local Redis
- Production environments must fail fast when Redis is unavailable
- Django provides built-in `LocMemCache` suitable for single-process development
- Django Channels provides `InMemoryChannelLayer` for development WebSockets

**Implementation Approach**:
1. Check `REDIS_URL` environment variable
2. If set, attempt connection with 1-second timeout ping
3. If ping succeeds: use Redis backends
4. If ping fails or URL not set:
   - If `DEBUG=True`: use in-memory backends + log warning
   - If `DEBUG=False`: raise `ImproperlyConfigured`

**Alternatives Considered**:
- **DummyCache**: Rejected - silently breaks caching behavior
- **FileBasedCache**: Rejected - adds filesystem complexity
- **Always require Redis**: Rejected - poor developer experience

### 2. GDAL Detection on Windows

**Question**: How to handle missing GDAL on Windows without crashing?

**Decision**: Proactive detection with actionable error messaging.

**Rationale**:
- GDAL is a native library dependency for `django.contrib.gis`
- Windows lacks package manager for native libraries
- Common installation via OSGeo4W in predictable paths
- Cannot easily disable GIS if models depend on it

**Implementation Approach**:
1. Check if `os.name == 'nt'` (Windows)
2. Check if `GDAL_LIBRARY_PATH` already set
3. If not, scan common OSGeo4W installation paths:
   - `C:\OSGeo4W\bin\gdal304.dll`
   - `C:\Program Files\QGIS 3.*\bin\gdal304.dll`
   - `C:\Program Files (x86)\OSGeo4W\bin\gdal304.dll`
4. If found: set `GDAL_LIBRARY_PATH` automatically
5. If not found: log prominent warning with fix instructions

**Alternatives Considered**:
- **Disable GIS entirely**: Rejected - models depend on GeoDjango fields
- **Silent failure**: Rejected - confusing stack traces for developers
- **Require GDAL in requirements.txt**: Rejected - can't pip install native Windows libraries

### 3. Diagnostic Script Design

**Question**: What checks should the doctor script perform?

**Decision**: Comprehensive environment validation with actionable output.

**Checks**:
1. **Python Version**: Verify 3.11+
2. **Environment File**: Check `.env` exists and contains required keys
3. **Redis Connectivity**: Ping `REDIS_URL`, report latency
4. **Database Connectivity**: Test `DATABASE_URL` connection
5. **GDAL Availability**: Import test for `osgeo.gdal`

**Output Format**:
```
Wateen Environment Diagnostics
==============================

✅ Python Version: 3.11.5 (Required: 3.11+)
✅ Environment File: .env found
❌ Redis Connectivity: Connection refused
   Fix: Set REDIS_URL or start local Redis server
✅ Database Connectivity: Connected (12ms latency)
⚠️  GDAL: Not found
   Fix: Install OSGeo4W or run: python scripts/doctor.py --fix-gdal

Summary: 3 passed, 1 failed, 1 warning
```

**Alternatives Considered**:
- **Django management command**: Rejected - requires settings to load first
- **Shell script**: Rejected - cross-platform compatibility issues

### 4. Security Considerations

**Question**: How to log connection status without exposing credentials?

**Decision**: Sanitize URLs before logging.

**Implementation**:
```python
def sanitize_redis_url(url: str) -> str:
    """Remove password from Redis URL for safe logging."""
    # redis://:password@host:port/db -> redis://***@host:port/db
    import re
    return re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', url)
```

**Applied to**:
- Startup logs
- Diagnostic output
- Error messages

## Resolved Clarifications

All technical decisions made. No NEEDS CLARIFICATION markers remain.
