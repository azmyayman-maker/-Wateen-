# Tasks: Pricing Engine Remediation

**Input**: Design documents from `/specs/002-pricing-engine-remediation/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Included based on existing test file patterns in project.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Django app structure: `visits/` at repository root
- Tests: `visits/tests/`

---

## Phase 1: Setup

**Purpose**: Verify environment and understand existing code

- [x] T001 Review existing `visits/api.py` to understand current estimate flow
- [x] T002 Review existing `visits/services/pricing.py` to understand pricing logic
- [x] T003 [P] Review existing `visits/services/matching.py` to understand nurse lookup
- [x] T004 [P] Review existing `visits/signals.py` to understand logging pattern
- [x] T005 [P] Review existing `users/models.py` for NurseProfile fields

---

## Phase 2: Foundational (Core Utility)

**Purpose**: Create the shared utility function that US1 and US2 both depend on

**⚠️ CRITICAL**: US1 and US2 cannot proceed until this phase is complete

- [x] T006 Create `visits/utils.py` with `find_nearest_available_nurse(lat, lng)` function implementing PostGIS Distance query with availability/verification filters

**Checkpoint**: Core utility ready - user story implementation can begin

---

## Phase 3: User Story 1+2 - Dynamic Distance with Availability Filtering (Priority: P1) 🎯 MVP

**Goal**: Calculate distance to nearest available verified nurse dynamically

**Independent Test**: Request estimates from different locations; verify distance varies based on actual nurse locations. Mark nurses unavailable and verify they're excluded.

> **Note**: US1 and US2 are tightly coupled through `find_nearest_available_nurse()` - implemented together.

### Tests for US1+US2

- [x] T007 [P] [US1] Add test for dynamic distance calculation in `visits/tests/test_pricing.py` - verify distance varies by nurse location
- [x] T008 [P] [US2] Add test for availability filter in `visits/tests/test_pricing.py` - verify unavailable nurses excluded
- [x] T009 [P] [US2] Add test for verification filter in `visits/tests/test_pricing.py` - verify unverified nurses excluded

### Implementation for US1+US2

- [x] T010 [US1] Modify `visits/api.py` - replace hardcoded `distance_km = Decimal("5.0")` with call to `find_nearest_available_nurse()`
- [x] T011 [US1] Handle case when no nurse found - default distance to 0 in `visits/api.py`
- [x] T012 [US2] Modify `visits/services/matching.py` - add `is_available=True` and `verification_status=VERIFIED` filter to `find_candidates()`
- [x] T013 [US1+US2] Run tests to verify dynamic distance and availability filtering work

**Checkpoint**: Estimates now use dynamic distance with availability filtering

---

## Phase 4: User Story 3 - Timezone-Aware Pricing (Priority: P2)

**Goal**: Use Cairo timezone for night/day pricing logic

**Independent Test**: Make estimates at different times; verify night multiplier (1.5x) applied between 22:00-06:00 Cairo time.

### Tests for US3

- [x] T014 [P] [US3] Add test for night hours (23:00) in `visits/tests/test_pricing.py` - verify 1.5x multiplier
- [x] T015 [P] [US3] Add test for day hours (10:00) in `visits/tests/test_pricing.py` - verify 1.0x multiplier
- [x] T016 [P] [US3] Add test for boundary time (22:00) in `visits/tests/test_pricing.py` - verify night starts

### Implementation for US3

- [x] T017 [US3] Add `from django.utils import timezone` import to `visits/services/pricing.py`
- [x] T018 [US3] Replace `datetime.now()` with `timezone.localtime(timezone.now())` in `is_night_hours()` method in `visits/services/pricing.py`
- [x] T019 [US3] Run tests to verify timezone-aware pricing

**Checkpoint**: Pricing now correctly applies night/day multiplier based on Cairo time

---

## Phase 5: User Story 4 - Non-Blocking Logging (Priority: P2)

**Goal**: Logging doesn't block API response

**Independent Test**: Measure API response time; verify logging doesn't add latency.

### Tests for US4

- [x] T020 [P] [US4] Add test verifying `transaction.on_commit` used in `visits/tests/test_pricing.py`

### Implementation for US4

- [x] T021 [US4] Add `from django.db import transaction` import to `visits/signals.py`
- [x] T022 [US4] Wrap `EstimateLog.objects.create()` in `transaction.on_commit()` lambda in `visits/signals.py`
- [x] T023 [US4] Run tests to verify logging is non-blocking

**Checkpoint**: Logging now happens asynchronously after transaction commit

---

## Phase 6: Polish & Validation

**Purpose**: Final cleanup and verification

- [x] T024 Run full test suite: `cd src && pytest visits/tests/test_pricing.py -v`
- [x] T025 [P] Run linting: `ruff check visits/`
- [x] T026 Verify no hardcoded `5.0` distance remains in `visits/api.py`
- [x] T027 [P] Verify `datetime.now()` replaced with `timezone.now()` in `visits/services/pricing.py`
- [x] T028 Update AGENTS.md with remediation completion notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - code review only
- **Foundational (Phase 2)**: No dependencies - creates core utility
- **US1+US2 (Phase 3)**: Depends on Phase 2 (needs `find_nearest_available_nurse`)
- **US3 (Phase 4)**: No dependencies on US1+US2 - can run in parallel
- **US4 (Phase 5)**: No dependencies on US1+US3 - can run in parallel
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1+US2 | Phase 2 | US3, US4 |
| US3 | Nothing | US1+US2, US4 |
| US4 | Nothing | US1+US2, US3 |

### Parallel Opportunities

- Phase 1: T003, T004, T005 can run in parallel
- Phase 3: T007, T008, T009 can run in parallel (different test cases)
- Phase 4: T014, T015, T016 can run in parallel (different test cases)
- Phase 6: T025, T027 can run in parallel
- **After Phase 2**: US3 and US4 can be implemented in parallel with US1+US2

---

## Parallel Example: All User Stories

```bash
# After Phase 2 completes, these can run in parallel:
# Team Member 1: US1+US2 (Phase 3)
Task: T007-T013

# Team Member 2: US3 (Phase 4)  
Task: T014-T019

# Team Member 3: US4 (Phase 5)
Task: T020-T023
```

---

## Implementation Strategy

### MVP First (US1+US2 Only)

1. Complete Phase 1: Setup (code review)
2. Complete Phase 2: Foundational (core utility)
3. Complete Phase 3: US1+US2 (dynamic distance + availability)
4. **STOP and VALIDATE**: Test estimate accuracy
5. Deploy if ready - core pricing now accurate

### Incremental Delivery

1. Setup + Foundational → Core utility ready
2. Add US1+US2 → Accurate distance-based pricing (MVP!)
3. Add US3 → Correct timezone handling
4. Add US4 → Non-blocking logging
5. Polish → Production ready

---

## Notes

- US1 and US2 combined - they share `find_nearest_available_nurse()` implementation
- All changes are to existing files - no new migrations needed
- Existing models (NurseProfile, EstimateLog) unchanged
- Tests follow existing pytest patterns in project
