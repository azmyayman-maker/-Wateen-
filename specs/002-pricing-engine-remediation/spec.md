# Feature Specification: Pricing Engine Remediation

**Feature Branch**: `002-pricing-engine-remediation`  
**Created**: 2026-02-18  
**Status**: Draft  
**Input**: Fix critical logic gaps identified in the Pricing Engine audit. The current implementation relies on hardcoded values and lacks necessary availability checks. We must make the pricing dynamic, timezone-aware, and performant.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accurate Price Estimates Based on Actual Distance (Priority: P1)

As a patient requesting a price estimate, I want the system to calculate pricing based on the actual distance to the nearest available nurse, so that I receive an accurate and fair price estimate.

**Why this priority**: This is the core value proposition - patients need accurate pricing to make informed decisions. The hardcoded 5.0 km distance produces inaccurate estimates.

**Independent Test**: Can be tested by requesting estimates from different locations and verifying the distance varies based on actual nurse locations, not a fixed value.

**Acceptance Scenarios**:

1. **Given** an available and verified nurse exists 2 km from patient location, **When** the patient requests an estimate, **Then** the distance used in pricing is 2 km (not hardcoded 5 km).
2. **Given** multiple available nurses at different distances, **When** the patient requests an estimate, **Then** the system uses the distance to the nearest available nurse.
3. **Given** no available nurses exist in the system, **When** the patient requests an estimate, **Then** the system defaults distance to 0 km (or provides an appropriate fallback message).

---

### User Story 2 - Only Available Nurses Considered for Pricing (Priority: P1)

As a patient, I want price estimates to only consider nurses who are currently available and verified, so that the estimate reflects reality and I won't be quoted a price for an unavailable provider.

**Why this priority**: Pricing based on unavailable nurses is misleading and creates false expectations. This impacts customer trust and operational efficiency.

**Independent Test**: Can be tested by marking nurses as unavailable and verifying they are excluded from pricing calculations.

**Acceptance Scenarios**:

1. **Given** a nurse exists but is marked as unavailable, **When** the patient requests an estimate, **Then** this nurse is not considered in distance calculation.
2. **Given** a nurse exists but is not verified, **When** the patient requests an estimate, **Then** this nurse is not considered in distance calculation.
3. **Given** multiple nurses exist with mixed availability status, **When** the patient requests an estimate, **Then** only available AND verified nurses are considered.

---

### User Story 3 - Correct Night/Day Pricing Based on Local Time (Priority: P2)

As a patient requesting an estimate at 11 PM local time (Cairo), I want the night multiplier applied correctly, so that I am charged the appropriate rate for after-hours service.

**Why this priority**: Incorrect timezone handling leads to wrong pricing, either overcharging or undercharging patients. This has financial and legal implications.

**Independent Test**: Can be tested by making estimates at different times of day and verifying the correct multiplier is applied based on Cairo timezone.

**Acceptance Scenarios**:

1. **Given** the current time in Cairo is 11 PM (23:00), **When** a price estimate is requested without specifying time, **Then** the night multiplier (1.5x) is applied.
2. **Given** the current time in Cairo is 2 AM, **When** a price estimate is requested, **Then** the night multiplier is applied (night hours span 22:00-06:00).
3. **Given** the current time in Cairo is 10 AM, **When** a price estimate is requested, **Then** the day multiplier (1.0x) is applied.

---

### User Story 4 - Responsive Estimate API (Priority: P2)

As a patient using the mobile app, I want the estimate API to respond quickly, so that I don't experience delays when getting price quotes.

**Why this priority**: Synchronous logging blocks the API response, degrading user experience. Non-blocking logging improves perceived performance.

**Independent Test**: Can be tested by measuring API response time with and without logging to verify logging doesn't block the response.

**Acceptance Scenarios**:

1. **Given** a patient requests an estimate, **When** the system logs the request for analytics, **Then** the logging does not block the API response.
2. **Given** the logging operation is slow or fails, **When** the patient receives their estimate, **Then** the estimate response is not delayed by logging issues.

---

### Edge Cases

- What happens when a nurse's location is null or invalid? The nurse should be excluded from distance calculations.
- What happens when the database is temporarily unavailable? The system should gracefully handle the error and either use a fallback or return an appropriate error message.
- What happens when a patient is at an extreme location (far from all nurses)? The distance should still be calculated accurately; no artificial capping.
- What happens at the exact boundary times (22:00:00 and 06:00:00)? The system should correctly identify these as night hours.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate distance to the nearest available nurse dynamically based on actual geographic coordinates.
- **FR-002**: System MUST only consider nurses where `is_available=True` AND `verification_status='VERIFIED'` for pricing calculations.
- **FR-003**: System MUST use timezone-aware datetime objects (Cairo timezone) for all time-based pricing logic.
- **FR-004**: System MUST apply night multiplier (1.5x) for requests between 22:00 and 06:00 Cairo time.
- **FR-005**: System MUST apply day multiplier (1.0x) for requests between 06:00 and 22:00 Cairo time.
- **FR-006**: System MUST perform estimate logging asynchronously (on transaction commit) to avoid blocking the API response.
- **FR-007**: System MUST default distance to 0 km when no available nurses are found, allowing the estimate to still provide a base price.
- **FR-008**: System MUST support spatial queries for efficient distance calculation using PostGIS capabilities.

### Key Entities

- **NurseProfile**: Represents a nurse with availability status (`is_available`), verification status (`verification_status`), and location (`last_location`). Only nurses meeting both availability and verification criteria are considered for pricing.
- **PriceBreakdown**: Contains the breakdown of pricing components including base price, distance, distance fee, time multiplier, and final price. Distance must reflect actual distance to nearest available nurse.
- **EstimateLog**: Records estimate requests for analytics. Logging must not block the main request flow.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Price estimates vary based on actual nurse locations within a 5 km radius show distance variations accurate to within 100 meters.
- **SC-002**: API response time for estimate requests is under 500 milliseconds (excluding logging overhead).
- **SC-003**: Night multiplier is applied 100% of the time for requests made between 22:00-06:00 Cairo time.
- **SC-004**: Day multiplier is applied 100% of the time for requests made between 06:00-22:00 Cairo time.
- **SC-005**: 100% of price estimates use dynamically calculated distance (no hardcoded distance values in production code).
- **SC-006**: Estimate logging completes without affecting API response time (logging happens post-commit).
