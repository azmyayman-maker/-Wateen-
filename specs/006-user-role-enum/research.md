# Research: User Role Enum Refactoring

**Feature**: 006-user-role-enum
**Created**: 2026-03-01

---

## R1: Legacy Role Removal Blast Radius

**Decision**: Safe to remove `DOCTOR` and `ADMIN` from `UserRole` enum.

**Rationale**: Grepped the entire codebase. Only 2 files reference these roles:

- `users/models.py` — enum definition, `create_superuser` default, `is_doctor` property, `is_admin_user` property
- `users/tests.py` — test assertions for `is_doctor` (L437-439), `UserRole.DOCTOR` (L416-420, L947), `is_admin_user` (L444), superuser role assertion `'ADMIN'` (L187), `test_no_profile_for_admin_role` (L956-968)

No other app references `UserRole.DOCTOR` or `UserRole.ADMIN`. The `visits/` app, `config/`, and `frontend/` are unaffected.

**Alternatives considered**: Keep DOCTOR/ADMIN as deprecated aliases → rejected (introduces confusion, the B2B2C model has no doctor persona).

---

## R2: Signals Impact

**Decision**: No changes needed to `users/signals.py`.

**Rationale**: The signal only checks for `UserRole.PATIENT` and `UserRole.NURSE` — both are retained. SUPERADMIN and AGENCY_ADMIN users do not get auto-created profiles, which is correct behavior.

---

## R3: Migration Strategy

**Decision**: Use a single Django data migration (0004) with RunPython to remap legacy role values.

**Rationale**:

- The `role` CharField doesn't change schema (same max_length, same column type)
- Only the `choices` constraint changes (Django-level, not DB-level)
- A `RunPython` migration can update existing rows + alter the field choices atomically
- Must be reversible: SUPERADMIN → ADMIN, and NURSE stays NURSE (can't reverse DOCTOR→NURSE perfectly, but acceptable since DOCTOR was unused)

**Alternatives considered**:

- Schema migration only (no data update) → rejected, old ADMIN/DOCTOR values would be orphaned
- Manual SQL → rejected, Django migration is more portable and reversible

---

## R4: Test Plan

**Decision**: Update existing `TestUserProperties` and signal tests; add new test cases for `is_agency_admin` and `is_superadmin`.

**Rationale**: Existing test at L406-444 tests role properties. The `test_no_profile_for_doctor_role` test (L941-954) must be adapted to test AGENCY_ADMIN or SUPERADMIN instead. The superuser assertion at L187 (`assertEqual(user.role, 'ADMIN')`) must change to `'SUPERADMIN'`.

**Existing test command**: `pytest users/tests.py -v` or `python manage.py test users`
