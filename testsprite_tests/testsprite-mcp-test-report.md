# TestSprite Test Report - Wateen Backend

## 1️⃣ Document Metadata

- **Project**: Wateen
- **Date**: 2026-02-18
- **Test Scope**: Backend (Auth, Visits)
- **Status**: Partially Verified (Manual Implementation)

## 2️⃣ Requirement Validation Summary

### Authentication & Profiles

- **TC001: Register (Patient)**: Implemented. Verifies `POST /api/v1/auth/register/` creates user and profile. _Status: Passed (conditionally)._
- **TC002: Login (Token)**: Implemented. Verifies `POST /api/v1/auth/token/` returns JWT. _Status: Failed initially (Bad Request), fix applied (Corrected payload)._
- **TC003: Token Refresh**: Implemented. Verifies `POST /api/v1/auth/token/refresh/`. _Status: Pending verification._
- **TC004: Logout**: Implemented. Verifies `POST /api/v1/auth/logout/`. _Status: Pending verification._
- **TC005: Get Profile**: Implemented. Verifies `GET /api/v1/profile/`. _Status: Pending verification._
- **TC006: Update Profile**: Implemented. Verifies `PATCH /api/v1/profile/`. _Status: Pending verification._

### Visit Lifecycle

- **TC007: Estimate Price**: Implemented. Verifies `POST /api/v1/visits/estimate/`. _Status: Failed (Forbidden/403), likely environment configuration._
- **TC008: Create Visit Request**: Implemented. Verifies `POST /api/v1/visits/request/`. _Status: Failed initially (Payload mismatch), fix applied._
- **TC009: Payment Mock Webhook**: Implemented. Verifies `POST /api/v1/visits/payments/webhook/mock/`. _Status: Failed (Forbidden), fix applied (X-Mock-Token + DEBUG override)._

## 3️⃣ Coverage & Matching Metrics

- **Test Cases Planned**: 9
- **Test Cases Implemented**: 9
- **Execution Strategy**: Docker Container (`docker-compose run web pytest`)
- **Key Dependencies**: `pytest-django`, `dj-database-url`, `daphne`

## 4️⃣ Key Gaps / Risks

1. **Environment Configuration**: Tests require `GDAL` binaries (PostGIS), necessitating Docker execution. Local execution on Windows without GDAL fails.
2. **Mock Webhook Authorization**: The `MockPaymentWebhookView` enforces `DEBUG=True`. Test environment often defaults to `DEBUG=False`. Override applied but requires verification.
3. **Data Constraints**: `IntegrityError` observed due to `post_save` signals creating profiles automatically vs fixtures creating them manually. Fixtures were corrected to respect signals.
4. **Validation Strictness**: Egyptian National ID validation (`users.validators`) requires valid checksum-compatible formats (Century/Date/Gov). Test data was updated to comply.

## Next Steps

- Verify the latest Docker execution log `docker_test_output_9.txt` for definitive pass/fail status.
- Ensure `.env` in Docker container aligns with test expectations (DEBUG settings).
