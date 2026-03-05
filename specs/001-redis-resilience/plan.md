# Implementation Plan: Infrastructure Resilience Upgrade

**Branch**: `001-redis-resilience` | **Date**: 2026-02-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-redis-resilience/spec.md`

## Summary

Make the Django application self-healing by implementing hybrid Redis configuration (cloud with in-memory fallback for dev), graceful GDAL handling for Windows, and a diagnostic doctor script. The system prioritizes cloud Redis when available, gracefully degrades to in-memory caching in development, and fails fast in production when Redis is required but unavailable.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Django 5.2, Django REST Framework, django-redis, channels_redis, django.contrib.gis (PostGIS)  
**Storage**: PostgreSQL with PostGIS extension  
**Testing**: pytest, ruff (linting)  
**Target Platform**: Linux server (production), Windows/macOS/Linux (development)  
**Project Type**: web (Django monolith with ASGI)  
**Performance Goals**: App startup <10s, Redis ping <1s timeout, diagnostics <30s  
**Constraints**: In-memory fallback ONLY when DEBUG=True, no credentials in logs  
**Scale/Scope**: Single Django application with WebSocket support via Django Channels

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution template is not populated with project-specific rules. Proceeding with standard best practices:

- [x] Feature has clear purpose (developer experience improvement)
- [x] No unnecessary complexity added
- [x] Backward compatible with existing Redis configuration
- [x] Tests will verify both fallback paths and production safety

## Project Structure

### Documentation (this feature)

```text
specs/001-redis-resilience/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (minimal - internal configuration)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
config/
├── settings.py          # Modified: Smart Redis config + GDAL handling
└── asgi.py              # Unchanged

scripts/
└── doctor.py            # New: Diagnostic script

tests/
├── unit/
│   └── test_settings_resilience.py  # New: Unit tests for config logic
└── integration/
    └── test_redis_fallback.py       # New: Integration tests

.env.example             # Modified: Documented REDIS_URL format
```

**Structure Decision**: Single Django project structure. Changes are localized to `config/settings.py` (smart configuration), new `scripts/doctor.py` (diagnostics), and test files.

## Complexity Tracking

No violations. This feature simplifies the developer experience by removing hard dependencies on external services during development.
