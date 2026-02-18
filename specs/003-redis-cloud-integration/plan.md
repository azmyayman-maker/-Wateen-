# Implementation Plan: Redis Cloud Integration

**Branch**: `003-redis-cloud-integration` | **Date**: 2026-02-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-redis-cloud-integration/spec.md`

## Summary

Integrate Redis Cloud into the Wateen Django project for caching and channel layers, replacing the local Redis container. The implementation involves updating Django settings to use Redis Cloud URL from environment variables, configuring connection pooling with 50 max connections, implementing graceful degradation for Redis unavailability, and updating Docker configuration to remove the local Redis service.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Django 5.2, Django REST Framework, django-redis 6.0.0, channels-redis 4.2.0, redis 5.0.1  
**Storage**: PostgreSQL with PostGIS (existing), Redis Cloud (new)  
**Testing**: pytest, pytest-django  
**Target Platform**: Linux server (Docker containers)
**Project Type**: Web application (backend API)  
**Performance Goals**: Cache operations < 100ms, WebSocket messages < 200ms, connection within 5 seconds  
**Constraints**: Connection pool max 50 connections per instance, graceful degradation required  
**Scale/Scope**: Healthcare application with real-time visit tracking and notifications

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Principle           | Status  | Notes                                                                                         |
| ------------------- | ------- | --------------------------------------------------------------------------------------------- |
| Test-First          | ✅ Pass | Tests will be written for connection verification, cache operations, and graceful degradation |
| Integration Testing | ✅ Pass | Integration tests for Redis Cloud connectivity and channel layers required                    |
| Observability       | ✅ Pass | Logging for connection status, degradation events, and errors                                 |
| Simplicity          | ✅ Pass | Minimal changes - only configuration updates and one management command                       |

## Project Structure

### Documentation (this feature)

```text
specs/003-redis-cloud-integration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal - no new entities)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - no new API endpoints)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
config/
├── settings.py          # Update CACHES and CHANNEL_LAYERS configuration
└── asgi.py              # No changes needed

docker/
├── docker-compose.yml   # Remove local Redis service, update environment
└── Dockerfile           # No changes needed

visits/
└── management/
    └── commands/
        └── test_redis.py  # New management command for connection verification

.env.example             # Update with REDIS_URL format
requirements/
└── base.txt             # Already has redis, django-redis, channels-redis

tests/
├── test_redis_cloud.py  # New integration tests
└── conftest.py          # Update fixtures if needed
```

**Structure Decision**: Existing web application structure maintained. Changes are primarily configuration updates in `config/settings.py` and `docker/docker-compose.yml`, plus one new management command.

## Complexity Tracking

> No constitution violations - this is a configuration change, not a new architectural pattern.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A       | N/A        | N/A                                  |

## Implementation Phases

### Phase 1: Configuration Updates

1. Update `config/settings.py`:
   - Read `REDIS_URL` from environment variable
   - Configure `CACHES` with Redis Cloud URL and connection pool (max 50 connections)
   - Configure `CHANNEL_LAYERS` with Redis Cloud URL
   - Add fallback configuration for graceful degradation

2. Update `docker/docker-compose.yml`:
   - Remove local Redis service
   - Remove Redis volume
   - Update web service environment to include `REDIS_URL`
   - Remove Redis dependency from web service

3. Update `.env.example`:
   - Add `REDIS_URL` format example

### Phase 2: Management Command

Create `visits/management/commands/test_redis.py`:

- Test connection to Redis Cloud
- Test cache read/write operations
- Test channel layer functionality
- Output "Redis Connected Successfully" on success
- Exit with appropriate code and error message on failure

### Phase 3: Graceful Degradation

Implement fallback behavior:

- Cache operations fall back to database queries on Redis failure
- WebSocket features disabled with user notification
- Logging for all degradation events

### Phase 4: Testing

1. Unit tests for management command
2. Integration tests for Redis Cloud connectivity
3. Tests for graceful degradation behavior
4. Tests for connection pool limits

## Risk Assessment

| Risk                            | Impact | Mitigation                                     |
| ------------------------------- | ------ | ---------------------------------------------- |
| Redis Cloud credentials exposed | High   | Use environment variables, never commit .env   |
| Connection timeout on startup   | Medium | Implement retry logic with exponential backoff |
| Connection pool exhaustion      | Medium | Set max connections to 50, monitor usage       |
| Network latency to Redis Cloud  | Low    | Redis Cloud regions chosen for low latency     |
