# Feature Specification: RBAC Security Hardening

**Feature Branch**: `007-rbac-security-hardening`  
**Created**: 2026-03-01  
**Status**: Draft  
**Input**: User description: "Implement DRF permission IsAgencyAdmin with verified agency check, refine data migration for P2P-to-B2B2C role remapping, and add role escalation prevention in serializers"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Agency Admin Access Gating (Priority: P1)

An Agency Admin who has completed agency verification (status = VERIFIED) attempts to access agency-only endpoints (e.g., nurse management, dispatch settings). The system grants access only if the user's role is AGENCY_ADMIN **and** their linked AgencyProfile has a verified status. If the AgencyProfile does not exist yet (signal failure, race condition) or is not verified (pending, suspended, rejected), access is denied with a clear error message.

**Why this priority**: This is the core security boundary for the B2B layer. Without verified-agency gating, unverified or fraudulent agencies could manage nurses and accept patient visits — a patient safety risk.

**Independent Test**: Can be fully tested by creating users with various agency states (no profile, pending, verified, suspended) and asserting that only authenticated AGENCY_ADMIN users with a VERIFIED agency pass the permission check.

**Acceptance Scenarios**:

1. **Given** an authenticated user with role=AGENCY_ADMIN and agencyprofile.status=VERIFIED, **When** accessing an agency-protected endpoint, **Then** request succeeds (200/201).
2. **Given** an authenticated user with role=AGENCY_ADMIN but agencyprofile.status=PENDING, **When** accessing an agency-protected endpoint, **Then** request is denied (403) with Arabic message.
3. **Given** an authenticated user with role=AGENCY_ADMIN but NO AgencyProfile (signal failed/deleted), **When** accessing an agency-protected endpoint, **Then** request is denied (403) — no crash, no 500.
4. **Given** an authenticated user with role=PATIENT, **When** accessing an agency-protected endpoint, **Then** request is denied (403).
5. **Given** an unauthenticated request, **When** accessing an agency-protected endpoint, **Then** request is denied (401).

---

### User Story 2 - Safe Data Migration from P2P to B2B2C Roles (Priority: P1)

A platform operator runs the data migration to remap legacy P2P roles (ADMIN, DOCTOR) to the new B2B2C enum (SUPERADMIN, NURSE). The migration executes without data loss and includes a reverse function so that the operator can safely roll back if something goes wrong.

**Why this priority**: Data integrity during the P2P → B2B2C transformation is non-negotiable. Incorrect role mapping breaks every permission check in the system.

**Independent Test**: Can be tested by running the migration forward and backward in a test database, verifying role values before and after each direction.

**Acceptance Scenarios**:

1. **Given** users with role=ADMIN in the database, **When** the forward migration runs, **Then** their role becomes SUPERADMIN.
2. **Given** users with role=DOCTOR in the database, **When** the forward migration runs, **Then** their role becomes NURSE.
3. **Given** users with role=PATIENT in the database, **When** the forward migration runs, **Then** their role is unchanged.
4. **Given** the forward migration has run, **When** the reverse migration is executed, **Then** SUPERADMIN → ADMIN and NURSE → DOCTOR, restoring original values.
5. **Given** the migration runs, **When** checking the role field choices, **Then** only PATIENT, NURSE, AGENCY_ADMIN, SUPERADMIN are valid choices.

---

### User Story 3 - Role Escalation Prevention at Registration (Priority: P1)

A user registering via the public API can only select the PATIENT or AGENCY_ADMIN role. Any attempt to register as SUPERADMIN or NURSE via the public endpoint is blocked with a validation error. SUPERADMINs are created via CLI only. Nurses are created via the Agency Invitation Flow only.

**Why this priority**: Privilege escalation is one of the top web vulnerabilities (OWASP A01:2021 Broken Access Control). If a user can self-assign SUPERADMIN, the entire system is compromised.

**Independent Test**: Can be tested by submitting registration requests with each role value and asserting only PATIENT and AGENCY_ADMIN succeed.

**Acceptance Scenarios**:

1. **Given** a registration request with role=PATIENT, **When** submitted to the public register endpoint, **Then** user is created successfully with role=PATIENT.
2. **Given** a registration request with role=AGENCY_ADMIN, **When** submitted to the public register endpoint, **Then** user is created successfully with role=AGENCY_ADMIN.
3. **Given** a registration request with role=SUPERADMIN, **When** submitted to the public register endpoint, **Then** a 400 error with a clear validation message is returned.
4. **Given** a registration request with role=NURSE, **When** submitted to the public register endpoint, **Then** a 400 error is returned explaining nurses are created via agency invitation.
5. **Given** a registration request with no role specified, **When** submitted to the public register endpoint, **Then** user defaults to PATIENT.
6. **Given** an authenticated user editing their profile, **When** they attempt to change their own role field, **Then** the role field is read-only and the change is ignored.

---

### Edge Cases

- What happens when an AGENCY_ADMIN's AgencyProfile is deleted after they were already granted access? → The permission check must re-evaluate on every request (stateless).
- What happens when an AgencyProfile exists but is in SUSPENDED status? → Treated as NOT verified — access denied.
- What happens if the role field receives an invalid string (e.g., "HACKER")? → Django's CharField choices validation rejects it before it reaches our custom logic.
- What happens if a NURSE user tries to update their role to AGENCY_ADMIN via profile update? → The role field is read-only in UserProfileSerializer — change is silently ignored.
- How does the reverse migration handle users who were originally NURSE (not DOCTOR)? → The reverse maps NURSE → DOCTOR. This is documented as lossy for original NURSE users.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST provide an `IsAgencyAdmin` DRF permission class that grants access ONLY to authenticated users with role=AGENCY_ADMIN AND a verified AgencyProfile (status=VERIFIED).
- **FR-002**: The `IsAgencyAdmin` permission MUST handle the case where the AgencyProfile does not exist (via `hasattr` or exception handling) without raising a 500 error.
- **FR-003**: System MUST provide a reversible Django data migration that maps ADMIN → SUPERADMIN and DOCTOR → NURSE using `apps.get_model()` (not direct model imports).
- **FR-004**: The reverse migration function MUST restore SUPERADMIN → ADMIN and NURSE → DOCTOR.
- **FR-005**: System MUST validate the `role` field during user registration to allow ONLY PATIENT and AGENCY_ADMIN as self-registration roles.
- **FR-006**: System MUST reject registration attempts with role=SUPERADMIN or role=NURSE, returning a descriptive validation error.
- **FR-007**: The `role` field in `UserProfileSerializer` MUST be read-only to prevent role changes via profile update.
- **FR-008**: All permission denial messages MUST be in Arabic, consistent with the platform's Arabic-first policy.

### Key Entities

- **CustomUser**: Central user model with `role` field (TextChoices enum: PATIENT, NURSE, AGENCY_ADMIN, SUPERADMIN). Has optional FK to AgencyProfile.
- **AgencyProfile**: B2B tenant profile with `status` field (AgencyStatus enum: pending, verified, suspended, rejected). Linked to CustomUser via FK.
- **UserRole enum**: TextChoices with four canonical values used across all permission and serializer logic.
- **AgencyStatus enum**: TextChoices controlling agency verification state, used by the permission check.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of unauthorized role registration attempts (SUPERADMIN, NURSE) are rejected at the serializer layer — zero privilege escalation paths exist.
- **SC-002**: Agency-protected endpoints return 403 within the same response time as other authenticated endpoints (no measurable latency impact from the defensive AgencyProfile check).
- **SC-003**: The data migration runs forward and backward without data loss on all existing user records.
- **SC-004**: All existing permission-gated views continue to function correctly after the migration — no regressions.
- **SC-005**: The IsAgencyAdmin permission handles the missing-AgencyProfile edge case gracefully (no 500 errors) in 100% of scenarios.
