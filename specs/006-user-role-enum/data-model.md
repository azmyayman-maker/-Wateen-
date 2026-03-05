# Data Model: User Role Enum Refactoring

**Feature**: 006-user-role-enum
**Created**: 2026-03-01

---

## Entity: UserRole (TextChoices Enum)

### Before

| Value        | DB String        | Label        |
| ------------ | ---------------- | ------------ |
| PATIENT      | `'PATIENT'`      | Patient      |
| NURSE        | `'NURSE'`        | Nurse        |
| DOCTOR       | `'DOCTOR'`       | Doctor       |
| ADMIN        | `'ADMIN'`        | Admin        |
| AGENCY_ADMIN | `'AGENCY_ADMIN'` | Agency Admin |

### After

| Value        | DB String        | Label        | Arabic Label |
| ------------ | ---------------- | ------------ | ------------ |
| PATIENT      | `'PATIENT'`      | Patient      | مريض         |
| NURSE        | `'NURSE'`        | Nurse        | ممرض/ة       |
| AGENCY_ADMIN | `'AGENCY_ADMIN'` | Agency Admin | مدير الوكالة |
| SUPERADMIN   | `'SUPERADMIN'`   | Super Admin  | مدير النظام  |

### Migration Map

| Old Value | New Value    | Rationale                                 |
| --------- | ------------ | ----------------------------------------- |
| `DOCTOR`  | `NURSE`      | Legacy P2P placeholder, no actual doctors |
| `ADMIN`   | `SUPERADMIN` | Direct rename to match B2B2C nomenclature |

---

## Entity: CustomUser — Property Changes

### Before

| Property        | Logic                           |
| --------------- | ------------------------------- |
| `is_patient`    | `role == PATIENT`               |
| `is_nurse`      | `role == NURSE`                 |
| `is_doctor`     | `role == DOCTOR`                |
| `is_admin_user` | `role == ADMIN or is_superuser` |

### After

| Property          | Logic                                                  |
| ----------------- | ------------------------------------------------------ |
| `is_patient`      | `role == PATIENT`                                      |
| `is_nurse`        | `role == NURSE`                                        |
| `is_agency_admin` | `role == AGENCY_ADMIN`                                 |
| `is_superadmin`   | `role == SUPERADMIN`                                   |
| `is_admin_user`   | `role == SUPERADMIN or is_superuser` (backward-compat) |

### Removed Properties

| Property    | Reason                       |
| ----------- | ---------------------------- |
| `is_doctor` | DOCTOR role no longer exists |

---

## State Transitions

No state transitions apply — `role` is a static assignment field, not a state machine.

---

## Validation Rules

- `role` must be one of `UserRole.choices` (enforced at Django form/serializer level)
- `create_superuser()` defaults to `SUPERADMIN`
- `max_length=15` is sufficient for all values
