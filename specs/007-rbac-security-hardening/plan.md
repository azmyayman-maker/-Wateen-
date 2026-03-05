# Implementation Plan: RBAC Security Hardening

**Branch**: `007-rbac-security-hardening` | **Date**: 2026-03-01 | **Spec**: [spec.md](file:///d:/projects/Wateen/specs/007-rbac-security-hardening/spec.md)
**Input**: Feature specification from `/specs/007-rbac-security-hardening/spec.md`

## Summary

Harden the Wateen B2B2C RBAC system by: (1) enhancing the `IsAgencyAdmin` DRF permission to require a verified agency profile, (2) adding role escalation prevention at registration, and (3) confirming the existing data migration is correct. No schema changes required — this is purely behavioral (permission logic + serializer validation).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django 5.x, Django REST Framework 3.15, SimpleJWT
**Storage**: PostgreSQL + PostGIS
**Testing**: Django TestCase + DRF APIClient, run via pytest
**Target Platform**: Linux server (Docker)
**Project Type**: Web service (B2B2C healthcare aggregator)
**Performance Goals**: Permission check latency indistinguishable from current (SC-002)
**Constraints**: Arabic-first error messages (FR-008), stateless per-request permission checks
**Scale/Scope**: ~4 roles, ~6 permission classes, ~1400 lines of existing tests

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Constitution file is an unfilled placeholder template (`[PRINCIPLE_1_NAME]`, etc.) — **no gates defined**. No violations possible against an empty constitution. ✅

**Post-Phase 1 re-check**: Still no gates. ✅

## Project Structure

### Documentation (this feature)

```text
specs/007-rbac-security-hardening/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output — all unknowns resolved
├── data-model.md        # Phase 1 output — entity diagrams
├── quickstart.md        # Phase 1 output — developer quickstart
├── contracts/
│   └── api-contracts.md # Phase 1 output — API endpoint contracts
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend (Django monolith at repo root)
├── users/
│   ├── models.py          # UserRole, CustomUser, AgencyProfile, AgencyStatus
│   ├── permissions.py     # IsAgencyAdmin, IsAgencyAdminOrSuperAdmin (MODIFY)
│   ├── serializers.py     # UserRegistrationSerializer (MODIFY)
│   ├── views.py           # RegisterView, ProfileView
│   ├── agency_views.py    # AgencyApprovalView
│   ├── agency_serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── tests.py           # Existing test suite (ADD new tests)
├── config/
│   └── settings.py
└── tests/                 # Infrastructure tests
```

**Structure Decision**: Single Django monolith with `users` app containing all RBAC logic. No multi-app or multi-service complexity needed.

## Proposed Changes

### 1. IsAgencyAdmin Permission Enhancement

**File**: `users/permissions.py`

**Current** `IsAgencyAdmin.has_permission()`:

```python
return (
    request.user
    and request.user.is_authenticated
    and request.user.is_agency_admin
)
```

**New** `IsAgencyAdmin.has_permission()`:

```python
if not (request.user and request.user.is_authenticated):
    return False
if not request.user.is_agency_admin:
    return False
agency = getattr(request.user, 'agency', None)
return agency is not None and agency.status == 'verified'
```

**Message update**: `'يجب أن يكون لديك صلاحيات مدير وكالة موثقة'` (adding "verified" to the message).

**Also update**: `IsAgencyAdminOrSuperAdmin` to use the same verified-agency logic for AGENCY_ADMIN users (SUPERADMIN bypasses agency check).

### 2. Role Escalation Prevention in Registration Serializer

**File**: `users/serializers.py`

**Add** `validate_role()` to `UserRegistrationSerializer`:

```python
SELF_REGISTRATION_ROLES = {UserRole.PATIENT, UserRole.AGENCY_ADMIN}

def validate_role(self, value):
    if value == UserRole.SUPERADMIN:
        raise serializers.ValidationError(
            _('لا يمكن التسجيل كمدير نظام. يتم إنشاء مديري النظام عبر سطر الأوامر فقط.')
        )
    if value == UserRole.NURSE:
        raise serializers.ValidationError(
            _('لا يمكن التسجيل كممرض/ة. يتم إضافة الممرضين عبر دعوة الوكالة فقط.')
        )
    return value
```

### 3. Tests

**File**: `users/tests.py`

**Add** three new test classes:

1. **`TestIsAgencyAdminPermission`** (~8 tests): All 5 acceptance scenarios from User Story 1 + edge cases (suspended, deleted agency).
2. **`TestRoleEscalationPrevention`** (~6 tests): All 6 acceptance scenarios from User Story 3.
3. **`TestDataMigration`** (~5 tests): All 5 acceptance scenarios from User Story 2 (forward/backward/choices).

## Verification Plan

### Automated Tests

Run the full test suite:

```bash
python -m pytest users/tests.py -v
```

Run only the new RBAC tests:

```bash
python -m pytest users/tests.py -v -k "IsAgencyAdminPermission or RoleEscalation or DataMigration"
```

### Existing Tests

The existing test suite in `users/tests.py` (~1400 lines) covers:

- User creation, JWT auth, registration, profile CRUD, signals, admin interface, model validation
- These tests serve as regression validation — they must continue to pass after changes

## Complexity Tracking

> No constitution violations — this section is empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| —         | —          | —                                    |
