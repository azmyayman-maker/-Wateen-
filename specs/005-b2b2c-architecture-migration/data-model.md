# B2B2C Data Model

Based on the entities mapped in `spec.md`, the following describes the data structures required.

## 1. AGENCY_PROFILE

**Type**: Django Model (Tenant)
**Description**: Represents a verified B2B healthcare agency. Acts as the legal entity for a group of nurses.
**Fields**:

- `id`: UUID (Primary Key)
- `manager_name`: String (Max 255)
- `commercial_registry`: String (Unique)
  - _Validation_: Must follow MoH format.
- `moh_license_number`: String (Unique)
  - _Validation_: Required for `verified` status.
- `tax_id`: String (Unique)
- `status`: Enum (`pending`, `verified`, `suspended`, `rejected`)
  - _State Transitions_: Only SuperAdmin can change to `verified`. If changed to `suspended`, all associated nurses are immediately logged out/blocked from accepting visits.
- `coverage_polygon`: PostGIS PolygonField (SRID 4326)
  - _Validation_: Must be a valid Polygon geometry.
- `rating`: Float (0.0 to 5.0, Default: 5.0)
- `network_capacity`: Integer (Number of active nurses)
- `dispatch_mode`: Enum (`AUTO`, `MANUAL`)
- `wallet_balance`: DecimalField

## 2. NURSE_PROFILE

**Type**: Django Model (Employee of an Agency)
**Description**: Extends the base User model for nurses.
**Fields**:

- `id`: UUID (Primary Key)
- `user`: OneToOneField(User)
- `agency`: ForeignKey(AGENCY_PROFILE, on_delete=CASCADE)
  - _Validation_: Cannot be null. A nurse must belong to an agency.
- `full_name`: String
- `national_id`: String (Unique)
- `is_available`: Boolean
- `last_location`: PostGIS PointField (SRID 4326)

## 3. VISIT

**Type**: Django Model (Transaction Context)
**Description**: The core service request and fulfillment record.
**Fields**:

- `id`: UUID (Primary Key)
- `patient`: ForeignKey(User)
- `agency`: ForeignKey(AGENCY_PROFILE)
- `nurse`: ForeignKey(NURSE_PROFILE, null=True)
- `status`: Enum (`pending_agency`, `pending_nurse`, `accepted`, `en_route`, `in_progress`, `completed`, `cancelled`)
  - _State Transitions_:
    - Auto-Dispatch: `pending_agency` -> `pending_nurse` (broadcast) -> `accepted` (by nurse)
    - Manual Dispatch: `pending_agency` -> `accepted` (assigned by admin to a nurse)
- `patient_location`: PostGIS PointField
- `final_price`: DecimalField

## 4. TRANSACTION

**Type**: Django Model (Financial Ledger)
**Description**: Tracks funds from escrow to settlement.
**Fields**:

- `id`: UUID
- `visit`: OneToOneField(VISIT)
- `agency`: ForeignKey(AGENCY_PROFILE)
- `amount_paid`: DecimalField (Total paid by patient)
- `wateen_take_rate`: DecimalField (e.g., 15% of amount_paid)
- `agency_payout`: DecimalField (remainder routed to agency wallet)
- `status`: Enum (`escrow`, `settled`, `refunded`)
  - _State Transitions_: Completing a visit atomically moves status from `escrow` to `settled`.
