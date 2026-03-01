# Implementation Plan: Phase 1 QA, Security & Validation

**Branch**: `011-phase1-qa-security` | **Date**: 2026-03-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-phase1-qa-security/spec.md`

## Summary

Final gate before Phase 2. Write exhaustive Pytest suites validating B2B2C database integrity (mandatory agency FK, PostGIS polygon validation), migration graph safety, and RBAC authorization (cross-role breach, financial tampering). Run `ruff` and `mypy` static analysis. Produce a comprehensive engineering QA report with threat model, algorithm explanations, and raw evidence.

## Technical Context

**Language/Version**: Python 3.11, Django 5.2, DRF
**Primary Dependencies**: django.contrib.gis (PostGIS), rest_framework, rest_framework_simplejwt, factory_boy, pytest-django
**Storage**: PostgreSQL 16 + PostGIS 3.4 (SRID 4326)
**Testing**: pytest + pytest-django + factory_boy
**Target Platform**: Linux/Docker (dev: Windows with OSGeo4W for GDAL)
**Project Type**: web-service (Django REST Framework)
**Performance Goals**: N/A — QA validation ticket (pass/fail)
**Constraints**: Tests must run against real PostGIS DB (transactional fixtures)
**Scale/Scope**: ~15 new test cases across 4 test files

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Constitution file is a placeholder template — no project-specific gates defined.
All work aligns with `AGENTS.md` rules:

- ✅ B2B2C enforcement (testing mandatory agency FK)
- ✅ No float for money (Decimal usage verified)
- ✅ State machine transitions via `transition_to()` only
- ✅ Test coverage target ≥ 80%

## Project Structure

### Documentation (this feature)

```text
specs/011-phase1-qa-security/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Technical research
├── data-model.md        # Phase 1: Entities under test
├── quickstart.md        # Phase 1: How to run
└── report.md            # Task 5: Final engineering report (generated during execution)
```

### Source Code (repository root)

```text
users/
├── tests/
│   ├── test_b2b2c_integrity.py    # [NEW] Task 1: Geospatial + relational tests
│   ├── test_migrations.py         # [NEW] Task 2: Migration graph safety
│   └── test_permissions.py        # [NEW] Task 3: Permission class unit tests
├── models.py                      # [READ] NurseProfile, AgencyProfile constraints
└── permissions.py                 # [READ] 5 RBAC permission classes

visits/
├── tests/
│   └── test_security_rbac.py      # [NEW] Task 3: Cross-role breach + financial tampering
├── serializers.py                 # [READ] Visit field read-only enforcement
└── dispatch_views.py              # [READ] ManualDispatchView permission guard
```

**Structure Decision**: All new files are test modules placed within existing Django app `tests/` directories. No new packages or structural changes required.

## Complexity Tracking

No constitution violations. No complexity justification needed.
