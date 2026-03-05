# Tasks: Phase 1 QA, Security & Validation

**Input**: Design documents from `/specs/011-phase1-qa-security/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: This entire ticket IS a test-writing ticket. All tasks produce test code or validation evidence.

**Organization**: Tasks are grouped by user story. Each story produces an independently runnable test file.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure test environment and conftest fixtures are ready

- [ ] T001 Verify `visits/tests/conftest.py` has CustomUserFactory, AgencyProfileFactory, NurseProfileFactory fixtures
- [ ] T002 [P] Ensure `users/tests/__init__.py` exists for test discovery in `users/tests/`

**Checkpoint**: Test infrastructure confirmed — test file authoring can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational work needed — existing factories, models, and permission classes are already in place from Phase 1 implementation tickets

**⚠️ SKIP**: All foundational code (models, permissions, serializers) exists. This ticket only writes tests and validation.

---

## Phase 3: User Story 1 — B2B2C Database Integrity (Priority: P1) 🎯 MVP

**Goal**: Validate that PostgreSQL enforces mandatory NurseProfile→AgencyProfile FK and PostGIS rejects invalid polygons

**Independent Test**: `pytest users/tests/test_b2b2c_integrity.py -v`

### Implementation

- [ ] T003 [US1] Write `TestNurseAgencyFKIntegrity` class in `users/tests/test_b2b2c_integrity.py`:
  - Test creating NurseProfile with `agency=None` via `objects.create()` (bypassing `full_clean`), assert `IntegrityError`
  - Test creating NurseProfile with `agency=None` via `save()`, assert `ValidationError` (ORM-level `clean()`)
  - Test that valid NurseProfile with agency succeeds
- [ ] T004 [US1] Write `TestGeospatialIntegrity` class in `users/tests/test_b2b2c_integrity.py`:
  - Test creating AgencyProfile with invalid polygon (LinearRing < 4 points), assert `GEOSException`
  - Test creating AgencyProfile with self-intersecting polygon, assert error
  - Test that valid polygon (closed ring, SRID 4326) succeeds

**Checkpoint**: DB-level B2B2C enforcement is proven — nurses cannot be freelancers, invalid polygons rejected

---

## Phase 4: User Story 2 — Migration Safety & CI Readiness (Priority: P1)

**Goal**: Verify migration graph integrity — no pending, conflicting, or data-losing migrations

**Independent Test**: `pytest users/tests/test_migrations.py -v` + `python manage.py migrate --check`

### Implementation

- [ ] T005 [P] [US2] Write `TestMigrationSafety` class in `users/tests/test_migrations.py`:
  - Test `call_command('migrate', '--check')` exits without error (no unapplied migrations)
  - Test `call_command('showmigrations', '--plan')` completes (no merge conflicts)
  - Test `call_command('makemigrations', '--check', '--dry-run')` confirms no missing migrations
- [ ] T006 [US2] Run `python manage.py migrate --check` locally and capture output for QA evidence

**Checkpoint**: Migration graph is CI-ready — safe to deploy

---

## Phase 5: User Story 3 — RBAC Security & Authorization (Priority: P1)

**Goal**: Prove cross-role breach returns 403; financial fields are tamper-proof

**Independent Test**: `pytest visits/tests/test_security_rbac.py users/tests/test_permissions.py -v`

### Implementation

- [ ] T007 [P] [US3] Write `TestPermissionClasses` in `users/tests/test_permissions.py`:
  - Unit test `IsSuperAdmin.has_permission()` with each role — only SUPERADMIN passes
  - Unit test `IsAgencyAdmin.has_permission()` — only verified AGENCY_ADMIN passes
  - Unit test `IsAgencyAdminOrSuperAdmin.has_permission()` — both pass, others fail
  - Unit test `IsNurseOrAbove.has_permission()` — NURSE, AGENCY_ADMIN, SUPERADMIN pass; PATIENT fails
  - Unit test `IsOwnerOrAdmin.has_object_permission()` — owner and SUPERADMIN pass
- [ ] T008 [P] [US3] Write `TestCrossRoleBreach` in `visits/tests/test_security_rbac.py`:
  - Authenticate as NURSE (JWT), POST to `/api/v1/users/agency/invite-nurse/`, assert 403
  - Authenticate as PATIENT (JWT), POST to `/api/v1/visits/agency/{id}/dispatch/manual/`, assert 403
  - Authenticate as PATIENT, attempt PATCH Visit financial fields, assert ignored/403
- [ ] T009 [US3] Write `TestFinancialTampering` in `visits/tests/test_security_rbac.py`:
  - Authenticate as PATIENT, send PATCH with `base_price` and `final_price` modifications
  - Assert the serializer ignores read-only fields or endpoint returns 400/403

**Checkpoint**: RBAC proven — no cross-role escalation, financial fields immutable from client

---

## Phase 6: User Story 4 — Static Analysis & Type Safety (Priority: P2)

**Goal**: Zero `ruff` errors across codebase, best-effort `mypy` compliance in `users/` and `visits/`

**Independent Test**: `ruff check .` exit code 0

### Implementation

- [ ] T010 [US4] Run `ruff check .` and capture all warnings/errors
- [ ] T011 [US4] Fix all `ruff` issues across `users/` and `visits/` modules
- [ ] T012 [P] [US4] Run `mypy users/ visits/ --ignore-missing-imports` and fix critical annotations
- [ ] T013 [US4] Re-run `ruff check .` to confirm zero errors and capture clean output for evidence

**Checkpoint**: Codebase passes static analysis — CI lint gate will pass

---

## Phase 7: User Story 5 — Engineering QA Report (Priority: P2)

**Goal**: Produce comprehensive sign-off report for Phase 1

**Independent Test**: Verify `specs/011-phase1-qa-security/report.md` exists with all 5 sections

### Implementation

- [ ] T014 [US5] Run full test suite (`pytest -v`) and capture raw output
- [ ] T015 [US5] Capture `ruff check .` and `mypy` outputs
- [ ] T016 [US5] Generate `specs/011-phase1-qa-security/report.md` with 5 sections:
  1. Executive Summary (Phase 1 context and completion status)
  2. Threat Model & Security Mitigation (IDOR, Role-Escalation testing approach)
  3. Geospatial & DB Algorithms (PostGIS constraints, mandatory FK explanation)
  4. QA Evidence (raw pytest, ruff, mypy output)
  5. Staff-Engineer Sign-off (formal Phase 1 seal)

**Checkpoint**: Phase 1 formally sealed — report serves as gate for Phase 2 commencement

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — verify fixtures exist
- **Foundational (Phase 2)**: Skipped — all code exists
- **US1 DB Integrity (Phase 3)**: Depends on Phase 1 setup only
- **US2 Migrations (Phase 4)**: Depends on Phase 1 setup only — **parallel with US1**
- **US3 RBAC Security (Phase 5)**: Depends on Phase 1 setup only — **parallel with US1, US2**
- **US4 Static Analysis (Phase 6)**: Independent — **parallel with US1-US3**
- **US5 QA Report (Phase 7)**: Depends on ALL previous phases (needs test evidence)

### User Story Dependencies

- **US1 (P1)**: Independent — no cross-story dependencies
- **US2 (P1)**: Independent — no cross-story dependencies
- **US3 (P1)**: Independent — no cross-story dependencies
- **US4 (P2)**: Independent — may fix files touched by US1-US3
- **US5 (P2)**: Depends on US1-US4 completion (aggregates evidence)

### Parallel Opportunities

- **T003 + T004**: Both in same file but different classes — sequential within US1
- **T005 + T007 + T008**: Different files, all [P] — run in parallel
- **T010 + T012**: ruff and mypy are independent tools — parallel
- **US1, US2, US3**: All test-writing tasks can proceed in parallel (different files)

---

## Parallel Example: Phase 3-5 Concurrent Start

```text
# After Phase 1 (Setup), launch all P1 stories in parallel:
T003 → users/tests/test_b2b2c_integrity.py (US1)
T005 → users/tests/test_migrations.py (US2)
T007 → users/tests/test_permissions.py (US3)
T008 → visits/tests/test_security_rbac.py (US3)
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3)

1. Complete Phase 1: Setup (T001-T002)
2. Write all P1 test files in parallel (T003-T009)
3. **VALIDATE**: Run all tests, confirm PASS
4. Proceed to Static Analysis (T010-T013)
5. Generate Report (T014-T016)

### Sequential Single-Developer

1. T001-T002 (Setup) → 2 min
2. T003-T004 (US1: DB Integrity) → 15 min
3. T005-T006 (US2: Migrations) → 10 min
4. T007-T009 (US3: RBAC Security) → 20 min
5. T010-T013 (US4: Static Analysis) → 15 min
6. T014-T016 (US5: Report) → 10 min

---

## Notes

- All tasks produce test code or validation evidence — no production code changes (except ruff/mypy fixes)
- Each test file is independently runnable with `pytest <path> -v`
- Commit after each phase checkpoint
- US5 (Report) MUST be last — it aggregates all evidence from prior phases
