# Tasks: Visit & Transaction Model Restructuring (P1-T4)

**Input**: Design documents from `/specs/010-visit-transaction-restructure/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Included — the spec explicitly requires test coverage for state machine, immutability, and financial calculations.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Branch verification and codebase preparation

- [ ] T001 Verify branch `010-visit-transaction-restructure` is active and clean
- [ ] T002 Review existing `visits/models.py` to confirm current field names and line numbers before editing

**Checkpoint**: Branch and codebase state confirmed — ready for foundational changes.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: FK protection changes and new pricing fields that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Change `agency` FK from `on_delete=SET_NULL` to `on_delete=PROTECT` in `visits/models.py`
- [ ] T004 Change `nurse` FK from `on_delete=SET_NULL` to `on_delete=PROTECT` in `visits/models.py`
- [ ] T005 Add `distance_km` DecimalField(6,2) to Visit model in `visits/models.py`
- [ ] T006 Add `distance_rate` DecimalField(10,2) to Visit model in `visits/models.py`
- [ ] T007 Update `VisitFactory` in `visits/tests/conftest.py` to include `distance_km` and `distance_rate` defaults
- [ ] T008 Run `python manage.py makemigrations visits` and verify migration file is generated for FK changes and new fields

**Checkpoint**: Foundation ready — Visit model has PROTECT FKs and all pricing fields. User story implementation can begin.

---

## Phase 3: User Story 1 — Visit Lifecycle State Machine (Priority: P1) 🎯 MVP

**Goal**: Enforce state machine transitions via `ALLOWED_TRANSITIONS` map and `transition_to()` method. Verify all valid paths succeed and all invalid paths raise `ValidationError`.

**Independent Test**: Create a Visit fixture, call `transition_to()` through the full happy path (PENDING_AGENCY → ... → COMPLETED) and verify invalid transitions (e.g., PENDING_AGENCY → COMPLETED) raise `ValidationError`.

### Tests for User Story 1

- [ ] T009 [P] [US1] Write `test_visit_transition_happy_path` — full lifecycle PENDING_AGENCY → PENDING_NURSE → ACCEPTED → EN_ROUTE → IN_PROGRESS → COMPLETED in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T010 [P] [US1] Write `test_visit_transition_invalid_raises` — PENDING_AGENCY → COMPLETED raises `ValidationError` in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T011 [P] [US1] Write `test_visit_terminal_states` — verify COMPLETED and CANCELLED are terminal (any `transition_to()` raises `ValidationError`) in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T012 [P] [US1] Write `test_visit_transition_invalid_status_string` — non-existent status string raises `ValidationError` in `visits/tests/test_visit_transaction_restructure.py`

### Implementation for User Story 1

- [ ] T013 [US1] Verify `VisitStatus` TextChoices and `ALLOWED_TRANSITIONS` dict are correct in `visits/models.py` — states must be: PENDING_AGENCY, PENDING_NURSE, ACCEPTED, EN_ROUTE, IN_PROGRESS, COMPLETED, CANCELLED
- [ ] T014 [US1] Verify `transition_to(new_status)` method validates against `ALLOWED_TRANSITIONS` and raises `ValidationError` with Arabic message on invalid transitions in `visits/models.py`
- [ ] T015 [US1] Fix `visits/tests/test_visit_lifecycle.py` — update references from old statuses (`MATCHED`, `ON_WAY`, `ARRIVED`) to current B2B2C statuses (`PENDING_NURSE`, `EN_ROUTE`, `IN_PROGRESS`)
- [ ] T016 [US1] Run `pytest visits/tests/test_visit_transaction_restructure.py -v --tb=short` — verify all US1 tests pass

**Checkpoint**: Visit state machine fully functional and independently tested.

---

## Phase 4: User Story 2 — Immutable Pricing Snapshot (Priority: P1)

**Goal**: Enforce that pricing fields (`base_price`, `distance_fee`, `distance_km`, `distance_rate`, `time_multiplier`, `ai_surge_coefficient`, `final_price`) cannot be modified after a Visit is created.

**Independent Test**: Create a Visit with `final_price=250.00`, save it, attempt to modify `final_price` to `300.00` and call `save()` → expect `ValidationError`. Modify `status` field and call `save()` → expect success.

### Tests for User Story 2

- [ ] T017 [P] [US2] Write `test_pricing_immutability_blocks_update` — change `final_price` on saved Visit, expect `ValidationError` with code `immutable_pricing` in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T018 [P] [US2] Write `test_pricing_immutability_allows_non_pricing_update` — change `status` via `transition_to()` on saved Visit, expect success in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T019 [P] [US2] Write `test_pricing_immutability_new_visit_saves` — create new Visit with all pricing fields, first save succeeds in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T020 [P] [US2] Write `test_pricing_immutability_none_to_none_allowed` — Visit with `None` pricing fields can be resaved without error in `visits/tests/test_visit_transaction_restructure.py`

### Implementation for User Story 2

- [ ] T021 [US2] Add `IMMUTABLE_PRICING_FIELDS` constant tuple to Visit model in `visits/models.py` listing: `base_price`, `distance_fee`, `distance_km`, `distance_rate`, `time_multiplier`, `ai_surge_coefficient`, `final_price`
- [ ] T022 [US2] Implement `save(*args, **kwargs)` override on Visit model in `visits/models.py` — on update (`self.pk` exists), fetch DB values via `Visit.objects.get(pk=self.pk)`, compare each immutable field, raise `ValidationError` if changed
- [ ] T023 [US2] Run `pytest visits/tests/test_visit_transaction_restructure.py -k "immutab" -v --tb=short` — verify all US2 tests pass

**Checkpoint**: Pricing snapshot is frozen on creation. No field tampering possible.

---

## Phase 5: User Story 3 — Transaction / Escrow Ledger (Priority: P1)

**Goal**: Restructure `Transaction` model with agency FK, Paymob fields, auto-calc `agency_payout`, and simplified `ESCROWED`/`SETTLED`/`REFUNDED` lifecycle. Transaction is created at payment capture (entering `ESCROWED` directly).

**Independent Test**: Create a Transaction with `amount_paid=Decimal('1000.00')`, save it, verify `agency_payout == Decimal('850.00')`. Set `status=SETTLED`, save, verify `settled_at` is populated.

### Tests for User Story 3

- [ ] T024 [P] [US3] Write `test_transaction_auto_calc_payout` — save Transaction with `amount_paid=1000.00`, verify `agency_payout=850.00` in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T025 [P] [US3] Write `test_transaction_settled_at_auto_set` — set `status=SETTLED`, save, verify `settled_at` is populated in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T026 [P] [US3] Write `test_transaction_default_status_escrowed` — new Transaction defaults to `ESCROWED` status in `visits/tests/test_visit_transaction_restructure.py`
- [ ] T027 [P] [US3] Write `test_transaction_visit_fk_protect` — attempt to delete Visit with Transaction raises `ProtectedError` in `visits/tests/test_visit_transaction_restructure.py`

### Implementation for User Story 3

- [ ] T028 [US3] Update `TransactionStatus` TextChoices — remove `PENDING` and `FAILED`, keep only `ESCROWED`, `SETTLED`, `REFUNDED` in `visits/models.py`
- [ ] T029 [US3] Apply field renames via migration: `total_amount` → `amount_paid`, `take_rate_percent` → `wateen_take_rate`, `agency_amount` → `agency_payout`, `stripe_payment_intent_id` → `paymob_order_id` in `visits/models.py`
- [ ] T030 [US3] Remove `take_rate_amount` field from Transaction model in `visits/models.py`
- [ ] T031 [US3] Add `agency` ForeignKey to `users.AgencyProfile` with `on_delete=PROTECT` on Transaction in `visits/models.py`
- [ ] T032 [US3] Add `paymob_transaction_id` CharField(255, nullable) to Transaction in `visits/models.py`
- [ ] T033 [US3] Add `settled_at` DateTimeField(nullable) to Transaction in `visits/models.py`
- [ ] T034 [US3] Set `editable=False` on `agency_payout` field in `visits/models.py`
- [ ] T035 [US3] Change `visit` field from ForeignKey to `OneToOneField` with `on_delete=PROTECT` in `visits/models.py`
- [ ] T036 [US3] Implement `save()` override — auto-calculate `agency_payout = amount_paid * Decimal('0.85')` and auto-set `settled_at` when status becomes `SETTLED` in `visits/models.py`
- [ ] T037 [US3] Remove legacy `clean()` and `calculate_split()` methods from Transaction in `visits/models.py`
- [ ] T038 [US3] Run `python manage.py makemigrations visits` — verify Transaction migration is generated correctly
- [ ] T039 [US3] Write data migration to populate `agency` on existing Transactions from `visit.agency` and convert any PENDING/FAILED records to ESCROWED
- [ ] T040 [US3] Run `python manage.py migrate` — apply all migrations
- [ ] T041 [US3] Run `pytest visits/tests/test_visit_transaction_restructure.py -k "transaction" -v --tb=short` — verify all US3 tests pass

**Checkpoint**: Transaction ledger fully functional with auto-calc, Paymob integration, and clean lifecycle.

---

## Phase 6: User Story 4 — Financial Tamper-Proof Admin (Priority: P2)

**Goal**: Register Visit and Transaction in Django Admin with all financial fields as `readonly_fields`. Add list filters for `status` and `agency`.

**Independent Test**: Inspect admin classes for correct `readonly_fields` tuples containing all financial fields.

### Implementation for User Story 4

- [ ] T042 [P] [US4] Update `VisitAdmin.readonly_fields` to include `base_price`, `time_multiplier`, `distance_km`, `distance_rate`, `ai_surge_coefficient`, `final_price` in `visits/admin.py`
- [ ] T043 [P] [US4] Update `VisitAdmin.list_filter` to include `status` and `agency` in `visits/admin.py`
- [ ] T044 [US4] Add `VisitAdmin.fieldsets` with pricing section (collapsed) and metadata section in `visits/admin.py`
- [ ] T045 [US4] Register `TransactionAdmin` with `list_display`, `list_filter` (`status`, `agency`), `readonly_fields` (`amount_paid`, `wateen_take_rate`, `agency_payout`) in `visits/admin.py`
- [ ] T046 [US4] Add `TransactionAdmin.fieldsets` with financial, Paymob, and settlement sections in `visits/admin.py`
- [ ] T047 [US4] Run `python manage.py shell -c "from django.contrib import admin; from visits.models import Visit, Transaction; assert admin.site.is_registered(Visit); assert admin.site.is_registered(Transaction); print('OK')"` — verify admin registrations

**Checkpoint**: All financial fields protected from manual tampering in admin.

---

## Phase 7: User Story 5 — GIS-Enabled Agency Admin (Priority: P2)

**Goal**: Register `AgencyProfile` with `GISModelAdmin` for interactive map widget on `coverage_polygon`.

**Independent Test**: Verify `AgencyProfileAdmin` inherits from `GISModelAdmin` and is registered.

### Implementation for User Story 5

- [ ] T048 [US5] Add `from django.contrib.gis.admin import GISModelAdmin` import to `users/admin.py`
- [ ] T049 [US5] Add `AgencyProfile` import to `users/admin.py`
- [ ] T050 [US5] Register `AgencyProfileAdmin(GISModelAdmin)` with `list_display`, `list_filter`, `readonly_fields`, and fieldsets including geographic coverage section in `users/admin.py`
- [ ] T051 [US5] Set GIS defaults: `default_lon=30.8025`, `default_lat=26.8206`, `default_zoom=6` (Egypt center) in `users/admin.py`
- [ ] T052 [US5] Run `python manage.py shell -c "from django.contrib import admin; from users.models import AgencyProfile; assert admin.site.is_registered(AgencyProfile); print('OK')"` — verify GIS admin registration

**Checkpoint**: AgencyProfile admin has interactive map widget.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all stories

- [ ] T053 Run full test suite: `pytest visits/tests/ -v --tb=short`
- [ ] T054 Run `python manage.py check --deploy` — verify Django system checks pass
- [ ] T055 Run `python manage.py showmigrations visits` — verify clean migration chain
- [ ] T056 Run quickstart.md validation steps
- [ ] T057 Commit all changes with message: `feat(visits): restructure Visit & Transaction models (P1-T4)`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 State Machine (Phase 3)**: Depends on Phase 2 completion
- **US2 Immutability (Phase 4)**: Depends on Phase 2 completion — can run parallel with US1
- **US3 Transaction (Phase 5)**: Depends on Phase 2 completion — can run parallel with US1/US2
- **US4 Admin (Phase 6)**: Depends on US1 + US2 + US3 (needs final model structure)
- **US5 GIS Admin (Phase 7)**: Depends on Phase 2 only — can run parallel with US1/US2/US3
- **Polish (Phase 8)**: Depends on all phases complete

### User Story Dependencies

- **US1 (P1)**: Independent — needs only foundational FKs and pricing fields
- **US2 (P1)**: Independent — needs only foundational pricing fields
- **US3 (P1)**: Independent — Transaction restructure has no US1/US2 dependency
- **US4 (P2)**: Depends on US1+US2+US3 — admin must reflect final model fields
- **US5 (P2)**: Independent — different file (`users/admin.py`)

### Parallel Opportunities

```text
After Phase 2 (Foundational):
  ┌── US1: State Machine (visits/models.py - transition_to)
  ├── US2: Immutability (visits/models.py - save override)
  ├── US3: Transaction (visits/models.py - Transaction class)
  └── US5: GIS Admin (users/admin.py)

After US1+US2+US3:
  └── US4: Admin (visits/admin.py)

After all:
  └── Phase 8: Polish
```

> ⚠️ **Note**: US1, US2, and US3 all modify `visits/models.py`. When executing sequentially (single developer), they should be done in order T003→T057. When parallelized, merge conflicts must be resolved carefully.

---

## Parallel Example: User Story 3 (Transaction)

```bash
# Launch all US3 tests together (they test different behaviors):
Task: "test_transaction_auto_calc_payout in visits/tests/test_visit_transaction_restructure.py"
Task: "test_transaction_settled_at_auto_set in visits/tests/test_visit_transaction_restructure.py"
Task: "test_transaction_default_status_escrowed in visits/tests/test_visit_transaction_restructure.py"
Task: "test_transaction_visit_fk_protect in visits/tests/test_visit_transaction_restructure.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (FK changes + new fields)
3. Complete Phase 3: US1 — State Machine verification
4. Complete Phase 4: US2 — Immutable pricing
5. **STOP and VALIDATE**: Test state machine + immutability independently
6. Deploy to staging if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (State Machine) → Test → ✅ MVP!
3. Add US2 (Immutability) → Test → Enhanced financial integrity
4. Add US3 (Transaction) → Test → Escrow ledger operational
5. Add US4 + US5 (Admin) → Test → Admin fully configured
6. Polish → Final validation → Ready for merge

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All US1-US3 tasks operate on `visits/models.py` — execute sequentially
- US4 operates on `visits/admin.py` — independent file
- US5 operates on `users/admin.py` — independent file
- Total: **57 tasks** across 8 phases
- Commit after each checkpoint phase
