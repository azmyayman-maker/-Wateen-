# Tasks: Infrastructure Resilience Upgrade

**Input**: Design documents from `/specs/001-redis-resilience/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included per AGENTS.md commands (pytest, ruff check)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Django monolith structure:
- `config/` - Django settings and configuration
- `scripts/` - Utility scripts
- `tests/` - Test files

---

## Phase 1: Setup

**Purpose**: Environment preparation and basic structure

- [x] T001 Update .env.example with documented REDIS_URL format per contracts/configuration.md
- [x] T002 [P] Create tests/unit/test_settings_resilience.py test file structure
- [x] T003 [P] Create tests/integration/test_redis_fallback.py test file structure

---

## Phase 2: Foundational (Core Configuration Module)

**Purpose**: Shared configuration utilities that all user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create config/redis_utils.py with sanitize_redis_url() function for credential masking
- [x] T005 Create config/redis_utils.py with ping_redis() function (1s timeout) for connectivity testing
- [x] T006 Create config/redis_utils.py with get_redis_config() function returning backend selection

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Developer Starts App Without Redis (Priority: P1) 🎯 MVP

**Goal**: Developer can run the app without REDIS_URL set, using in-memory fallback in dev mode

**Independent Test**: Unset REDIS_URL, set DEBUG=True, run `python manage.py runserver` - should start with warning message

### Tests for User Story 1

- [x] T007 [P] [US1] Write unit test for fallback to LocMemCache when no REDIS_URL in tests/unit/test_settings_resilience.py
- [x] T008 [P] [US1] Write unit test for production error when no REDIS_URL and DEBUG=False in tests/unit/test_settings_resilience.py
- [x] T009 [US1] Write integration test for dev server startup without Redis in tests/integration/test_redis_fallback.py

### Implementation for User Story 1

- [x] T010 [US1] Add REDIS_URL check and fallback logic to CACHES in config/settings.py
- [x] T011 [US1] Add fallback logic to CHANNEL_LAYERS in config/settings.py using InMemoryChannelLayer
- [x] T012 [US1] Add colored console warning message for fallback mode in config/settings.py
- [x] T013 [US1] Add production safety check (raise ImproperlyConfigured when DEBUG=False and no Redis)

**Checkpoint**: App starts without Redis in dev mode, fails in production mode

---

## Phase 4: User Story 2 - Developer Connects to Cloud Redis (Priority: P1)

**Goal**: Developer can configure REDIS_URL and app connects to cloud Redis with success message

**Independent Test**: Set valid REDIS_URL, run `python manage.py runserver` - should show "Connected to Cloud Redis" message

### Tests for User Story 2

- [x] T014 [P] [US2] Write unit test for Redis backend selection when URL valid in tests/unit/test_settings_resilience.py
- [x] T015 [P] [US2] Write unit test for URL sanitization (no password in logs) in tests/unit/test_settings_resilience.py
- [x] T016 [US2] Write integration test for Redis connection with latency reporting in tests/integration/test_redis_fallback.py

### Implementation for User Story 2

- [x] T017 [US2] Add ping validation before selecting Redis backend in config/settings.py
- [x] T018 [US2] Add colored success message with sanitized URL and latency in config/settings.py
- [x] T019 [US2] Add fallback-to-memory when ping fails (with dev-only warning) in config/settings.py

**Checkpoint**: App connects to cloud Redis when configured, shows sanitized connection status

---

## Phase 5: User Story 3 - Developer Runs Diagnostics (Priority: P2)

**Goal**: Developer can run `python scripts/doctor.py` to diagnose environment issues

**Independent Test**: Run `python scripts/doctor.py` - should output pass/fail report for all checks

### Tests for User Story 3

- [x] T020 [P] [US3] Write unit tests for doctor.py check functions in tests/unit/test_doctor.py
- [x] T021 [US3] Write integration test for full diagnostic output in tests/integration/test_doctor.py

### Implementation for User Story 3

- [x] T022 [P] [US3] Create check_python_version() in scripts/doctor.py
- [x] T023 [P] [US3] Create check_env_file() in scripts/doctor.py
- [x] T024 [P] [US3] Create check_redis() with latency reporting in scripts/doctor.py
- [x] T025 [P] [US3] Create check_database() in scripts/doctor.py
- [x] T026 [P] [US3] Create check_gdal() in scripts/doctor.py
- [x] T027 [US3] Create main() with visual pass/fail report output in scripts/doctor.py
- [x] T028 [US3] Add fix commands for each failed check in output

**Checkpoint**: Doctor script diagnoses all environment issues with actionable output

---

## Phase 6: User Story 4 - Developer on Windows Without GDAL (Priority: P2)

**Goal**: Windows developer without GDAL sees actionable warning instead of cryptic error

**Independent Test**: On Windows without GDAL, run app - should see warning with fix instructions

### Tests for User Story 4

- [x] T029 [P] [US4] Write unit test for GDAL auto-detection in tests/unit/test_settings_resilience.py
- [x] T030 [P] [US4] Write unit test for warning message when GDAL missing on Windows in tests/unit/test_settings_resilience.py

### Implementation for User Story 4

- [x] T031 [US4] Add Windows platform detection in config/settings.py
- [x] T032 [US4] Add GDAL_LIBRARY_PATH auto-detection for OSGeo4W paths in config/settings.py
- [x] T033 [US4] Add actionable warning message with doctor.py reference in config/settings.py

**Checkpoint**: Windows developers get clear GDAL guidance instead of stack traces

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T034 [P] Run ruff check . and fix any linting issues
- [x] T035 [P] Run pytest and ensure all tests pass
- [x] T036 Validate quickstart.md scenarios work as documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 - implement US1 first (MVP), then US2
  - US3 and US4 are P2 - can proceed in parallel after P1 stories complete
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - can start after Foundational
- **User Story 2 (P1)**: Independent - can start after Foundational (extends US1 config)
- **User Story 3 (P2)**: Independent - can start after Foundational
- **User Story 4 (P2)**: Independent - can start after Foundational

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Core logic before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003 can run in parallel (different test files)
- T004, T005, T006 can run in parallel (same file but independent functions)
- All [P] marked tests within a story can run in parallel
- T022-T026 can run in parallel (independent check functions)

---

## Parallel Example: User Story 3 (Doctor Script)

```bash
# Launch all check functions together:
Task: "Create check_python_version() in scripts/doctor.py"
Task: "Create check_env_file() in scripts/doctor.py"
Task: "Create check_redis() with latency reporting in scripts/doctor.py"
Task: "Create check_database() in scripts/doctor.py"
Task: "Create check_gdal() in scripts/doctor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test without REDIS_URL set
5. Deploy/demo if ready - dev server works without Redis!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Dev server works without Redis (MVP!)
3. Add User Story 2 → Cloud Redis connection works
4. Add User Story 3 → Diagnostic script available
5. Add User Story 4 → Windows GDAL handling
6. Each story adds value without breaking previous stories

---

## Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| 1 | Setup | 3 | 2 |
| 2 | Foundational | 3 | 0 |
| 3 | US1 - No Redis (P1) | 7 | 2 |
| 4 | US2 - Cloud Redis (P1) | 6 | 2 |
| 5 | US3 - Diagnostics (P2) | 9 | 5 |
| 6 | US4 - Windows GDAL (P2) | 5 | 2 |
| 7 | Polish | 3 | 2 |
| **Total** | | **36** | **15** |

**MVP Scope**: Phases 1-3 (User Story 1) = 13 tasks
