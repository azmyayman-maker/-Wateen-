# Task Identification

Task ID: 2.4
Task Name: Pricing Engine (AI-Ready Foundation)
Status: Pending
Assigned Execution Agent: OpenCode
Assigned Review Authority: Kilo Code

## 1) Context & Objective

**Objective:** Implement a professional, modular pricing engine for the Wateen platform that is "AI-Ready". The system must support rule-based pricing initially but allow seamless switching to ML-based strategies in the future.

**Context:**
The current pricing logic needs to be decoupled from hardcoded values. We introduce a `PricingStrategy` pattern and a dynamic configuration model (`PricingFactor`) to allow admins to adjust pricing variables without code deployment. Additionally, specific data points (time, location, service type) must be logged during estimate requests to build a dataset for future ML model training.

## 2) Technical Specifications

### Target Files

- `visits/models.py`: [MODIFY] Add `ServiceType`, `PricingFactor`, update `Visit`.
- `visits/services/pricing.py`: [NEW] Implement Strategy Pattern for pricing.
- `visits/signals.py`: [NEW/MODIFY] Implement data logging for AI.
- `visits/api.py`: [NEW] Implement `POST /api/visits/estimate/` API.
- `visits/urls.py`: [MODIFY] Register new API endpoints.
- `visits/payment_mock.py`: [NEW] Implememt simple mock webhook.
- `visits/tests/test_pricing.py`: [NEW] Unit tests for pricing logic and API.

### Architecture Rules

- **Strategy Pattern**: Use the Strategy Pattern for pricing logic to ensure modularity.
- **Separation of Concerns**: Pricing logic resides in `services/pricing.py`, not in views or models.
- **Data Driven**: Pricing variables must be fetched from the database (`PricingFactor`), not hardcoded.
- **AI Readiness**: Ensure all necessary data fields for future ML training are present and populated.

### Technology Stack

- **Backend**: Django, Django REST Framework (DRF).
- **Language**: Python 3.x.
- **Database**: PostgreSQL (via Django ORM).

## 3) Implementation Steps

1.  **Define Models (`visits/models.py`)**:
    - Create `ServiceType` model with `name`, `base_price`, `description`.
    - Create `PricingFactor` model with `key` (unique), `value` (Decimal), `description`.
    - Update `Visit` model with `base_price`, `distance_fee`, `time_multiplier`, `ai_surge_coefficient` (default 1.0), `final_price`.
    - Create and run migrations.

2.  **Implement Pricing Logic (`visits/services/pricing.py`)**:
    - Define abstract `PricingStrategy` interface with an `calculate_price(visit_data)` method.
    - Implement `RuleBasedPricingStrategy` inheriting from `PricingStrategy`.
      - Logic: `(Base + (Distance * PerKm)) * NightMultiplier`.
      - Retrieve `PerKm`, `NightMultiplier`, etc., from `PricingFactor` (use sensible defaults if missing, e.g., 50 EGP).
    - Add comments/placeholders for future `MLPricingStrategy`.

3.  **Implement Data Collection (`visits/signals.py`)**:
    - Create a signal or service method to log `request_time`, `location`, and `service_type` whenever a price estimate is requested. This ensures valid training data is captured.

4.  **Implement API (`visits/api.py` & `visits/urls.py`)**:
    - Create `EstimateView` (APIView).
    - Endpoint: `POST /api/visits/estimate/`.
    - Input: `service_type_id`, `location` (lat/long), `time`.
    - Logic: Instantiate `RuleBasedPricingStrategy`, calculate price, and return a detailed breakdown (base, distance, fees, final).

5.  **Implement Mock Payment (`visits/payment_mock.py`)**:
    - Create a simple view `POST /api/payments/webhook/mock/` that accepts a payment status and updates the visit status accordingly (for testing purposes).

6.  **Verify & Test (`visits/tests/test_pricing.py`)**:
    - Write unit tests for `RuleBasedPricingStrategy` to verify calculations with different factors.
    - Write integration test for the `estimate` API endpoint.

## 4) Definition of Done (DoD)

### Functional Validation

- [ ] `ServiceType` and `PricingFactor` models are created and accessible via Admin.
- [ ] `Visit` model includes all new fields.
- [ ] `PricingStrategy` logic correctly calculates price based on DB factors.
- [ ] `POST /api/visits/estimate/` returns correct JSON breakdown.
- [ ] Data is logged for AI training purposes upon estimate request.
- [ ] Mock payment webhook functions correctly.

### Architectural Compliance

- [ ] Strict separation of pricing logic into `services/pricing.py`.
- [ ] No hardcoded pricing values in code.
- [ ] `PricingStrategy` interface is strictly followed.

### Standards Compliance

- [ ] Code follows PEP8 and project linting rules.
- [ ] All new code is covered by tests.

## 5) Acceptance Authority

- **Reviewer**: Kilo Code
- **Criteria**: Full compliance with specifications and architecture.
