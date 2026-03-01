# Research: RBAC Security Hardening

**Branch**: `007-rbac-security-hardening` | **Date**: 2026-03-01

---

## 1. IsAgencyAdmin Permission — Verified Agency Check

### Decision

Enhance `IsAgencyAdmin` to require `AgencyProfile.status == VERIFIED` in addition to `role == AGENCY_ADMIN`. Access the agency via the `user.agency` FK on `CustomUser`.

### Rationale

- The current implementation only checks `user.is_agency_admin` (role), which grants access to AGENCY_ADMIN users with no agency, pending agencies, or suspended agencies.
- The spec mandates that access is gated on both role AND verified agency status (FR-001).
- `CustomUser.agency` is an FK to `AgencyProfile` (nullable), so `hasattr` or `getattr` with safe defaults handles the missing-profile edge case without 500s (FR-002).

### Alternatives Considered

1. **Check via `AgencyProfile` lookup query**: `AgencyProfile.objects.filter(admin_users=user, status='verified').exists()` — adds a DB query per request. Rejected because the FK on `CustomUser.agency` already provides direct access.
2. **Cache agency status in JWT token**: Would avoid DB lookups but makes status changes stale until token refresh. Rejected because stateless per-request checks are required by the spec (edge case: deleted/suspended agency must be denied immediately).

---

## 2. Data Migration — P2P to B2B2C Roles

### Decision

The existing migration `0004_refactor_userrole_enum.py` already correctly implements ADMIN → SUPERADMIN and DOCTOR → NURSE remapping with a reverse function. No new migration needed — the migration is already production-ready.

### Rationale

- Uses `apps.get_model("users", "CustomUser")` — correct per Django best practices (FR-003).
- Forward: `ADMIN → SUPERADMIN`, `DOCTOR → NURSE` via `bulk_update` (`.filter().update()`).
- Reverse: `SUPERADMIN → ADMIN`, `NURSE → DOCTOR` — documented as lossy for original NURSE users.
- Both functions are provided to `RunPython`, making it fully reversible (FR-004).
- `AlterField` step updates choices to the 4 canonical roles.

### Alternatives Considered

1. **Row-by-row migration with logging**: Would provide per-user audit trail but adds significant overhead for large datasets. Rejected in favor of batch `UPDATE` queries.
2. **Adding a `legacy_role` column**: Would solve the lossy reverse problem but adds unnecessary schema complexity. Documented as a known trade-off.

---

## 3. Role Escalation Prevention

### Decision

Add `validate_role()` method to `UserRegistrationSerializer` that restricts self-registration to `PATIENT` and `AGENCY_ADMIN` only. `UserProfileSerializer` already has `role` in `read_only_fields` — no change needed there.

### Rationale

- `UserRegistrationSerializer` currently has no role validation — any value from `UserRole.choices` is accepted (FR-005, FR-006 violation).
- `UserUpdateSerializer` (used for PATCH profile) does not include `role` in its fields — already safe.
- `UserProfileSerializer` lists `role` in `read_only_fields` — profile retrieval is safe (FR-007 ✓).
- Default role is `PATIENT` (via model default), so omitting role works correctly (acceptance scenario 5).

### Alternatives Considered

1. **View-level role enforcement (in RegisterView)**: Would work but violates DRF's serializer-as-validation-layer pattern. Rejected because serializer validation is the standard Django/DRF approach.
2. **Separate serializers per role**: `PatientRegistrationSerializer` and `AgencyAdminRegistrationSerializer` on separate endpoints. Adds unnecessary API surface for this simple validation. Rejected.

---

## 4. Arabic Error Messages

### Decision

All permission denial messages are already in Arabic in the existing permission classes. The new `validate_role()` errors will also use Arabic messages wrapped in `gettext_lazy`.

### Rationale

- FR-008 mandates Arabic-first error messages.
- Existing pattern uses raw Arabic strings in `message` attributes (e.g., `'يجب أن يكون لديك صلاحيات مدير الوكالة'`).
- Validation errors should follow the same pattern.

---

## 5. Performance and Statelessness

### Decision

The `IsAgencyAdmin` permission check will access `user.agency` (FK, already loaded or single-query) and check `user.agency.status` — no additional query if the FK is already selected. Each request is evaluated independently.

### Rationale

- SC-002 requires no measurable latency impact.
- Django's FK access triggers a single SELECT if not prefetched, but since this is per-request anyway, the overhead is minimal.
- Stateless evaluation means a suspended/deleted agency is caught on the very next request (edge case requirement).

---

## 6. Technology Confirmation

| Aspect          | Value                                                |
| --------------- | ---------------------------------------------------- |
| **Language**    | Python 3.11+                                         |
| **Framework**   | Django 5.x + DRF 3.15                                |
| **Auth**        | SimpleJWT (token-based)                              |
| **Database**    | PostgreSQL + PostGIS                                 |
| **Testing**     | Django TestCase + DRF APIClient                      |
| **Test Runner** | pytest with `DJANGO_SETTINGS_MODULE=config.settings` |
