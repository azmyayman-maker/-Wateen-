# User Role Enum Refactoring — Feature Specification

**Feature Branch**: `006-user-role-enum`
**Created**: 2026-03-01
**Origin**: AGENTS.md Core Data Model + WBS Phase 1 (RBAC Enum + Permission Classes)
**Status**: DRAFT

---

## 1. Executive Summary

This specification defines the refactoring of the `UserRole` enum in `users/models.py` to align with Wateen's finalized B2B2C architecture. The platform recognizes exactly **four canonical personas**: Patient, Agency Admin, Nurse, and SuperAdmin. The current codebase contains stale legacy roles (`DOCTOR`, `ADMIN`) from the P2P era that must be replaced. Additionally, the `SUPERADMIN` role — referenced throughout the WBS, PRD, and AGENTS.md — has never been added to the enum.

This change also introduces missing `@property` convenience accessors (`is_agency_admin`, `is_superadmin`) on `CustomUser`, ensuring that permission classes and business logic can rely on clean, readable role checks throughout the codebase.

---

## 2. User Scenarios & Acceptance Criteria

### Scenario 1 — Role Assignment at Registration

**Description**: When a new user is created, their role must be one of the four canonical values.

**Acceptance Criteria**:

1. **Given** a new user is registered, **When** no role is explicitly set, **Then** the role defaults to `PATIENT`.
2. **Given** a superuser is created via `create_superuser`, **When** no role is explicitly set, **Then** the role defaults to `SUPERADMIN`.
3. **Given** an API request tries to create a user with role `DOCTOR` or `ADMIN`, **Then** the request is rejected with a validation error (invalid choice).

### Scenario 2 — Role-Based Property Checks

**Description**: Code throughout the platform uses `@property` shortcuts to check a user's role instead of comparing strings directly.

**Acceptance Criteria**:

1. **Given** a user with role `AGENCY_ADMIN`, **When** `user.is_agency_admin` is accessed, **Then** it returns `True`.
2. **Given** a user with role `SUPERADMIN`, **When** `user.is_superadmin` is accessed, **Then** it returns `True`.
3. **Given** a user with role `PATIENT`, **When** `user.is_patient` is accessed, **Then** it returns `True`.
4. **Given** a user with role `NURSE`, **When** `user.is_nurse` is accessed, **Then** it returns `True`.
5. **Given** a user with role `PATIENT`, **When** any other role property (e.g., `is_nurse`, `is_agency_admin`) is accessed, **Then** it returns `False`.

### Scenario 3 — SuperAdmin Privileges

**Description**: SuperAdmins are the highest-authority users who manage the entire Wateen platform.

**Acceptance Criteria**:

1. **Given** a `SUPERADMIN` user, **When** `user.is_admin_user` is accessed, **Then** it returns `True` (backward compatibility).
2. **Given** a `SUPERADMIN` user, **When** `user.is_superadmin` is accessed, **Then** it also returns `True`.
3. **Given** a `SUPERADMIN` user, **When** Django Admin access is checked, **Then** `is_staff` should be `True`.

### Scenario 4 — Data Migration of Legacy Roles

**Description**: Existing users with roles `DOCTOR` or `ADMIN` must be migrated to appropriate new roles.

**Acceptance Criteria**:

1. **Given** existing users with role `ADMIN`, **When** the migration runs, **Then** their role is updated to `SUPERADMIN`.
2. **Given** existing users with role `DOCTOR`, **When** the migration runs, **Then** their role is updated to `NURSE` (or handled per business decision).
3. **Given** the migration completes, **When** querying the database, **Then** zero records exist with role values `ADMIN` or `DOCTOR`.

---

## 3. Functional Requirements

### FR-001: Canonical Role Enum

The `UserRole` enum must contain exactly four values:

- `PATIENT` — End consumers requesting home healthcare services
- `AGENCY_ADMIN` — Agency managers operating the B2B SaaS Dashboard
- `NURSE` — Healthcare professionals employed by licensed agencies
- `SUPERADMIN` — Platform administrators managing the entire Wateen ecosystem

### FR-002: Role Field Configuration

The `role` field on `CustomUser` must:

- Use `max_length=15` (sufficient for `AGENCY_ADMIN`, the longest value)
- Default to `UserRole.PATIENT`
- Be constrained to `UserRole.choices` only

### FR-003: Property Accessors

`CustomUser` must expose the following `@property` methods:

- `is_patient` → `True` when `role == PATIENT`
- `is_agency_admin` → `True` when `role == AGENCY_ADMIN`
- `is_nurse` → `True` when `role == NURSE`
- `is_superadmin` → `True` when `role == SUPERADMIN`
- `is_admin_user` → `True` when `role == SUPERADMIN` or `is_superuser` is `True` (backward-compatible)

### FR-004: Superuser Creation

`create_superuser()` must default `role` to `UserRole.SUPERADMIN` instead of the current `UserRole.ADMIN`.

### FR-005: Data Migration

A Django data migration must:

- Map `ADMIN` → `SUPERADMIN`
- Map `DOCTOR` → `NURSE` (assumption: DOCTOR was a legacy placeholder; no actual doctors registered)
- Be reversible

---

## 4. Key Entities

| Entity                   | Affected Field | Change                                                                                   |
| ------------------------ | -------------- | ---------------------------------------------------------------------------------------- |
| `UserRole` (TextChoices) | Entire enum    | Remove `DOCTOR`, `ADMIN`; Add `SUPERADMIN`                                               |
| `CustomUser`             | `role`         | No schema change (CharField stays)                                                       |
| `CustomUser`             | Properties     | Add `is_agency_admin`, `is_superadmin`; Remove `is_doctor`; Rename `is_admin_user` logic |

---

## 5. Scope & Boundaries

### In Scope

- Modifying the `UserRole` enum in `users/models.py`
- Adding/updating `@property` accessors on `CustomUser`
- Updating `create_superuser()` default role
- Creating a data migration for legacy role values
- Updating any direct references to removed roles within the `users/` app

### Out of Scope

- Permission classes (separate ticket in Phase 1)
- JWT token claims with role/agency info (Phase 2)
- React Admin RBAC integration (Phase 2)
- Frontend role-based routing (Phase 7)

---

## 6. Dependencies & Assumptions

### Dependencies

- PostgreSQL database must be accessible for migration execution
- No concurrent schema migrations modifying the `users_customuser` table

### Assumptions

- The `DOCTOR` role was a legacy P2P placeholder; no active doctor-role users exist in production. If they do, mapping to `NURSE` is acceptable per business rules.
- The `ADMIN` role maps directly to `SUPERADMIN` — these users retain all existing permissions.
- The `max_length=15` on the `role` CharField is sufficient (longest value: `AGENCY_ADMIN` = 12 chars, `SUPERADMIN` = 10 chars).

---

## 7. Success Criteria

- **SC-001**: The `UserRole` enum contains exactly 4 values: `PATIENT`, `AGENCY_ADMIN`, `NURSE`, `SUPERADMIN`.
- **SC-002**: All four `@property` accessors (`is_patient`, `is_nurse`, `is_agency_admin`, `is_superadmin`) return correct boolean values for every role.
- **SC-003**: `is_admin_user` remains backward-compatible and returns `True` for SUPERADMIN users.
- **SC-004**: `create_superuser()` assigns `SUPERADMIN` role by default.
- **SC-005**: After migration, zero database records contain the values `ADMIN` or `DOCTOR` in the `role` column.
- **SC-006**: All existing tests pass after the refactoring.

---

## 8. Risks

| Risk                                                                     | Likelihood | Impact                          | Mitigation                                                 |
| ------------------------------------------------------------------------ | ---------- | ------------------------------- | ---------------------------------------------------------- |
| Code elsewhere references `UserRole.DOCTOR` or `UserRole.ADMIN` directly | Medium     | High — will cause import errors | Grep entire codebase for these references before migration |
| Existing tests assert on removed roles                                   | Medium     | Medium — test failures          | Update tests as part of this task                          |
| Third-party integrations storing role strings externally                 | Low        | High — data inconsistency       | Document migration in release notes                        |

---

_This specification is ready for `/speckit.clarify` or `/speckit.plan`._
