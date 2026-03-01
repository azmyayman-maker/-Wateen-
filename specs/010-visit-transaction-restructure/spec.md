# Feature Specification: Visit & Transaction Model Restructuring (P1-T4)

**Feature Branch**: `010-visit-transaction-restructure`  
**Created**: 2026-03-01  
**Status**: Draft  
**Input**: User description: "Restructure Visit and Transaction models with state machine, immutable pricing snapshot, and escrow ledger for P1-T4"

## Assumptions

- The existing `Visit` and `Transaction` models in `visits/models.py` are the starting point; this is a restructuring, not a greenfield rewrite.
- All pricing fields use `DecimalField` (max_digits=10, decimal_places=2) per FinTech precision requirements.
- The `decimal.Decimal` module is used for all financial arithmetic — never `float`.
- Wateen's platform take rate defaults to 15% (agency receives 85%).
- The `Visit.status` field already uses the correct B2B2C states (`PENDING_AGENCY` → `PENDING_NURSE` → `ACCEPTED` → `EN_ROUTE` → `IN_PROGRESS` → `COMPLETED` | `CANCELLED`), as defined by the AGENTS.md core data model.
- Immutable pricing snapshots are enforced at the Django model layer via `save()` override, not at the database constraint layer.
- Foreign key deletion protection (`on_delete=PROTECT`) is used for Visit→Agency, Visit→Nurse, Transaction→Visit, and Transaction→Agency to prevent orphaned financial records.
- The `AgencyProfile` model exists in `users/models.py` with a PostGIS `PolygonField` (`coverage_polygon`) that requires GIS admin registration.
- Arabic `verbose_name` labels are required on all model fields per project convention.
- Paymob is the payment gateway for the Egyptian market (replacing Stripe references in the original ticket).
- Transaction records are created at payment capture time (entering `ESCROWED` status), not at Visit creation. No Transaction exists until the patient pays.
- Field renames use Django `RenameField` migrations to preserve existing data. New fields added with separate data migrations where splits are needed.

## Clarifications

### Session 2026-03-01

- Q: When is the Transaction record created relative to the Visit lifecycle? → A: At payment capture (`ESCROWED` entry point) — no Transaction exists until the patient pays.
- Q: When a Visit is cancelled and an ESCROWED Transaction exists, should it auto-transition to REFUNDED? → A: Conditional — auto-refund only if cancelled before `IN_PROGRESS`; manual review required after.
- Q: Should existing `PENDING` and `FAILED` TransactionStatus values be removed? → A: Yes, remove both. Transaction starts at `ESCROWED` directly at payment capture. `FAILED` is a Stripe-level concern, not a ledger state.
- Q: Should field renames be destructive or data-preserving? → A: Data-preserving `RenameField` migrations where possible, with data migration for field splits.
- Q: Should the Transaction model use Stripe or Paymob as the payment gateway? → A: Paymob — use `paymob_order_id` and `paymob_transaction_id` fields instead of Stripe.

## User Scenarios & Testing _(mandatory)_

### User Story 1 — Visit Lifecycle State Machine (Priority: P1)

A patient requests a home-nursing visit. The system creates a `Visit` record in `PENDING_AGENCY` status. As the visit progresses through dispatch (agency assignment), nurse acceptance, en-route transit, active care, and completion, the `status` field transitions through the defined state machine. Only valid transitions (as defined by the `ALLOWED_TRANSITIONS` map) are permitted. Invalid transitions raise a `ValidationError`.

**Why this priority**: The state machine is the operational backbone of the entire platform. Every downstream feature (dispatch, real-time tracking, payments) depends on Visit status being accurate and tamper-proof.

**Independent Test**: Can be fully tested by creating a Visit fixture and calling `transition_to()` through the happy path and invalid paths, verifying correct transitions succeed and invalid ones raise `ValidationError`.

**Acceptance Scenarios**:

1. **Given** a Visit in `PENDING_AGENCY` status, **When** `transition_to("pending_nurse")` is called, **Then** the status updates to `PENDING_NURSE` and the record is saved.
2. **Given** a Visit in `PENDING_AGENCY` status, **When** `transition_to("completed")` is called, **Then** a `ValidationError` is raised and status remains `PENDING_AGENCY`.
3. **Given** a Visit in `COMPLETED` status, **When** any `transition_to()` is called, **Then** a `ValidationError` is raised (terminal state).
4. **Given** a Visit in `CANCELLED` status, **When** any `transition_to()` is called, **Then** a `ValidationError` is raised (terminal state).

---

### User Story 2 — Immutable Pricing Snapshot (Priority: P1)

When a Visit is first created, the pricing fields (`base_price`, `time_multiplier`, `distance_km`, `distance_rate`, `surge_coefficient`, `final_price`) are set once and frozen. On any subsequent save, if any of these fields have changed from their database values, the system rejects the save with a `ValidationError`. This prevents retroactive price tampering after a patient has committed to a visit.

**Why this priority**: Financial integrity is a regulatory and trust requirement. If pricing can be altered post-creation, it undermines the entire escrow and settlement flow.

**Independent Test**: Can be tested by creating a Visit with pricing, then attempting to modify `final_price` and calling `save()`, verifying that `ValidationError("Pricing snapshot is immutable and cannot be modified after visit creation.")` is raised.

**Acceptance Scenarios**:

1. **Given** a newly created Visit with `final_price=250.00`, **When** the Visit is saved for the first time, **Then** the pricing fields are stored successfully.
2. **Given** an existing Visit (has `pk`), **When** `final_price` is changed from `250.00` to `300.00` and `save()` is called, **Then** a `ValidationError` is raised with the immutability message.
3. **Given** an existing Visit, **When** non-pricing fields (e.g., `status`, `nurse`) are changed and `save()` is called, **Then** the save succeeds without error.

---

### User Story 3 — Transaction / Escrow Ledger (Priority: P1)

When a patient pays for a visit, a `Transaction` record is created linked to the `Visit` and the servicing `Agency`. The system automatically calculates the agency payout as `amount_paid * Decimal('0.85')` (i.e., 85% of the total after Wateen's 15% take rate). The Transaction tracks the payment lifecycle through `ESCROWED` → `SETTLED` | `REFUNDED` states.

**Why this priority**: The financial ledger is the legal proof of payment flow. Without accurate automatic split calculation and escrow tracking, neither Wateen nor agencies can reconcile earnings.

**Independent Test**: Can be tested by creating a Transaction with `amount_paid=Decimal('1000.00')`, verifying `agency_payout` is auto-calculated as `Decimal('850.00')` upon save. Verify that `agency_payout` is non-editable. Verify `settled_at` is set only when status is `SETTLED`.

**Acceptance Scenarios**:

1. **Given** a completed Visit and `amount_paid=1000.00`, **When** a Transaction is saved, **Then** `agency_payout` is automatically calculated as `850.00`.
2. **Given** a Transaction in `ESCROWED` status, **When** the visit completes, **Then** the Transaction can transition to `SETTLED` and `settled_at` is recorded.
3. **Given** a Transaction in `ESCROWED` status, **When** the visit is cancelled before reaching `IN_PROGRESS`, **Then** the Transaction automatically transitions to `REFUNDED`.
4. **Given** a Transaction in `ESCROWED` status, **When** the visit is cancelled after reaching `IN_PROGRESS`, **Then** the Transaction remains `ESCROWED` and requires manual admin review for refund.

---

### User Story 4 — Financial Tamper-Proof Admin (Priority: P2)

Platform administrators can view Visit and Transaction records via Django Admin. All financial fields (`base_price`, `final_price`, `amount_paid`, `agency_payout`) are read-only to prevent manual tampering. The Visit admin includes list filters for `status` and `agency`, and the Transaction admin provides a complete financial overview.

**Why this priority**: Even trusted admin users must not be able to modify financial records after creation. This is a FinTech compliance requirement.

**Independent Test**: Can be verified by inspecting the `readonly_fields` tuple on the admin classes and confirming all financial fields are included.

**Acceptance Scenarios**:

1. **Given** a logged-in SuperAdmin, **When** they view a Visit in Django Admin, **Then** `base_price`, `final_price`, and all pricing fields are displayed as read-only.
2. **Given** a logged-in SuperAdmin, **When** they view a Transaction in Django Admin, **Then** `amount_paid`, `agency_payout`, and `wateen_take_rate` are displayed as read-only.
3. **Given** the Django Admin for Visit, **When** the list view is loaded, **Then** filters for `status` and `agency` are available.

---

### User Story 5 — GIS-Enabled Agency Admin (Priority: P2)

The `AgencyProfile` is registered in Django Admin using `GISModelAdmin`, providing an interactive map widget for the `coverage_polygon` field. This allows SuperAdmins to visually verify and edit agency coverage areas directly from the admin interface.

**Why this priority**: Visual verification of geospatial coverage is essential for onboarding QA but does not block core financial operations.

**Independent Test**: Can be verified by checking that `AgencyProfileAdmin` inherits from `django.contrib.gis.admin.GISModelAdmin` and renders the map widget for `coverage_polygon`.

**Acceptance Scenarios**:

1. **Given** a SuperAdmin navigating to the AgencyProfile admin page, **When** they open an agency record, **Then** an interactive map widget is displayed for the `coverage_polygon` field.

---

### Edge Cases

- What happens when `transition_to()` receives a status string not in `VisitStatus.values`? → System raises `ValidationError` with "invalid_status" code.
- What happens if a Transaction is created with `amount_paid=0.00`? → The `MinValueValidator(Decimal("0.00"))` permits zero; the payout calculation yields `0.00`.
- What happens if pricing fields are `None` on a Visit update? → The immutability check compares against database values; `None`-to-`None` is not a change and is permitted.
- How does the system handle concurrent `transition_to()` calls? → Django's `save(update_fields=...)` provides last-writer-wins semantics; race conditions are mitigated at the application layer.
- What happens when a Visit with an ESCROWED Transaction is cancelled? → If cancelled before `IN_PROGRESS`, Transaction auto-refunds. If cancelled during/after `IN_PROGRESS`, Transaction stays `ESCROWED` for manual admin review (partial service was rendered).

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: Visit model MUST have a `status` CharField with `VisitStatus` TextChoices: `PENDING_AGENCY`, `PENDING_NURSE`, `ACCEPTED`, `EN_ROUTE`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`.
- **FR-002**: Visit model MUST enforce state transitions via an `ALLOWED_TRANSITIONS` dictionary and a `transition_to(new_status)` method that raises `ValidationError` on invalid transitions.
- **FR-003**: Visit model MUST have ForeignKey relationships to `PatientProfile` (CASCADE), `AgencyProfile` (PROTECT, nullable), and `NurseProfile` (PROTECT, nullable).
- **FR-004**: Visit model MUST contain immutable pricing snapshot fields: `base_price`, `time_multiplier`, `distance_km`, `distance_rate`, `surge_coefficient`, `final_price` — all `DecimalField(max_digits=10, decimal_places=2)`.
- **FR-005**: Visit model `save()` MUST raise `ValidationError` if any pricing field is modified after initial creation (when `self.pk` exists).
- **FR-006**: Transaction model MUST have a `OneToOneField` to Visit (`on_delete=PROTECT`) and a `ForeignKey` to AgencyProfile (`on_delete=PROTECT`).
- **FR-007**: Transaction model `save()` MUST auto-calculate `agency_payout = amount_paid * Decimal('0.85')` before saving.
- **FR-008**: Transaction model MUST have `status` CharField with TextChoices: `ESCROWED`, `SETTLED`, `REFUNDED` only. The legacy `PENDING` and `FAILED` statuses are removed.
- **FR-009**: Transaction model MUST have `settled_at` DateTimeField (nullable), `paymob_order_id` CharField, and `paymob_transaction_id` CharField for Paymob payment gateway integration.
- **FR-010**: Django Admin MUST register Visit and Transaction with all financial fields as `readonly_fields`.
- **FR-011**: Django Admin for Visit MUST include list filters for `status` and `agency`.
- **FR-012**: `AgencyProfile` MUST be registered in `users/admin.py` using `GISModelAdmin` for interactive map widget support.

### Key Entities

- **Visit**: Represents a single home-nursing visit request. Links Patient, Agency, Nurse. Contains immutable pricing snapshot and state machine status. Core operational entity.
- **Transaction**: Financial ledger entry for a Visit. One-to-one with Visit. Tracks escrow lifecycle (ESCROWED → SETTLED/REFUNDED). Auto-calculates platform/agency split.
- **AgencyProfile**: B2B tenant profile. Linked from Visit and Transaction. Contains geospatial coverage polygon.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: All 7 valid state transitions in the Visit lifecycle complete successfully without errors.
- **SC-002**: All invalid state transitions (e.g., `PENDING_AGENCY` → `COMPLETED`) raise `ValidationError` with descriptive messages.
- **SC-003**: Modifying any pricing field on a saved Visit raises `ValidationError` with the immutability error message 100% of the time.
- **SC-004**: Non-pricing fields on an existing Visit can be modified and saved without immutability errors.
- **SC-005**: Transaction `agency_payout` is always exactly `amount_paid * 0.85` after save, verified to 2 decimal places.
- **SC-006**: All financial fields in Django Admin are confirmed read-only (not editable via the admin form).
- **SC-007**: AgencyProfile admin renders an interactive map widget for `coverage_polygon`.
