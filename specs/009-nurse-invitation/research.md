# Research: Nurse Invitation Flow

## Overview

This document outlines the architectural decisions necessary for the Nurse Invitation Flow (Ticket P1-T3), resolving unknowns regarding IDOR prevention and strictly enforcing the B2B2C rules.

## Decisions

### Decision 1: Cryptographic Invitation Tokens

**Decision:** Use `UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)` for invitation tokens.
**Rationale:** UUIDv4 is practically unguessable, making it a cryptographically secure token for registration. Since the accept endpoint is `AllowAny`, the token acts as the sole proof of an agency's authorization. A database index is required for fast lookup during the authorization phase.
**Alternatives considered:** JWT tokens (rejected because we need to easily invalidate, expire, and track state changes like PENDING to ACCEPTED in the DB).

### Decision 2: IDOR Prevention Strategy

**Decision:** Validate user claims explicitly against the `request.user.admin_user` (the AgencyProfile).
**Rationale:** The B2B2C architecture strictly prohibits an Agency Admin from creating data for another agency. By asserting `request.user.role == UserRole.AGENCY_ADMIN` and strictly matching `request.user.admin_user.id == target_agency_id`, we lock down creation at the serializer and view levels.
**Alternatives considered:** Row-Level Security (RLS) in PostgreSQL (too complex for current phase, DRF-level validation is sufficient and explicit).

### Decision 3: Atomic Transaction for Nurse Registration

**Decision:** Wrap the entire Nurse registration (CustomUser creation + NurseProfile creation + NurseInvitation state update) in `@transaction.atomic`.
**Rationale:** Ensures data integrity. If `NurseProfile` fails validation (e.g., missing agency), the `CustomUser` creation is completely rolled back, preventing orphaned users.

### Decision 4: Spatial Context

**Decision:** Store `last_location` as `gis_models.PointField(srid=4326)` with a `GistIndex` in `NurseProfile`.
**Rationale:** Conforms to the project's requirement to utilize PostGIS and SRID 4326 for all spatial queries. GistIndex optimizes matching agencies to patients later in Phase 4.
