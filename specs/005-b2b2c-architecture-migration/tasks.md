---
description: "Task list template for feature implementation"
---

# Tasks: B2B2C Architecture Migration

**Input**: Design documents from `/specs/005-b2b2c-architecture-migration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize React frontend with `react-map-gl` Mapbox GL JS dependencies
- [ ] T002 Configure Stripe Connect API keys and Escrow logic in backend environment mapping
- [ ] T003 [P] Setup testing frameworks (`pytest-django`, `locust` for WS, `jest`/RTL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Generate database migration for `AGENCY_PROFILE` and `VISIT` models in `backend/src/users/models.py` and `backend/src/visits/models.py`
- [ ] T005 Update `NURSE_PROFILE` model to include `agency_id` ForeignKey in `backend/src/users/models.py`
- [ ] T006 Create data migration script to move existing P2P nurses to "Wateen Internal Agency" to prevent data loss
- [ ] T007 [P] Implement role-based access control (RBAC) middleware for SuperAdmin, AgencyAdmin, Nurse, Patient in Django
- [ ] T008 [P] Update JWT token generation to embed `agency_id` claims

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Agency Onboarding & Verification (Priority: P1) 🎯 MVP

**Goal**: SuperAdmins digitally onboard, verify, and approve Agencies via React Admin panel.

**Independent Test**: Register an agency, verify it as SuperAdmin, and observe the status change to `verified`.

### Implementation for User Story 1

- [ ] T009 [P] [US1] Create REST API endpoints for Agency registration (upload Tax ID, Registry, MoH License) in `backend/src/users/api.py`
- [ ] T010 [P] [US1] Create REST API endpoint for SuperAdmin to approve/reject Agencies in `backend/src/users/api.py`
- [ ] T011 [US1] Implement Agency Onboarding UI forms in `frontend/src/app/(admin)/agencies/onboarding/page.tsx`
- [ ] T012 [US1] Implement SuperAdmin review queue UI in `frontend/src/app/(admin)/agencies/review/page.tsx`
- [ ] T013 [P] [US1] Write integration tests for Agency registration and approval flow in `backend/tests/integration/test_agency_onboarding.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Agency Defines Coverage Geography (Priority: P1)

**Goal**: Agency Admin draws a coverage polygon on map dashboard.

**Independent Test**: As an Agency Admin, navigate to Settings, draw a polygon on the Mapbox widget, and verify it saves to the PostGIS `coverage_polygon` field.

### Implementation for User Story 2

- [ ] T014 [P] [US2] Implement `POST /api/v1/agency/{agency_id}/coverage/` endpoint in `backend/src/users/api.py`
- [ ] T015 [P] [US2] Create Mapbox interactive widget component using `mapbox-gl-draw` in `frontend/src/components/map/CoverageMap.tsx`
- [ ] T016 [US2] Integrate CoverageMap into Settings page in `frontend/src/app/(b2b)/agency/[id]/settings/page.tsx`
- [ ] T017 [P] [US2] Write unit tests for PostGIS Polygon validation in `backend/tests/unit/test_agency_coverage.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Patient Requests a Visit (Priority: P1)

**Goal**: Patient requests visit, system uses PostGIS ST_Intersects to route to verified agencies.

**Independent Test**: Drop a pin as a patient within an Agency's polygon and verify the payload routes correctly based on the `ST_Intersects` query.

### Implementation for User Story 3

- [ ] T018 [P] [US3] Implement `ST_Intersects` spatial matching query using Django PostGIS ORM in `backend/src/visits/services.py`
- [ ] T019 [US3] Create `POST /api/v1/visits/request/` endpoint to handle patient requests in `backend/src/visits/api.py`
- [ ] T020 [US3] Update Patient mobile/web UI to pass spatial coordinates and handle B2B2C ETA responses in `frontend/src/app/(patient)/request/page.tsx`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Agency Dispatch Protocol (Manual vs Auto) (Priority: P1)

**Goal**: Respect `AUTO` vs `MANUAL` dispatch modes with WebSocket push or dashboard review queue.

**Independent Test**: Route a request to an AUTO agency (verify all nurses receive WS event) and a MANUAL agency (verify it enters the dashboard review queue).

### Implementation for User Story 4

- [ ] T021 [P] [US4] Implement WebSocket Channels consumer for nurses (`agency_{id}_nurses`) and admins (`agency_{id}_admins`) in `backend/src/visits/consumers.py`
- [ ] T022 [US4] Implement Dispatch Engine logic (Auto-dispatch broadcast vs Manual pending queue) in `backend/src/visits/services.py`
- [ ] T023 [P] [US4] Implement `POST /api/v1/agency/{agency_id}/dispatch/manual/` endpoint in `backend/src/visits/api.py`
- [ ] T024 [P] [US4] Implement `GET /api/v1/agency/{agency_id}/dashboard/overview` endpoint in `backend/src/visits/api.py`
- [ ] T025 [US4] Build Real-Time B2B Dashboard map and review queue UI in `frontend/src/app/(b2b)/agency/[id]/dashboard/page.tsx`
- [ ] T026 [US4] Create Celery task `re_route_visit` for 180s timeouts in `backend/src/visits/tasks.py`

---

## Phase 7: User Story 5 - Escrow and Financial Settlement (Priority: P2)

**Goal**: Hold patient payment in escrow, deduct take rate, credit agency wallet via Stripe Connect.

**Independent Test**: Complete a visit and verify Escrow funds are split precisely via Stripe Destination Charges.

### Implementation for User Story 5

- [ ] T027 [P] [US5] Create `TRANSACTION` model in `backend/src/financials/models.py`
- [ ] T028 [US5] Implement Stripe Connect Destination Charges for payment collection during visit request in `backend/src/financials/services.py`
- [ ] T029 [US5] Create Celery task to calculate Wateen Take Rate and update status to `settled` on visit completion in `backend/src/financials/tasks.py`
- [ ] T030 [P] [US5] Write contract tests for Stripe Connect integrations in `backend/tests/contract/test_stripe_escrow.py`

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T031 [P] E2E locust load test for 5000 concurrent Nurse WS connections
- [ ] T032 Update API documentation (Swagger/OpenAPI)
- [ ] T033 Run idempotency script on staging database to verify zero data loss

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### Parallel Opportunities

- All Setup and Foundational tasks marked [P] can run in parallel.
- User Stories 1, 2, 3, and 4 are high-priority (P1) and can be executed independently post-Foundations.
- `api.py` and `services.py` API endpoint generations (T009, T010, T014, T023, T024) can be split among backend developers.
- Mapbox integration (T015, T016) can run concurrently with Setup Tasks.
