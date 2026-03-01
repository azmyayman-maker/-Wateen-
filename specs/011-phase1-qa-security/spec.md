# Feature Specification: Phase 1 QA, Security & Validation

**Feature Branch**: `011-phase1-qa-security`  
**Created**: 2026-03-01  
**Status**: Draft  
**Input**: Ticket P1-T5 — Professional QA, Security & Validation (Phase 1 Final Gate)

## User Scenarios & Testing

### User Story 1 — B2B2C Database Integrity Enforcement (Priority: P1)

As a **Staff QA Engineer**, I need to validate that the database enforces the B2B2C model rules at the schema level — specifically that nurses cannot exist without an agency (no freelancers) and that geospatial polygons are validated before storage.

**Why this priority**: Database integrity is the foundation. If the mandatory FK (`NurseProfile.agency`) or PostGIS constraints fail, the entire B2B2C business model collapses.

**Independent Test**: Run `pytest users/tests/test_b2b2c_integrity.py -v` and verify all assertions pass.

**Acceptance Scenarios**:

1. **Given** a valid agency exists, **When** a NurseProfile is created with `agency=None` at the ORM level, **Then** the system raises `IntegrityError` or `ValidationError`.
2. **Given** a PostGIS-enabled database, **When** an AgencyProfile is created with an invalid polygon (unclosed ring / missing SRID), **Then** the system raises a `GEOSException` or `IntegrityError`.

---

### User Story 2 — Migration Safety & CI Readiness (Priority: P1)

As a **DevOps Engineer**, I need to ensure no pending or conflicting migrations exist and the entire migration graph can be applied cleanly.

**Why this priority**: Broken migrations block CI pipelines and can cause data loss on deployment.

**Independent Test**: Run `python manage.py migrate --check` and `pytest users/tests/test_migrations.py -v`.

**Acceptance Scenarios**:

1. **Given** the current migration graph, **When** `migrate --check` is run, **Then** it exits with code 0 (no unapplied migrations).
2. **Given** a clean database, **When** all migrations are applied sequentially, **Then** no errors occur and no data is lost.

---

### User Story 3 — RBAC Security & Cross-Role Breach Prevention (Priority: P1)

As a **Security Engineer**, I need to verify that RBAC permission classes correctly reject unauthorized access — cross-role breaches and financial tampering must return 403.

**Why this priority**: Authorization bypass is a critical security vulnerability in B2B2C systems.

**Independent Test**: Run `pytest visits/tests/test_security_rbac.py users/tests/test_permissions.py -v`.

**Acceptance Scenarios**:

1. **Given** a user with role NURSE, **When** they attempt to hit the `POST /api/v1/users/agency/invite-nurse/` endpoint (AGENCY_ADMIN only), **Then** the response is `403 Forbidden`.
2. **Given** a user with role PATIENT, **When** they `PATCH` a Visit to modify `base_price` or `final_price`, **Then** the serializer ignores these read-only fields or returns `400/403`.

---

### User Story 4 — Static Analysis & Type Safety (Priority: P2)

As an **Engineering Lead**, I need full `ruff` and `mypy` compliance across the Python codebase to ensure code quality standards before Phase 2.

**Why this priority**: Lint and type errors compound over time and block CI gates.

**Independent Test**: Run `ruff check .` and `mypy .` with zero errors.

**Acceptance Scenarios**:

1. **Given** the full codebase, **When** `ruff check .` is run, **Then** it exits with zero warnings.
2. **Given** the full codebase, **When** `mypy .` is run, **Then** it exits with zero errors.

---

### User Story 5 — Engineering QA Report (Priority: P2)

As a **Staff Engineer**, I need a comprehensive markdown report documenting the Phase 1 QA sign-off including threat model, geospatial/DB algorithm explanations, and raw test evidence.

**Why this priority**: Without formal sign-off documentation, Phase 2 cannot begin.

**Independent Test**: Verify `specs/011-phase1-qa-security/report.md` exists and contains all required sections.

**Acceptance Scenarios**:

1. **Given** all tests and checks pass, **When** the report is generated, **Then** it contains: Executive Summary, Threat Model, Geospatial/DB Algorithms, QA Evidence, and Staff-Engineer Sign-off.

---

### Edge Cases

- What happens when a nurse is created via raw SQL bypassing Django ORM validation? (DB FK constraint still catches it)
- How does the system handle a user whose role changes from NURSE to PATIENT while they have an active NurseProfile?
- What if two parallel migrations create conflicting schema changes?

## Requirements

### Functional Requirements

- **FR-001**: The test suite MUST include a geospatial integrity test that creates an AgencyProfile with an invalid polygon and asserts a database/validation error.
- **FR-002**: The test suite MUST include a relational integrity test that creates a NurseProfile with `agency=None` and asserts `IntegrityError`.
- **FR-003**: A migration test MUST verify the full migration graph applies without errors.
- **FR-004**: Security tests MUST verify NURSE users receive 403 when calling AGENCY_ADMIN-only endpoints.
- **FR-005**: Security tests MUST verify PATIENT users cannot modify financial fields (`base_price`, `final_price`) on Visits.
- **FR-006**: `ruff check .` MUST pass with zero warnings across the codebase.
- **FR-007**: A comprehensive QA report MUST be generated at `specs/011-phase1-qa-security/report.md`.

### Key Entities

- **NurseProfile**: Must have non-null FK to AgencyProfile (enforced at DB level)
- **AgencyProfile**: `coverage_polygon` is a PostGIS PolygonField with GIST index (SRID=4326)
- **Visit**: `base_price` / `final_price` are read-only from client perspective
- **UserRole**: PATIENT | NURSE | AGENCY_ADMIN | SUPERADMIN — drives permission classes

## Success Criteria

### Measurable Outcomes

- **SC-001**: All pytest tests pass with zero failures (`pytest -v` exit code 0)
- **SC-002**: `python manage.py migrate --check` exits with code 0
- **SC-003**: `ruff check .` returns zero errors/warnings
- **SC-004**: Cross-role breach tests confirm 403 for every unauthorized endpoint access
- **SC-005**: A formal engineering report exists at `specs/011-phase1-qa-security/report.md` with all 5 required sections
