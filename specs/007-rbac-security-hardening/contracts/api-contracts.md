# API Contracts: RBAC Security Hardening

**Branch**: `007-rbac-security-hardening` | **Date**: 2026-03-01

---

## Affected Endpoints

### POST `/api/v1/auth/register/`

**Permission**: `AllowAny`

**Request Body** (changed — `role` now validated):

```json
{
  "national_id": "29901011234567",
  "phone_number": "01012345678",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "role": "PATIENT",
  "first_name_ar": "أحمد",
  "last_name_ar": "محمد"
}
```

**Allowed `role` values**: `"PATIENT"`, `"AGENCY_ADMIN"` only. Omitting defaults to `"PATIENT"`.

**Error responses for forbidden roles**:

```json
// role=SUPERADMIN
{
  "role": [
    "لا يمكن التسجيل كمدير نظام. يتم إنشاء مديري النظام عبر سطر الأوامر فقط."
  ]
}
// HTTP 400
```

```json
// role=NURSE
{
  "role": ["لا يمكن التسجيل كممرض/ة. يتم إضافة الممرضين عبر دعوة الوكالة فقط."]
}
// HTTP 400
```

---

### Agency-Protected Endpoints (all using `IsAgencyAdmin`)

**Permission**: `IsAuthenticated` + `IsAgencyAdmin` (enhanced)

**New behavior**: Requires `user.role == AGENCY_ADMIN` AND `user.agency.status == "verified"`.

**Error responses**:

```json
// 403 — user is AGENCY_ADMIN but agency not verified
{
  "detail": "يجب أن يكون لديك صلاحيات مدير وكالة موثقة"
}
```

```json
// 403 — user is AGENCY_ADMIN but has no AgencyProfile
{
  "detail": "يجب أن يكون لديك صلاحيات مدير وكالة موثقة"
}
```

```json
// 401 — unauthenticated
{
  "detail": "Authentication credentials were not provided."
}
```

---

### GET/PATCH `/api/v1/profile/`

**Permission**: `IsAuthenticated`

**Existing behavior (no change)**: `role` field is read-only in `UserProfileSerializer` and excluded from `UserUpdateSerializer`. Any attempt to change role via profile update is silently ignored.

---

## Permission Class Contract

### `IsAgencyAdmin` (enhanced)

```python
# Returns True ONLY when ALL conditions are met:
# 1. request.user is authenticated
# 2. request.user.role == "AGENCY_ADMIN"
# 3. request.user.agency exists (is not None)
# 4. request.user.agency.status == "verified"
```

### `IsAgencyAdminOrSuperAdmin` (enhanced for consistency)

```python
# Returns True when:
# 1. User is SUPERADMIN (no agency check needed), OR
# 2. User passes the full IsAgencyAdmin check (role + verified agency)
```
