# Tasks: Infrastructure Verification

**Input**: Design documents from `/specs/005-infra-verification/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Not explicitly requested in spec. Tasks focus on implementation of verification scripts.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `scripts/`, `tests/` at repository root
- Existing scripts have been enhanced in-place

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create shared verification infrastructure and models

- [x] T001 Create verification result models module in `scripts/verification/models.py`
- [x] T002 [P] Create JSON output formatter in `scripts/verification/output.py`
- [x] T003 [P] Create configuration loader for environment variables in `scripts/verification/config.py`

**Checkpoint**: ✅ Shared infrastructure ready for script enhancement

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities that all verification scripts depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create base verifier class with timeout and exit code handling in `scripts/verification/base.py`
- [x] T005 [P] Create console output formatter with status indicators in `scripts/verification/console.py`
- [x] T006 Create `scripts/verification/__init__.py` with public exports

**Checkpoint**: ✅ Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Verify Database Connectivity (Priority: P1) 🎯 MVP

**Goal**: Enhance database verification script with JSON output, timeout, and structured results

**Independent Test**: Run `python scripts/verify_local_db.py` and verify it outputs JSON report file with database status

### Implementation for User Story 1

- [x] T007 [US1] Create DatabaseVerificationResult class in `scripts/verification/models.py`
- [x] T008 [US1] Refactor `scripts/verify_local_db.py` to use base verifier class from `scripts/verification/base.py`
- [x] T009 [US1] Add 5-second connection timeout to database verification in `scripts/verify_local_db.py`
- [x] T010 [US1] Add JSON output generation matching schema in `scripts/verify_local_db.py`
- [x] T011 [US1] Add PostGIS version detection to structured output in `scripts/verify_local_db.py`
- [x] T012 [US1] Add CRUD status object to output in `scripts/verify_local_db.py`
- [x] T013 [US1] Implement non-zero exit code on failure in `scripts/verify_local_db.py`

**Checkpoint**: ✅ User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 - Verify Cache and Message Broker (Priority: P1)

**Goal**: Enhance cache verification script with JSON output, latency thresholds, and structured results

**Independent Test**: Run `python scripts/verify_local_redis.py` and verify it outputs JSON report file with cache status and latency metrics

### Implementation for User Story 2

- [x] T014 [US2] Create CacheVerificationResult class in `scripts/verification/models.py`
- [x] T015 [US2] Refactor `scripts/verify_local_redis.py` to use base verifier class from `scripts/verification/base.py`
- [x] T016 [US2] Add 5-second connection timeout to cache verification in `scripts/verify_local_redis.py`
- [x] T017 [US2] Add JSON output generation matching schema in `scripts/verify_local_redis.py`
- [x] T018 [US2] Implement 100ms latency threshold validation in `scripts/verify_local_redis.py`
- [x] T019 [US2] Add operations status object (set/get/delete) to output in `scripts/verify_local_redis.py`
- [x] T020 [US2] Add pubsub status object to output in `scripts/verify_local_redis.py`
- [x] T021 [US2] Implement non-zero exit code on failure in `scripts/verify_local_redis.py`

**Checkpoint**: ✅ User Stories 1 AND 2 both work independently

---

## Phase 5: User Story 3 - Run Comprehensive Infrastructure Test Suite (Priority: P2)

**Goal**: Create comprehensive runner that combines all verification checks with aggregated report

**Independent Test**: Run `python scripts/verify_infra.py` and verify it outputs combined JSON report with all component statuses

### Implementation for User Story 3

- [x] T022 [US3] Create InfrastructureTestReport class in `scripts/verification/models.py`
- [x] T023 [US3] Create comprehensive runner `scripts/verify_infra.py` that invokes both verifiers
- [x] T024 [US3] Implement aggregated JSON report generation in `scripts/verify_infra.py`
- [x] T025 [US3] Add total duration timing to report in `scripts/verify_infra.py`
- [x] T026 [US3] Implement summary output with all component statuses in `scripts/verify_infra.py`
- [x] T027 [US3] Add environment variable support for VERIFICATION_OUTPUT and VERIFICATION_JSON_PATH
- [x] T028 [US3] Implement non-zero exit code if any component fails in `scripts/verify_infra.py`

**Checkpoint**: ✅ All user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T029 [P] Create integration test `tests/integration/test_infra_full.py` for comprehensive suite
- [x] T030 [P] Update `tests/test_infra.py` to support JSON output mode
- [x] T031 Validate all scripts against quickstart.md examples
- [x] T032 Add docstrings to all new modules in `scripts/verification/`

---

## ✅ Implementation Complete

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately ✅
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories ✅
- **User Stories (Phase 3+)**: All depend on Foundational phase completion ✅
  - US1 and US2 can proceed in parallel (both P1) ✅
  - US3 depends on US1 and US2 being complete (combines them) ✅
- **Polish (Phase 6)**: Depends on all user stories being complete (in progress)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories ✅
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories ✅
- **User Story 3 (P2)**: Depends on US1 and US2 being complete (consumes their output) ✅

### Within Each User Story

- Models before script refactoring
- Refactoring before feature additions
- Core implementation before JSON output
- Story complete before moving to next priority

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T005 can run in parallel with T004
- US1 and US2 can run in parallel after Phase 2
- T029 and T030 can run in parallel (different files)

---

## Parallel Example: Setup Phase

```bash
# Launch in parallel:
Task T002: "Create JSON output formatter in scripts/verification/output.py"
Task T003: "Create configuration loader for environment variables in scripts/verification/config.py"
```

## Parallel Example: User Stories 1 & 2

```bash
# After Phase 2, both US1 and US2 can proceed in parallel:
# Developer A: User Story 1 (Database verification)
# Developer B: User Story 2 (Cache verification)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup ✅
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories) ✅
3. Complete Phase 3: User Story 1 ✅
4. **STOP and VALIDATE**: Test `verify_local_db.py` independently
5. Database verification is usable at this point

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready ✅
2. Add User Story 1 → Test independently → Database verification ready ✅
3. Add User Story 2 → Test independently → Cache verification ready ✅
4. Add User Story 3 → Test independently → Comprehensive suite ready ✅
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Existing scripts are enhanced in-place, preserving backward compatibility
