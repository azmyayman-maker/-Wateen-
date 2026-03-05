# Quickstart: RBAC Security Hardening

**Branch**: `007-rbac-security-hardening`

---

## What This Feature Does

Hardens the Wateen B2B2C RBAC system by:

1. **IsAgencyAdmin permission**: Now requires verified agency status, not just the role.
2. **Role escalation prevention**: Public registration only allows PATIENT and AGENCY_ADMIN roles.
3. **Data migration**: Already in place — maps legacy P2P roles to B2B2C roles.

## Files Changed

| File                   | Change                                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| `users/permissions.py` | `IsAgencyAdmin` — add verified agency check; `IsAgencyAdminOrSuperAdmin` — update for consistency |
| `users/serializers.py` | `UserRegistrationSerializer` — add `validate_role()` to restrict to PATIENT/AGENCY_ADMIN          |

## Files NOT Changed (already correct)

| File                                              | Why                                       |
| ------------------------------------------------- | ----------------------------------------- |
| `users/models.py`                                 | No schema changes needed                  |
| `users/migrations/0004_refactor_userrole_enum.py` | Migration already correctly implemented   |
| `users/serializers.py` → `UserProfileSerializer`  | `role` already in `read_only_fields`      |
| `users/serializers.py` → `UserUpdateSerializer`   | `role` not in `fields` — already excluded |

## How to Verify

```bash
# Run all user tests
python -m pytest users/tests.py -v

# Run specific RBAC tests (once added)
python -m pytest users/tests.py -v -k "RBAC or role_escalation or agency_admin_permission"
```

## Key Design Decisions

- **Stateless checks**: `IsAgencyAdmin` re-evaluates agency status on every request — no caching.
- **Serializer-level validation**: Role restriction happens in the serializer, not the view, following DRF best practices.
- **Arabic error messages**: All new error messages are in Arabic per the platform's Arabic-first policy.
