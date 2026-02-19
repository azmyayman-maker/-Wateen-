# Research: Infrastructure Verification

**Feature**: 005-infra-verification  
**Date**: 2026-02-19

## Research Tasks

### 1. JSON Report Format for CI/CD Integration

**Decision**: Use a structured JSON format with component-level results, timing, and overall status.

**Rationale**: 
- Machine-readable for CI/CD pipelines
- Can be parsed by tools like `jq` for selective checks
- Supports both human-readable console output and structured file output

**Alternatives Considered**:
- JUnit XML: Too test-framework specific
- YAML: Less common for programmatic parsing
- Plain text: Not machine-readable

**Schema** (see `contracts/verification-report.json`):
```json
{
  "timestamp": "2026-02-19T10:30:00Z",
  "overall_status": "pass|fail",
  "components": {
    "database": { "status": "pass", "latency_ms": 15, "details": "..." },
    "cache": { "status": "pass", "latency_ms": 2, "details": "..." }
  }
}
```

### 2. Connection Timeout Implementation

**Decision**: Use 5-second timeout for both database and Redis connections.

**Rationale**:
- Fast enough to fail quickly in CI/CD
- Allows for container startup delays in local Docker
- Standard practice for health check timeouts

**Implementation**: 
- Database: Django `CONN_MAX_AGE` and connection health checks
- Redis: `socket_timeout` and `socket_connect_timeout` parameters

### 3. Latency Threshold Validation

**Decision**: 100ms threshold for cache operations, warn but pass if under 200ms.

**Rationale**:
- Local Docker localhost connections should be fast
- 100ms is reasonable for local development
- Soft failure (warning) prevents false negatives from minor network variations

### 4. Exit Code Strategy

**Decision**: Exit code 0 for pass, 1 for any failure.

**Rationale**:
- Standard POSIX convention
- CI/CD systems expect this pattern
- Simple and predictable

### 5. Environment Variable Configuration

**Decision**: Support standard environment variables for connection configuration.

**Variables**:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `VERIFICATION_TIMEOUT`: Override default 5-second timeout
- `VERIFICATION_OUTPUT`: Output format (console, json, both)

**Rationale**:
- Follows 12-factor app principles
- Compatible with existing project configuration
- No hardcoded credentials in scripts

### 6. Existing Script Enhancement Strategy

**Decision**: Enhance existing scripts in-place rather than create new ones.

**Rationale**:
- Scripts already functional
- Avoid duplication
- Maintain backward compatibility for console output

**Changes Required**:
- `verify_local_db.py`: Add JSON output, timeout, exit codes
- `verify_local_redis.py`: Add JSON output, timeout, latency threshold
- New `verify_infra.py`: Comprehensive runner combining both
