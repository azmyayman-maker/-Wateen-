# Engineering Ticket Report: Ticket 1.3

## 1. Ticket Metadata

| Property     | Value                                                   |
| :----------- | :------------------------------------------------------ |
| **ID**       | 1.3                                                     |
| **Title**    | Advanced Auth System Implementation (Custom User & JWT) |
| **Status**   | ✅ Completed & Verified                                 |
| **Assignee** | AI Lead Architect (Antigravity)                         |

## 2. Technical Summary

Implemented a scalable, secure authentication system replacing Django's default User model.

- **Core Logic:** Users login via **Egyptian National ID** (14 digits) instead of username.
- **Identity:** `national_id` is the `USERNAME_FIELD`. Primary key is a **UUID** (`id`).
- **Security:**
  - Integrated `Argon2` password hashing for quantum-resistant security.
  - Implmented `SimpleJWT` for stateless access/refresh token pairs.
  - Hardened `settings.py` to read `SECRET_KEY` and `DEBUG` strictly from environment variables (raising errors in production if missing).
- **Validation:** Added strict regex validators for National ID (checking century, birthdate including leap years, and governorate codes) and Phone Numbers (Egyptian format).

## 3. File Manifest (Created & Modified)

### [NEW] `users/` (Django App structure)

- **`users/models.py`**: Defined `CustomUser` model (extends `AbstractBaseUser`, `PermissionsMixin`) and `CustomUserManager`.
- **`users/validators.py`**: Implemented `validate_egyptian_national_id` and `validate_phone_number` (includes fixes for leap year constraints).
- **`users/serializers.py`**: Created `UserRegistrationSerializer`, `UserProfileSerializer`, and `ChangePasswordSerializer` (Cleaned of redundant uniqueness checks).
- **`users/views.py`**: Implemented `RegisterView`, `UserProfileView`, `ChangePasswordView`, and `LogoutView`.
- **`users/signals.py`**: Empty module created to resolve `AppConfig` import errors.
- **`users/tests.py`**: Comprehensive test suite (46 tests covering validators, Auth flow, User Manager).

### [MODIFIED] Configuration & Docker

- **`config/settings.py`**:
  - Set `AUTH_USER_MODEL = 'users.CustomUser'`.
  - Added `rest_framework`, `users`, `corsheaders` to `INSTALLED_APPS`.
  - Configured `SIMPLE_JWT` (60m access, 7d refresh) and `REST_FRAMEWORK` defaults.
  - **Security Patch:** Added conditional Production Security Headers (HSTS, SSL Redirect, XSS Filter) when `DEBUG=False`.
- **`docker/Dockerfile`**: Added `RUN chmod +x /app/docker/entrypoint.sh` to fix permission startup crashes.
- **`requirements/base.txt`**: Added `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`.

## 4. Configuration Changes

### Environment Variables (`.env`)

- **`SECRET_KEY`**: Required in Production.
- **`DEBUG`**: Defaults to False.
- **`DB_PASSWORD`**: Fallback removed for security.

### Permissions

- **Docker entrypoint**: Now executable (`chmod +x`).

## 5. Verification Steps

### How to Test

```bash
# 1. Rebuild Container (Reflects Dockerfile & Requirement changes)
docker compose -f docker/docker-compose.yml build web

# 2. Start Services
docker compose -f docker/docker-compose.yml up -d

# 3. Apply Migrations (Users app)
docker compose -f docker/docker-compose.yml exec web python manage.py migrate

# 4. Run Test Suite (All 46 tests must pass)
docker compose -f docker/docker-compose.yml exec web python manage.py test users -v 2
```
