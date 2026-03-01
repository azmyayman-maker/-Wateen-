# Data Model: Entities Under Test

**Date**: 2026-03-01 | **Branch**: `011-phase1-qa-security`

This ticket does not create new models. It validates the integrity constraints of existing Phase 1 entities.

## Entities Under Test

### NurseProfile (`users/models.py:369`)

| Field    | Type                       | Constraint Under Test                                     |
| -------- | -------------------------- | --------------------------------------------------------- |
| `user`   | OneToOneField → CustomUser | PK, CASCADE                                               |
| `agency` | ForeignKey → AgencyProfile | **NOT NULL (DB-level)** — B2B2C rule: no freelance nurses |

**Validation Chain**:

1. DB column `agency_id` has NOT NULL constraint (FK without `null=True`)
2. `NurseProfile.clean()` raises `ValidationError` if `agency_id` is falsy
3. `NurseProfile.save()` calls `full_clean()` automatically

**Test Strategy**: Bypass ORM validation (`skip_full_clean=True` or raw `objects.create()`) to verify DB-level constraint fires `IntegrityError`.

---

### AgencyProfile (`users/models.py:222`)

| Field                 | Type                     | Constraint Under Test           |
| --------------------- | ------------------------ | ------------------------------- |
| `coverage_polygon`    | PolygonField (SRID 4326) | **PostGIS geometry validation** |
| `commercial_registry` | CharField                | UNIQUE                          |
| `moh_license_number`  | CharField                | UNIQUE                          |

**Index**: `GistIndex(fields=["coverage_polygon"])` for sub-ms spatial queries.

**Test Strategy**: Create polygon with invalid geometry (< 4 points in ring). Assert `GEOSException`.

---

### Visit (`visits/models.py:136`)

| Field         | Type                    | Constraint Under Test                                      |
| ------------- | ----------------------- | ---------------------------------------------------------- |
| `base_price`  | DecimalField            | **Read-only from client** (no input serializer exposes it) |
| `final_price` | DecimalField            | **Read-only from client**                                  |
| `status`      | CharField (VisitStatus) | State machine via `ALLOWED_TRANSITIONS`                    |

**Test Strategy**: Authenticate as PATIENT and attempt to modify price fields via API. Assert they are ignored.

---

### UserRole (`users/models.py:18`)

| Value        | Permission Classes                       |
| ------------ | ---------------------------------------- |
| PATIENT      | Default only (IsAuthenticated)           |
| NURSE        | IsNurseOrAbove                           |
| AGENCY_ADMIN | IsAgencyAdmin, IsAgencyAdminOrSuperAdmin |
| SUPERADMIN   | IsSuperAdmin, bypasses all               |

**Test Strategy**: For each role, verify access to role-gated endpoints matches expected 200/403 matrix.

## State Transitions (Visit)

```
PENDING_AGENCY → PENDING_NURSE → ACCEPTED → EN_ROUTE → IN_PROGRESS → COMPLETED
     ↕               ↕             ↕           ↕            ↕
  CANCELLED       CANCELLED     CANCELLED   CANCELLED    CANCELLED
```

Terminal states: `COMPLETED`, `CANCELLED` (no outgoing transitions).
