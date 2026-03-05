# Implementation Plan: User Role Enum Refactoring

**Feature**: 006-user-role-enum
**Created**: 2026-03-01
**Depends on**: spec.md, research.md, data-model.md

---

## Technical Context

| Aspect              | Detail                                                               |
| ------------------- | -------------------------------------------------------------------- |
| **Framework**       | Django 5.2, Python 3.11+                                             |
| **Affected app**    | `users/`                                                             |
| **Files changed**   | `models.py`, `tests.py`, new migration `0004_*`                      |
| **Files unchanged** | `signals.py`, `views.py`, `serializers.py`, `admin.py`               |
| **Blast radius**    | Contained to `users/` app — no cross-app references to removed roles |

---

## Phase 1: Model Changes (`users/models.py`)

### Step 1.1 — Refactor `UserRole` enum

```diff
 class UserRole(models.TextChoices):
     PATIENT = 'PATIENT', _('Patient')
     NURSE = 'NURSE', _('Nurse')
-    DOCTOR = 'DOCTOR', _('Doctor')
-    ADMIN = 'ADMIN', _('Admin')
     AGENCY_ADMIN = 'AGENCY_ADMIN', _('Agency Admin')
+    SUPERADMIN = 'SUPERADMIN', _('Super Admin')
```

### Step 1.2 — Update `create_superuser()` default

```diff
-        extra_fields.setdefault('role', UserRole.ADMIN)
+        extra_fields.setdefault('role', UserRole.SUPERADMIN)
```

### Step 1.3 — Replace `is_doctor` property, add new ones

```diff
     @property
-    def is_doctor(self) -> bool:
-        return self.role == UserRole.DOCTOR
+    def is_agency_admin(self) -> bool:
+        return self.role == UserRole.AGENCY_ADMIN
+
+    @property
+    def is_superadmin(self) -> bool:
+        return self.role == UserRole.SUPERADMIN
```

### Step 1.4 — Update `is_admin_user` logic

```diff
     @property
    def is_admin_user(self):
        # Was previously used internally. Now requires superadmin or superuser.
        return self.role == UserRole.SUPERADMIN or self.is_superuser
```

---

## Phase 2: Data Migration

### Step 2.1 — Create `0004_refactor_userrole_enum.py`

- `RunPython`: `ADMIN` → `SUPERADMIN`, `DOCTOR` → `NURSE`
- **`CustomUser` Migration**:
  - `RunPython`: `ADMIN` → `SUPERADMIN`, `DOCTOR` → `NURSE`
  - Reverse: `SUPERADMIN` → `ADMIN` (DOCTOR reverse is lossy — acceptable)

---

## Phase 3: Test Updates (`users/tests.py`)

| Test                                     | Change                                                                    |
| ---------------------------------------- | ------------------------------------------------------------------------- |
| `test_create_superuser_success` (L187)   | Assert `'SUPERADMIN'` instead of `'ADMIN'`                                |
| `test_user_role_properties` (L406-444)   | Remove doctor user + assertions; add agency_admin + superadmin assertions |
| `test_no_profile_for_doctor_role` (L941) | Rename → `test_no_profile_for_superadmin_role`                            |
| `test_no_profile_for_admin_role` (L956)  | Rename → `test_no_profile_for_agency_admin_role`                          |

---

## Verification

```bash
python manage.py migrate users
python manage.py test users -v 2
python manage.py makemigrations --check --dry-run
```
