# Tasks: RBAC Security Hardening

**Input**: Design documents from `/specs/007-rbac-security-hardening/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Tests ARE included — the spec explicitly requires acceptance scenarios for all 3 user stories, and the project already has an established test suite in `users/tests.py`.

**Organization**: Tasks grouped by user story. All 3 stories are P1 priority and independent of each other — they can be implemented in parallel.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in descriptions

---

## Phase 1: Setup

**Purpose**: No project setup needed — this is an enhancement to an existing Django project with established patterns. Skip to Foundational.

_(No tasks — project infrastructure already exists)_

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify existing code state before making changes

**⚠️ CRITICAL**: These must complete before any user story work begins

- [x] T001 Verify existing test suite passes by running `python -m pytest users/tests.py -v` from project root
- [x] T002 Review current `UserRole` enum values in `users/models.py` to confirm PATIENT, NURSE, AGENCY_ADMIN, SUPERADMIN are the 4 canonical roles
- [x] T003 [P] Review current `AgencyStatus` enum values in `users/models.py` to confirm pending, verified, suspended, rejected are the valid statuses

**Checkpoint**: Foundation verified — all existing tests pass, enums confirmed correct

---

## Phase 3: User Story 1 — Agency Admin Access Gating (Priority: P1) 🎯 MVP

**Goal**: Enhance `IsAgencyAdmin` permission to require verified agency status, not just the AGENCY_ADMIN role. Also update `IsAgencyAdminOrSuperAdmin` for consistency.

**Independent Test**: Create users with various agency states (no profile, pending, verified, suspended) and assert only AGENCY_ADMIN + VERIFIED agency pass the permission check.

### Tests for User Story 1

- [x] T004 [US1] Write `TestIsAgencyAdminPermission` test class in `users/tests.py` with the following test methods:
  - `test_verified_agency_admin_allowed` — AGENCY_ADMIN + verified agency → 200 (acceptance 1)
  - `test_pending_agency_admin_denied` — AGENCY_ADMIN + pending agency → 403 (acceptance 2)
  - `test_no_agency_profile_denied` — AGENCY_ADMIN + no AgencyProfile → 403, no 500 (acceptance 3)
  - `test_patient_denied` — PATIENT role → 403 (acceptance 4)
  - `test_unauthenticated_denied` — no auth → 401 (acceptance 5)
  - `test_suspended_agency_denied` — AGENCY_ADMIN + suspended agency → 403 (edge case)
  - `test_rejected_agency_denied` — AGENCY_ADMIN + rejected agency → 403 (edge case)
  - Tests should use DRF's `APIRequestFactory` and call `IsAgencyAdmin().has_permission()` directly

### Implementation for User Story 1

- [x] T005 [US1] Update `IsAgencyAdmin.has_permission()` in `users/permissions.py` to check `user.agency` exists AND `user.agency.status == 'verified'`. Update the Arabic error message to `'يجب أن يكون لديك صلاحيات مدير وكالة موثقة'`
- [x] T006 [US1] Update `IsAgencyAdminOrSuperAdmin.has_permission()` in `users/permissions.py` to use the same verified-agency logic for AGENCY_ADMIN users (SUPERADMIN bypasses the agency check)
- [x] T007 [US1] Run `python -m pytest users/tests.py -v -k "IsAgencyAdminPermission"` and verify all tests pass

**Checkpoint**: Agency Admin access gating works — only verified agencies can access protected endpoints

---

## Phase 4: User Story 2 — Safe Data Migration (Priority: P1)

**Goal**: Validate that the existing migration `0004_refactor_userrole_enum.py` correctly maps ADMIN→SUPERADMIN, DOCTOR→NURSE with a working reverse function.

**Independent Test**: Run the migration forward and backward in tests, verifying role values before and after.

### Tests for User Story 2

- [x] T008 [US2] Write `TestRoleMigration` test class in `users/tests.py` with the following test methods:
  - `test_forward_admin_to_superadmin` — create user with role ADMIN via raw SQL, run migration forward, assert role is SUPERADMIN (acceptance 1)
  - `test_forward_doctor_to_nurse` — create user with role DOCTOR via raw SQL, run migration forward, assert role is NURSE (acceptance 2)
  - `test_forward_patient_unchanged` — create PATIENT user, run migration forward, assert role is still PATIENT (acceptance 3)
  - `test_reverse_superadmin_to_admin` — assert reverse migration maps SUPERADMIN → ADMIN and NURSE → DOCTOR (acceptance 4)
  - `test_role_field_choices_correct` — assert `UserRole.choices` contains exactly PATIENT, NURSE, AGENCY_ADMIN, SUPERADMIN (acceptance 5)
  - Note: Use `django.test.TestCase` with direct model field inspection for choices test; migration tests should use `MigrationTestCase` pattern or validate current state

### Implementation for User Story 2

- [x] T009 [US2] Review existing migration `users/migrations/0004_refactor_userrole_enum.py` and confirm it uses `apps.get_model()` correctly (FR-003), has both forward and reverse functions (FR-004), and document any issues found
- [x] T010 [US2] Run `python -m pytest users/tests.py -v -k "RoleMigration"` and verify all tests pass

**Checkpoint**: Data migration is verified correct — forward and backward operations work without data loss

---

## Phase 5: User Story 3 — Role Escalation Prevention (Priority: P1)

**Goal**: Add `validate_role()` to `UserRegistrationSerializer` to block SUPERADMIN and NURSE self-registration. Confirm `UserProfileSerializer` already has `role` as read-only.

**Independent Test**: Submit registration requests with each role value and assert only PATIENT and AGENCY_ADMIN succeed.

### Tests for User Story 3

- [x] T011 [US3] Write `TestRoleEscalationPrevention` test class in `users/tests.py` with the following test methods:
  - `test_register_as_patient_succeeds` — POST register with role=PATIENT → 201 (acceptance 1)
  - `test_register_as_agency_admin_succeeds` — POST register with role=AGENCY_ADMIN → 201 (acceptance 2)
  - `test_register_as_superadmin_blocked` — POST register with role=SUPERADMIN → 400 with Arabic error (acceptance 3)
  - `test_register_as_nurse_blocked` — POST register with role=NURSE → 400 with Arabic error (acceptance 4)
  - `test_register_no_role_defaults_to_patient` — POST register without role → 201, user.role == PATIENT (acceptance 5)
  - `test_profile_update_role_readonly` — PATCH profile with role=SUPERADMIN → role unchanged (acceptance 6)
  - Tests should use `APIClient` with POST to `/api/v1/auth/register/` and GET/PATCH to `/api/v1/profile/`

### Implementation for User Story 3

- [x] T012 [US3] Add `validate_role()` method to `UserRegistrationSerializer` in `users/serializers.py` that raises `ValidationError` with Arabic messages for SUPERADMIN and NURSE roles (FR-005, FR-006)
- [x] T013 [US3] Verify `UserProfileSerializer` in `users/serializers.py` has `role` in `read_only_fields` (FR-007 — already correct, just add a comment confirming this is intentional for RBAC)
- [x] T014 [US3] Run `python -m pytest users/tests.py -v -k "RoleEscalationPrevention"` and verify all tests pass

**Checkpoint**: Role escalation is fully blocked — no public path to SUPERADMIN or NURSE exists

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all user stories

- [ ] T015 Run full test suite: `python -m pytest users/tests.py -v` to verify no regressions in existing ~1400 lines of tests
- [x] T016 [P] Verify all permission denial messages are in Arabic (FR-008) by reviewing `users/permissions.py` and `users/serializers.py`
- [ ] T017 [P] Run `python -m pytest tests/ -v` to verify no infrastructure test regressions
- [ ] T018 Validate quickstart.md verification commands all pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Skipped (existing project)
- **Foundational (Phase 2)**: No dependencies — can start immediately
- **User Stories (Phases 3–5)**: All depend on Phase 2 completion
  - US1, US2, US3 are **fully independent** — can run in parallel
  - US1 and US3 modify `users/permissions.py` and `users/serializers.py` respectively (different files, no conflicts)
  - US2 is read-only (validation of existing migration)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Agency Admin Access Gating)**: Phase 2 → T004 → T005, T006 → T007
- **US2 (Safe Data Migration)**: Phase 2 → T008 → T009 → T010
- **US3 (Role Escalation Prevention)**: Phase 2 → T011 → T012, T013 → T014

### Within Each User Story

- Tests written FIRST → verify they FAIL → implement → verify tests PASS
- No model changes needed (existing schema is correct)
- Permission changes (US1) and serializer changes (US3) are in different files

### Parallel Opportunities

- **Phase 2**: T002 and T003 can run in parallel [P]
- **Phases 3–5**: All three user stories can be worked on simultaneously (different files)
- **Phase 6**: T016 and T017 can run in parallel [P]

---

## Parallel Example: All User Stories

```bash
# After Phase 2 completes, all three stories can start simultaneously:

# Stream 1: User Story 1 (permissions.py)
Task T004: "Write TestIsAgencyAdminPermission in users/tests.py"
Task T005: "Update IsAgencyAdmin in users/permissions.py"
Task T006: "Update IsAgencyAdminOrSuperAdmin in users/permissions.py"
Task T007: "Run US1 tests"

# Stream 2: User Story 2 (migration review — read-only)
Task T008: "Write TestRoleMigration in users/tests.py"
Task T009: "Review migration 0004_refactor_userrole_enum.py"
Task T010: "Run US2 tests"

# Stream 3: User Story 3 (serializers.py)
Task T011: "Write TestRoleEscalationPrevention in users/tests.py"
Task T012: "Add validate_role() to UserRegistrationSerializer in users/serializers.py"
Task T013: "Verify UserProfileSerializer read-only role in users/serializers.py"
Task T014: "Run US3 tests"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational verification
2. Complete Phase 3: User Story 1 (Agency Admin Access Gating)
3. **STOP and VALIDATE**: Test US1 independently with `pytest -k "IsAgencyAdminPermission"`
4. This alone closes the most critical security gap

### Incremental Delivery

1. Complete Phase 2 → Foundation verified
2. Add US1 (Agency Gating) → Test independently → **Biggest security win** (MVP!)
3. Add US2 (Migration Validation) → Test independently → **Data integrity confirmed**
4. Add US3 (Escalation Prevention) → Test independently → **All OWASP A01 risks closed**
5. Phase 6 → Full regression pass → **Feature complete**

### Parallel Team Strategy

With 3 developers:

1. Team completes Phase 2 together (5 minutes)
2. Once Phase 2 done:
   - Developer A: User Story 1 (permissions.py)
   - Developer B: User Story 2 (migration review)
   - Developer C: User Story 3 (serializers.py)
3. All stories complete independently, no merge conflicts

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- All 3 user stories are P1 priority and fully independent
- Tests use existing patterns from `users/tests.py` (APIClient, TestCase)
- No new migrations needed — existing schema and migration 0004 are correct
- Arabic error messages required for all user-facing strings (FR-008)
- Commit after each completed user story for clean git history
