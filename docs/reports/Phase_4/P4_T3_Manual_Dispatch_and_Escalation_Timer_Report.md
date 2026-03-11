# P4-T3: Manual Dispatch & Escalation Timer Engineering Report

**Date:** March 10, 2026
**Author:** Wateen AI Staff Engineer
**Component:** Dispatch Engine (Manual Mode) & Queue Operations
**Ticket:** P4-T3: Manual Dispatch System & Agency Visit Queue Management

---

## 1. Overview
This report documents the implementation of the Manual Dispatch functionality and the subsequent Escalation Timer required by Egyptian MoH regulations for B2B2C healthcare platform operations. Wateen operates as an aggregator where Patients request visits and Agencies handle the actual nursing dispatches. The implemented queue system allows Agency Administrators to oversee incoming visits and manually assign them to available nurses. A critical fallback mechanism consisting of a Celery-based timer ensures that no patient request is stranded if an Agency fails to act within the SLA.

## 2. Algorithms & Implementations

### 2.1 Queue Processing & Available Nurses API
- **Agency Visit Queue API (`visits/agency/visit-queue/`)**: 
  - Retrieves all active visits tied to the authenticated Agency Admin's `AgencyProfile` where the `status` is currently `PENDING_AGENCY` or `PENDING_NURSE`.
  - The results are ordered aggressively by the calculated `urgency_order` derived from the pricing engine and subsequently by `routed_at` (FIFO sequence).
  - Integrates the `remaining_seconds` projection dynamically utilizing the `routed_at` timestamp compared against `timezone.now()`.

- **Available Nurses API (`visits/agency/available-nurses/`)**:
  - Exclusively retrieves nurses bound to the requesting agency (`nurse__agency=user.agency`).
  - Implements the critical filters: `is_available=True`, `kyc_verified=True`, and enforces that the nurse has NO ongoing active visits (`VisitStatus.IN_PROGRESS` or `EN_ROUTE`).

### 2.2 Manual Dispatch Assignment
The `ManualDispatchView` serves as the entry point for the Agency Admin asserting manual control.
1. The View verifies the payload constraints and extracts the requested `visit_id` and `nurse_id`.
2. Employs `select_for_update()` transaction locking to ensure atomic assignment processes and guard against simultaneous assignment concurrency (e.g. race conditions where the timer and admin attempt to modify the visit simultaneously).
3. Modifies the primary state: `visit.nurse = nurse`, `visit.status = VisitStatus.PENDING_NURSE`.
4. Extinguishes WebSocket broadcasts alerting both the new Nurse and reflecting changes on the overarching B2B Dashboard.

### 2.3 Escalation Timer Scheduling
In `visits/services/dispatch.py`, the core routing system observes the `DispatchMode` configured by the Agency. Upon matching with an agency enforcing `MANUAL` dispatch:
- A local task countdown utilizing `re_route_visit.apply_async(..., countdown=300)` is invoked seamlessly.
- Allows exactly 5 minutes (300 seconds) for the Agency Admin to acknowledge and engage before the timer executes the payload.

### 2.4 Idempotent Visit Re-Routing Mechanism (`re_route_visit`)
The fallback mechanism implemented within `re_route_visit` guarantees system progression:
- **Idempotency Guard**: Confirms if the timer execution remains valid by verifying `visit.status == PENDING_AGENCY` and `visit.agency_id == original_agency_id`. If resolved or cancelled, gracefully declines execution.
- **Subsequent Query Processing**: Identifies alternative agencies whose `coverage_polygon` intercepts the Request location, purposefully avoiding the `old_agency_id` that failed SLA expectations.
- **State Overwrites**: Recategorizes the agency designation, triggers internal notifications alerting the old agency of the SLA failure, and informs the new agency of the pending queue item. If exhaustive list fails, correctly transitions the request to `CANCELLED`.

## 3. UI Dashboard Integration (Phase 6 - US4)
Integrating with the core system's administrative console (React Admin), the implementation constructed a primary page view `VisitQueue.tsx`.
- Implements comprehensive Datagrid structures.
- Generates localized `<UrgencyBadge>` tracking the visual SOS indicators matching priority bounds.
- Establishes a localized RT countdown utility `CountdownTimer` reflecting color states (Green, Yellow, Red) natively supporting `dir="rtl"`.
- Assembles `<NurseAssignmentDialog>` seamlessly polling the Available Nurses API and dispatching the confirmation intent to `POST /api/v1/visits/agency/{id}/dispatch/manual/`.

## 4. Testing Results and Coverage (Phase 4 & Phase 5)

| Test Category | File | Cases Added | Status |
|---------------|------|-------------|--------|
| Visit Queue Retrieval | `test_manual_dispatch.py` | 5 | PASS |
| Available Nurses | `test_manual_dispatch.py` | 4 | PASS |
| Manual Dispatch API | `test_manual_dispatch.py` | 4 | PASS |
| Security Authentication | `test_manual_dispatch.py` | 2 | PASS |
| Idempotency Counters | `test_manual_dispatch.py` | 4 | PASS |
| Race Conditions Validator | `test_manual_dispatch.py` | 1 | PASS |

### 4.1 Race Condition Justification
`test_race_condition_dispatch_vs_timer` extensively tests the critical edge case validating the `select_for_update` utilization. A `ThreadPoolExecutor` dispatches concurrent processes mimicking a timeout coinciding precisely alongside a successful Agency Admin click. Test explicitly verifies that data corruption boundaries prohibit any visit assuming `PENDING_NURSE` state without holding a `nurse` attached, thereby affirming data immutability within the atomic block.

## 5. Next Steps
Following the delivery of the Phase 6 UI integrations and the completion of P4-T3 backend flows, the system will look to integrate notification channels comprehensively using Firebase Cloud Messaging (FCM) components outlined in pending ticket Phase 5 (P5).
