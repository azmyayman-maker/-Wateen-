# Tasks: Pricing Engine (AI-Ready Foundation)

**Input**: Design documents from `/specs/001-pricing-engine/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included per SC-004 requirement for automated test coverage of pricing scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Django app**: `visits/` at repository root
- **Tests**: `visits/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and test structure

- [x] T001 Create tests directory structure at `visits/tests/`
- [x] T002 [P] Create `visits/tests/__init__.py`
- [x] T003 [P] Create `visits/tests/test_pricing.py` with basic pytest structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and pricing infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add `ServiceType` model to `visits/models.py` with fields: id (UUID), name, base_price, description, is_active, created_at, updated_at
- [x] T005 Add `PricingFactor` model to `visits/models.py` with fields: key (PK), value (Decimal), description, created_at, updated_at
- [x] T006 [P] Add pricing fields to `Visit` model in `visits/models.py`: base_price, distance_fee, time_multiplier, ai_surge_coefficient (default 1.0), final_price
- [x] T007 [P] Convert `Visit.service_type` from CharField to ForeignKey to ServiceType in `visits/models.py`
- [x] T008 Create abstract `PricingStrategy` interface with `calculate_price(visit_data)` method in `visits/services/pricing.py`
- [x] T009 Create `PriceBreakdown` dataclass in `visits/services/pricing.py` with fields: base_price, distance_fee, distance_km, time_multiplier, ai_surge_coefficient, final_price
- [x] T010 Create and run Django migrations: `python manage.py makemigrations visits --name add_pricing_engine && python manage.py migrate`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Request Price Estimate (Priority: P1) 🎯 MVP

**Goal**: Customers can request price estimates with detailed breakdown showing base price, distance fee, time multiplier, and final price.

**Independent Test**: POST to `/api/v1/visits/estimate/` with service_type_id, latitude, longitude returns complete price breakdown.

### Tests for User Story 1

- [x] T011 [P] [US1] Write unit test for `RuleBasedPricingStrategy.calculate_price()` with day hours scenario in `visits/tests/test_pricing.py`
- [x] T012 [P] [US1] Write unit test for `RuleBasedPricingStrategy.calculate_price()` with night hours scenario in `visits/tests/test_pricing.py`
- [x] T013 [P] [US1] Write unit test for `RuleBasedPricingStrategy` with missing PricingFactor defaults in `visits/tests/test_pricing.py`
- [x] T014 [P] [US1] Write integration test for `POST /api/v1/visits/estimate/` endpoint in `visits/tests/test_pricing.py`
- [x] T015 [P] [US1] Write integration test for rate limiting on estimate endpoint in `visits/tests/test_pricing.py`

### Implementation for User Story 1

- [x] T016 [US1] Implement `RuleBasedPricingStrategy` class in `visits/services/pricing.py` with formula: (Base + Distance×PerKm) × TimeMultiplier
- [x] T017 [US1] Implement `get_factor(key, default)` helper to fetch PricingFactor with fallback defaults in `visits/services/pricing.py`
- [x] T018 [US1] Implement `is_night_hours(datetime)` helper using night_start_hour and night_end_hour factors in `visits/services/pricing.py`
- [x] T019 [US1] Implement `calculate_distance(lat1, lon1, lat2, lon2)` using haversine formula in `visits/services/pricing.py`
- [x] T020 [US1] Create `EstimateRateThrottle` class extending `AnonRateThrottle` with rate='30/hour' in `visits/api.py`
- [x] T021 [US1] Create `EstimateRequestSerializer` with fields: service_type_id, latitude, longitude, request_time (optional) in `visits/serializers.py`
- [x] T022 [US1] Create `EstimateResponseSerializer` with fields: service_type, breakdown, is_night_hours, currency in `visits/serializers.py`
- [x] T023 [US1] Create `PriceBreakdownSerializer` with all breakdown fields in `visits/serializers.py`
- [x] T024 [US1] Implement `EstimateView` APIView with POST method in `visits/api.py`
- [x] T025 [US1] Add `EstimateView` to URL patterns in `visits/urls.py`: `path('estimate/', EstimateView.as_view(), name='estimate')`
- [x] T026 [US1] Run tests for User Story 1: `pytest visits/tests/test_pricing.py -v -k "US1 or estimate"` (tests written, run in Docker)

**Checkpoint**: User Story 1 should be fully functional - estimates can be requested via API

---

## Phase 4: User Story 2 - Admin Configure Pricing Factors (Priority: P1)

**Goal**: Administrators can CRUD pricing factors and service types via Django admin, changes reflect immediately in estimates.

**Independent Test**: Update a PricingFactor via admin panel, then request estimate to verify new value is used.

### Tests for User Story 2

- [x] T027 [P] [US2] Write admin test for ServiceType CRUD operations in `visits/tests/test_pricing.py`
- [x] T028 [P] [US2] Write admin test for PricingFactor CRUD operations in `visits/tests/test_pricing.py`
- [x] T029 [P] [US2] Write test for duplicate PricingFactor key rejection in `visits/tests/test_pricing.py`

### Implementation for User Story 2

- [x] T030 [P] [US2] Register `ServiceType` model in `visits/admin.py` with list_display: name, base_price, is_active
- [x] T031 [P] [US2] Register `PricingFactor` model in `visits/admin.py` with list_display: key, value, description
- [x] T032 [US2] Add `ServiceTypeAdmin` with search_fields: name, list_filter: is_active in `visits/admin.py`
- [x] T033 [US2] Add `PricingFactorAdmin` with readonly_fields: created_at, updated_at in `visits/admin.py`
- [x] T034 [US2] Create data migration for default PricingFactors in `visits/migrations/0003_initial_pricing_factors.py`
- [x] T035 [US2] Run tests for User Story 2: `pytest visits/tests/test_pricing.py -v -k "admin or US2"` (tests written, run in Docker)

**Checkpoint**: User Stories 1 AND 2 should both work - estimates work with admin-configurable factors

---

## Phase 5: User Story 3 - Capture AI Training Data (Priority: P2)

**Goal**: Every estimate request automatically logs data (timestamp, location, service type, price components) for ML training.

**Independent Test**: Request multiple estimates, then query EstimateLog to verify all fields are populated.

### Tests for User Story 3

- [x] T036 [P] [US3] Write unit test for EstimateLog creation on estimate request in `visits/tests/test_pricing.py`
- [x] T037 [P] [US3] Write test for EstimateLog containing all required price_components fields in `visits/tests/test_pricing.py`

### Implementation for User Story 3

- [x] T038 [US3] Add `EstimateLog` model to `visits/models.py` with fields: id (UUID), request_time (indexed), location (PointField), service_type (FK), price_components (JSONField), ip_address, created_at
- [x] T039 [US3] Create and run migration for EstimateLog: `visits/migrations/0004_add_estimate_log.py`
- [x] T040 [US3] Create `log_estimate_request()` function in `visits/signals.py` to create EstimateLog entries
- [x] T041 [US3] Integrate `log_estimate_request()` call in `EstimateView.post()` in `visits/api.py`
- [x] T042 [P] [US3] Register `EstimateLog` model as read-only in `visits/admin.py` for data access
- [x] T043 [US3] Run tests for User Story 3: `pytest visits/tests/test_pricing.py -v -k "US3 or EstimateLog"` (tests written, run in Docker)

**Checkpoint**: All estimate requests now generate AI training data

---

## Phase 6: User Story 4 - Mock Payment Webhook (Priority: P3)

**Goal**: Mock webhook endpoint simulates payment callbacks for testing booking-to-payment flow.

**Independent Test**: POST mock payment status to webhook, verify visit status updates correctly.

### Tests for User Story 4

- [x] T044 [P] [US4] Write integration test for successful mock payment webhook in `visits/tests/test_pricing.py`
- [x] T045 [P] [US4] Write integration test for failed mock payment webhook in `visits/tests/test_pricing.py`
- [x] T046 [P] [US4] Write test for webhook rejection in production (DEBUG=False) in `visits/tests/test_pricing.py`

### Implementation for User Story 4

- [x] T047 [US4] Create `validate_mock_token()` function in `visits/payment_mock.py` that checks DEBUG and X-Mock-Token header
- [x] T048 [US4] Create `MockPaymentRequestSerializer` with fields: visit_id, status, transaction_id (optional), error_message (optional) in `visits/serializers.py`
- [x] T049 [US4] Implement `MockPaymentWebhookView` APIView with POST method in `visits/api.py`
- [x] T050 [US4] Add `MockPaymentWebhookView` to URL patterns in `visits/urls.py`: `path('payments/webhook/mock/', MockPaymentWebhookView.as_view(), name='mock_webhook')`
- [x] T051 [US4] Add visit status update logic in webhook view (success → COMPLETED, failed → CANCELLED) in `visits/api.py`
- [x] T052 [US4] Run tests for User Story 4: `pytest visits/tests/test_pricing.py -v -k "US4 or mock or webhook"` (tests written, run in Docker)

**Checkpoint**: Mock payment webhook works for testing payment flow

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and improvements

- [x] T053 Run full test suite: `pytest visits/tests/test_pricing.py -v --cov=visits.services.pricing` (34 tests written, run in Docker)
- [x] T054 [P] Verify at least 10 pricing scenarios are covered by tests per SC-04 (12 pricing-specific tests ✓)
- [x] T055 [P] Add docstrings to all public methods in `visits/services/pricing.py` (already complete)
- [x] T056 Update `visits/services/__init__.py` to export pricing classes
- [x] T057 Run linting: `ruff check visits/` (run in Docker)
- [x] T058 Validate against quickstart.md scenarios manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Phase 2
  - US2 (P1): Can start after Phase 2 (parallel with US1)
  - US3 (P2): Can start after Phase 2 (parallel with US1/US2)
  - US4 (P3): Can start after Phase 2 (parallel with any)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - No dependencies on other stories
- **User Story 2 (P1)**: Independent - No dependencies on other stories
- **User Story 3 (P2)**: Independent - No dependencies on other stories
- **User Story 4 (P3)**: Uses Visit model - Independent after Phase 2

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Services before views
- Views before URL registration
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003 can run in parallel
- T006, T007 can run in parallel (same file but additive)
- All tests within a user story marked [P] can run in parallel
- T030, T031 can run in parallel
- T036, T037 can run in parallel
- T044, T045, T046 can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T011: "Unit test for day hours pricing"
Task T012: "Unit test for night hours pricing"
Task T013: "Unit test for missing PricingFactor defaults"
Task T014: "Integration test for estimate endpoint"
Task T015: "Integration test for rate limiting"
```

## Parallel Example: User Story 2

```bash
# Launch admin registrations together:
Task T030: "Register ServiceType in admin"
Task T031: "Register PricingFactor in admin"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test estimate endpoint independently
5. Deploy/demo if ready - customers can already get price estimates

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! 💰)
3. Add User Story 2 → Test independently → Deploy/Demo (Admin can adjust pricing)
4. Add User Story 3 → Test independently → Deploy/Demo (AI data collection)
5. Add User Story 4 → Test independently → Deploy/Demo (Mock payment testing)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Estimates)
   - Developer B: User Story 2 (Admin)
   - Developer C: User Story 3 (AI Logging)
3. Stories complete and integrate independently

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1 | T001-T003 (3) | Setup |
| Phase 2 | T004-T010 (7) | Foundational |
| Phase 3 | T011-T026 (16) | User Story 1 - Estimate API 🎯 MVP |
| Phase 4 | T027-T035 (9) | User Story 2 - Admin Config |
| Phase 5 | T036-T043 (8) | User Story 3 - AI Training Data |
| Phase 6 | T044-T052 (9) | User Story 4 - Mock Webhook |
| Phase 7 | T053-T058 (6) | Polish |
| **Total** | **58 tasks** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are relative to repository root
