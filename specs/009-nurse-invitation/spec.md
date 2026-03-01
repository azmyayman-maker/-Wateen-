# Feature Specification: Nurse Invitation Flow

**Feature Branch**: `009-nurse-invitation`  
**Created**: 2026-03-01  
**Status**: Active  
**Input**: User description: "Implementing the cryptographic Nurse Invitation Flow and secure serializers against cross-agency hijacking (IDOR)."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Agency Admin Invites Nurse (Priority: P1)

Agency Admins need a way to securely invite nurses to their agency, ensuring the nurse is inextricably bound to the agency.

**Why this priority**: Without this, agencies cannot onboard the primary service providers to the platform.

**Independent Test**: Can be fully tested by authenticating an `AGENCY_ADMIN` and hitting the `POST /api/v1/agencies/invite-nurse/` endpoint with a phone number, expecting a cryptographic token in return.

**Acceptance Scenarios**:

1. **Given** an authenticated agency admin, **When** they POST to the invite endpoint with a phone number, **Then** a 72-hour valid UUID token is returned.
2. **Given** a patient or unauthorized user, **When** they attempt to POST to the endpoint, **Then** a `403 Forbidden` error is returned.

---

### User Story 2 - Nurse Accepts Invitation (Priority: P1)

Nurses need to accept the invitation using the cryptographic token to register and become active in the system under the agency.

**Why this priority**: The invitation flow is useless if the nurse cannot consume the token and register.

**Independent Test**: Can be fully tested by POSTing valid credentials and a valid token to `POST /api/v1/auth/accept-invitation/`, checking that the `CustomUser` and `NurseProfile` are atomically created and bound to the agency.

**Acceptance Scenarios**:

1. **Given** a valid token and valid user details, **When** POSTing to the accept endpoint, **Then** the nurse is registered securely under the exact agency that issued the token.
2. **Given** an expired token, **When** POSTing to the accept endpoint, **Then** a `410/400` error is returned.

---

### Edge Cases

- What happens when a user submits an arbitrary string instead of a UUID token? The system handles this gracefully returning a 400 error.
- How does system handle creating a user if the National ID is already in use? The system will utilize `transaction.atomic` to completely rollback any partial profile creations and will return a validation error.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST allow Agency Admins to generate 72-hour cryptographic tokens mapped to their agency.
- **FR-002**: System MUST validate Egyptian National IDs (14 digits) during registration.
- **FR-003**: System MUST securely attribute the newly registered nurse ONLY to the inviting agency (IDOR prevention).
- **FR-004**: System MUST perform registration atomically to prevent dangling `CustomUser` records without a `NurseProfile`.

### Key Entities

- **NurseProfile**: Extended user profile for Nurses including syndicate data, documents, and a hard constraint `ForeignKey` to `AgencyProfile`.
- **NurseInvitation**: Cryptographic tracking model storing the token, agency reference, expiration, and status.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% test coverage on IDOR prevention inside the Nurse Invitation view.
- **SC-002**: Zero dangling profiles in the database after failed registrations due to the implementation of `transaction.atomic`.
- **SC-003**: Secure registration APIs are deployed with HTTP 201 statuses and proper cryptographic expirations.
