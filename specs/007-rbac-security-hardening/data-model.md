# Data Model: RBAC Security Hardening

**Branch**: `007-rbac-security-hardening` | **Date**: 2026-03-01

---

## Entity Relationship Diagram

```mermaid
erDiagram
    CustomUser ||--o| AgencyProfile : "agency (FK, nullable)"
    CustomUser ||--o| PatientProfile : "patient_profile (1:1)"
    CustomUser ||--o| NurseProfile : "nurse_profile (1:1)"
    NurseProfile }|--|| AgencyProfile : "agency (FK)"

    CustomUser {
        UUID id PK
        string national_id UK "14 digits"
        string phone_number UK "11 digits"
        string email "optional"
        UserRole role "PATIENT|NURSE|AGENCY_ADMIN|SUPERADMIN"
        UUID agency_id FK "nullable → AgencyProfile"
        string first_name_ar
        string last_name_ar
        bool is_active
        bool is_staff
        datetime date_joined
        datetime updated_at
    }

    AgencyProfile {
        UUID id PK
        string manager_name
        string commercial_registry UK
        string moh_license_number UK
        string tax_id UK
        AgencyStatus status "pending|verified|suspended|rejected"
        polygon coverage_polygon "SRID 4326"
        decimal rating "default 5.00"
        int network_capacity "default 0"
        DispatchMode dispatch_mode "AUTO|MANUAL"
        decimal wallet_balance
        string stripe_account_id "nullable"
        datetime created_at
        datetime updated_at
    }
```

---

## Entities Involved in This Feature

### CustomUser (existing — no schema changes)

| Field    | Type               | Constraints                                           | Relevance                                                    |
| -------- | ------------------ | ----------------------------------------------------- | ------------------------------------------------------------ |
| `role`   | CharField(15)      | TextChoices: PATIENT, NURSE, AGENCY_ADMIN, SUPERADMIN | Core field for permission checks and registration validation |
| `agency` | FK → AgencyProfile | nullable, SET_NULL                                    | Used by `IsAgencyAdmin` to check verified status             |

**Validation rules**:

- Self-registration: `role` limited to `PATIENT` or `AGENCY_ADMIN`
- Profile update: `role` is read-only (already enforced)
- Default: `PATIENT`

### AgencyProfile (existing — no schema changes)

| Field    | Type          | Constraints                                         | Relevance                           |
| -------- | ------------- | --------------------------------------------------- | ----------------------------------- |
| `status` | CharField(20) | TextChoices: pending, verified, suspended, rejected | Gate for `IsAgencyAdmin` permission |

**State transitions relevant to permission**:

- `pending` → access denied
- `verified` → access granted
- `suspended` → access denied
- `rejected` → access denied

### UserRole (existing enum — no changes)

```python
class UserRole(models.TextChoices):
    PATIENT = "PATIENT"
    NURSE = "NURSE"
    AGENCY_ADMIN = "AGENCY_ADMIN"
    SUPERADMIN = "SUPERADMIN"
```

**Registration rules**:

- Public self-registration: PATIENT, AGENCY_ADMIN only
- SUPERADMIN: CLI only (`create_superuser`)
- NURSE: Agency invitation flow only

---

## No Schema Changes Required

This feature is purely behavioral (permission logic, serializer validation, migration data). No new fields, tables, or indexes are needed.
