# Feature Specification: Pricing Engine (AI-Ready Foundation)

**Feature Branch**: `001-pricing-engine`  
**Created**: 2026-02-18  
**Status**: Draft  
**Input**: User description: "Implement a professional, modular pricing engine for the Wateen platform that is AI-Ready, supporting rule-based pricing initially with seamless switching to ML-based strategies in the future."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Request Price Estimate (Priority: P1)

A customer wants to know the cost of a service visit before booking. They provide their location and the type of service needed, and the system returns a detailed price breakdown including base price, distance fee, time-based adjustments, and final total.

**Why this priority**: This is the core value proposition - customers cannot make booking decisions without knowing the price. Without this, the platform cannot function commercially.

**Independent Test**: Can be fully tested by submitting a POST request with service type, location, and time to the estimate endpoint and receiving a complete price breakdown in response.

**Acceptance Scenarios**:

1. **Given** a customer selects a service type and location, **When** they request a price estimate, **Then** the system returns a breakdown showing base price, distance fee, time multiplier, and final price
2. **Given** a customer requests an estimate during night hours, **When** the system calculates the price, **Then** a night multiplier is applied and clearly shown in the breakdown
3. **Given** a customer is located far from service providers, **When** the estimate is calculated, **Then** the distance fee accurately reflects the additional cost

---

### User Story 2 - Admin Configure Pricing Factors (Priority: P1)

An administrator needs to adjust pricing variables (per-kilometer rate, night multiplier, surge coefficients) without requiring code changes or developer intervention. They access an admin interface to modify these values, and the changes take effect immediately for new estimates.

**Why this priority**: Business agility depends on being able to adjust pricing dynamically. Hardcoded values require developer time and code deployments for simple business changes.

**Independent Test**: Can be fully tested by modifying a pricing factor through the admin interface and verifying that subsequent estimates reflect the new value.

**Acceptance Scenarios**:

1. **Given** an admin is logged into the admin panel, **When** they navigate to Pricing Factors and update the per-kilometer rate, **Then** new estimates use the updated rate immediately
2. **Given** multiple pricing factors exist, **When** an admin updates any factor, **Then** only that factor changes without affecting others
3. **Given** an admin tries to create a duplicate pricing factor key, **When** they submit the form, **Then** the system rejects the duplicate and shows an error message

---

### User Story 3 - Capture AI Training Data (Priority: P2)

The system automatically logs data points (request time, location, service type, calculated price components) every time an estimate is requested. This builds a dataset for future machine learning model training without requiring additional user action.

**Why this priority**: This enables future ML capabilities without impacting current users. It's preparation work that doesn't block the primary pricing functionality.

**Independent Test**: Can be fully tested by requesting multiple estimates with varying inputs and verifying that each request creates a corresponding log entry with all required fields populated.

**Acceptance Scenarios**:

1. **Given** a customer requests a price estimate, **When** the estimate is calculated, **Then** a log entry is created with request timestamp, location coordinates, service type, and all price components
2. **Given** the AI training log exists, **When** administrators or data scientists query the data, **Then** all fields needed for ML model training are present and accurate

---

### User Story 4 - Mock Payment Webhook (Priority: P3)

During testing and development, a mock payment endpoint simulates payment callbacks. This allows testers to verify the flow from estimate to booking to payment confirmation without integrating with a real payment provider.

**Why this priority**: This is a development/testing convenience that enables verification of the payment flow but is not required for the core pricing functionality.

**Independent Test**: Can be fully tested by posting a mock payment status to the webhook endpoint and verifying that the associated visit status updates correctly.

**Acceptance Scenarios**:

1. **Given** a visit exists with pending payment status, **When** a mock webhook receives a successful payment notification, **Then** the visit status updates to paid/confirmed
2. **Given** a mock webhook receives a failed payment notification, **When** the webhook processes it, **Then** the visit status reflects the payment failure

---

### Edge Cases

- What happens when a PricingFactor is missing from the database? System uses sensible defaults (e.g., 50 EGP for per-km rate)
- What happens when location coordinates are invalid or missing? System returns an error indicating valid location is required
- What happens when a non-existent service type is requested? System returns a clear error indicating the service type is not available
- What happens when concurrent requests update the same pricing factor? Last write wins (standard database behavior)
- What happens when the estimate request rate spikes? System continues processing; rate limiting not in scope for this phase

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a public endpoint (no authentication required) to request price estimates given service type, location, and time, with IP-based rate limiting to prevent abuse
- **FR-002**: System MUST calculate price using the formula: (Base Price + (Distance × PerKm Rate)) × Time Multiplier
- **FR-003**: System MUST retrieve all pricing variables (per-km rate, night multiplier, etc.) from a configurable data store
- **FR-004**: System MUST allow administrators to create, read, update, and delete pricing factors via an admin interface
- **FR-005**: System MUST support multiple service types, each with its own base price
- **FR-006**: System MUST return a detailed price breakdown showing base price, distance fee, time multiplier, and final price
- **FR-007**: System MUST log estimate request data including timestamp, location, service type, and calculated price components for future ML training
- **FR-008**: System MUST apply time-based multipliers (e.g., night hours) when calculating estimates
- **FR-009**: System MUST use sensible default values when pricing factors are not configured in the database
- **FR-010**: System MUST provide a mock payment webhook endpoint for testing payment flow integration
- **FR-011**: System MUST store pricing data (base_price, distance_fee, time_multiplier, ai_surge_coefficient, final_price) with each visit record

### Key Entities

- **ServiceType**: Represents a category of service (e.g., home repair, consultation) with a name, description, and base price. Multiple visits can reference the same service type.

- **PricingFactor**: Represents a configurable pricing variable with a unique key (e.g., "per_km_rate", "night_multiplier"), decimal value, and description. Used to drive pricing calculations without code changes.

- **Visit**: Represents a service booking with associated pricing data. Contains base price, distance fee, time multiplier, AI surge coefficient (for future ML), and final calculated price.

- **EstimateLog**: Captures data from each estimate request for AI training. Contains request timestamp, location coordinates, service type, and all price components. Data retained for 2 years.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Price estimates return within 2 seconds for 99% of requests under normal load
- **SC-002**: Administrators can update any pricing factor and see changes reflected in estimates within the next request
- **SC-003**: 100% of estimate requests generate a corresponding AI training log entry with all required fields populated
- **SC-004**: Price calculation accuracy is verified through automated tests covering at least 10 different scenarios (various distances, times, service types)
- **SC-005**: Mock payment webhook correctly updates visit status 100% of the time during testing
- **SC-006**: All pricing values in estimates match the configured pricing factors in the database with zero discrepancies

## Clarifications

### Session 2026-02-18

- Q: Is the estimate endpoint public or authenticated? → A: Rate-limited public - no auth but IP-based rate limiting applies
- Q: What is the distance reference point for pricing? → A: Distance from nearest available provider
- Q: How long should EstimateLog data be retained? → A: 2 years - sufficient for ML training cycles

## Assumptions

- Distance calculation is based on straight-line (haversine) distance from the customer location to the nearest available provider; actual routing distance may differ
- "Night hours" are defined as 10 PM to 6 AM local time (configurable via PricingFactor)
- All prices are in Egyptian Pounds (EGP) unless otherwise specified
- The mock payment webhook is for testing only and will be replaced with real payment integration in a future phase
- AI surge coefficient defaults to 1.0 (no surge) and will be populated by ML models in future implementations
- Location is provided as latitude/longitude coordinates; geocoding is not in scope
- Authentication and authorization for admin pricing configuration uses existing Django admin functionality
