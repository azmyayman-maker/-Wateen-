# Data Model: Visit & Transaction Model Restructuring

**Feature**: 010-visit-transaction-restructure  
**Date**: 2026-03-01

## Entity: Visit

**Table**: `visits_visit`  
**Purpose**: Represents a single home-nursing visit request and its lifecycle.

### Fields

| Field                  | Type                 | Constraints                        | Notes                            |
| ---------------------- | -------------------- | ---------------------------------- | -------------------------------- |
| `id`                   | UUID                 | PK, auto-generated                 | `uuid.uuid4`                     |
| `patient`              | FK → PatientProfile  | NOT NULL, on_delete=CASCADE        | Requesting patient               |
| `agency`               | FK → AgencyProfile   | NULLABLE, on_delete=**PROTECT**    | Populated during dispatch        |
| `nurse`                | FK → NurseProfile    | NULLABLE, on_delete=**PROTECT**    | Populated upon acceptance        |
| `status`               | CharField(15)        | choices=VisitStatus, db_index=True | State machine                    |
| `location`             | PointField           | geography=True, srid=4326          | Patient location at request time |
| `service_type`         | FK → ServiceType     | NULLABLE, on_delete=SET_NULL       | Type of nursing service          |
| `base_price`           | DecimalField(10,2)   | NULLABLE                           | **IMMUTABLE** after creation     |
| `distance_fee`         | DecimalField(10,2)   | NULLABLE                           | **IMMUTABLE** — legacy, kept     |
| `distance_km`          | DecimalField(6,2)    | NULLABLE                           | **IMMUTABLE** — NEW field        |
| `distance_rate`        | DecimalField(10,2)   | NULLABLE                           | **IMMUTABLE** — NEW field        |
| `time_multiplier`      | DecimalField(4,2)    | NULLABLE                           | **IMMUTABLE** after creation     |
| `ai_surge_coefficient` | DecimalField(4,2)    | default=1.0                        | **IMMUTABLE** after creation     |
| `final_price`          | DecimalField(10,2)   | NULLABLE                           | **IMMUTABLE** after creation     |
| `reroute_attempts`     | PositiveIntegerField | default=0                          | Dispatch reroute counter         |
| `created_at`           | DateTimeField        | auto_now_add                       | Immutable timestamp              |
| `updated_at`           | DateTimeField        | auto_now                           | Last modified                    |

### State Machine (`VisitStatus` TextChoices)

```
PENDING_AGENCY ──→ PENDING_NURSE ──→ ACCEPTED ──→ EN_ROUTE ──→ IN_PROGRESS ──→ COMPLETED
      │                  │               │            │              │
      └──────────────────┴───────────────┴────────────┴──────────────┘
                                    ↓
                                CANCELLED
```

### Allowed Transitions

| From           | To                                 |
| -------------- | ---------------------------------- |
| PENDING_AGENCY | PENDING_NURSE, ACCEPTED, CANCELLED |
| PENDING_NURSE  | ACCEPTED, CANCELLED                |
| ACCEPTED       | EN_ROUTE, CANCELLED                |
| EN_ROUTE       | IN_PROGRESS, CANCELLED             |
| IN_PROGRESS    | COMPLETED, CANCELLED               |
| COMPLETED      | _(terminal)_                       |
| CANCELLED      | _(terminal)_                       |

### Immutability Rule

These fields are frozen after initial `save()`: `base_price`, `distance_fee`, `distance_km`, `distance_rate`, `time_multiplier`, `ai_surge_coefficient`, `final_price`. Any attempt to modify them on an existing record raises `ValidationError`.

---

## Entity: Transaction

**Table**: `visits_transaction`  
**Purpose**: Financial ledger entry for a Visit. Tracks escrow lifecycle.

### Fields

| Field                   | Type                  | Constraints                     | Notes                                     |
| ----------------------- | --------------------- | ------------------------------- | ----------------------------------------- |
| `id`                    | UUID                  | PK, auto-generated              | `uuid.uuid4`                              |
| `visit`                 | OneToOneField → Visit | NOT NULL, on_delete=**PROTECT** | One transaction per visit                 |
| `agency`                | FK → AgencyProfile    | NOT NULL, on_delete=**PROTECT** | Receiving agency                          |
| `amount_paid`           | DecimalField(10,2)    | ≥ 0.00                          | Total paid by patient                     |
| `wateen_take_rate`      | DecimalField(5,2)     | 0.00–100.00, default=15.00      | Platform percentage                       |
| `agency_payout`         | DecimalField(10,2)    | editable=False, ≥ 0.00          | **Auto-calculated**: `amount_paid * 0.85` |
| `status`                | CharField(20)         | choices=TransactionStatus       | Escrow lifecycle                          |
| `paymob_order_id`       | CharField(255)        | NULLABLE                        | Paymob Order ID                           |
| `paymob_transaction_id` | CharField(255)        | NULLABLE                        | Paymob Transaction ID                     |
| `settled_at`            | DateTimeField         | NULLABLE                        | Auto-set when status → SETTLED            |
| `created_at`            | DateTimeField         | auto_now_add                    | Creation timestamp                        |
| `updated_at`            | DateTimeField         | auto_now                        | Last modified                             |

### Status Lifecycle (`TransactionStatus` TextChoices)

```
ESCROWED ──→ SETTLED      (Visit completed successfully)
    │
    └──→ REFUNDED         (Visit cancelled before IN_PROGRESS = auto;
                           Visit cancelled after IN_PROGRESS = manual)
```

### Auto-calculation Rule

On every `save()`, `agency_payout` is recalculated as: `amount_paid * Decimal('0.85')`. The `settled_at` timestamp is auto-set when `status` transitions to `SETTLED`.

---

## Relationships Diagram

```
PatientProfile ──(1:N)──→ Visit ──(1:1)──→ Transaction
                            │                    │
AgencyProfile ──(1:N)───────┘                    │
      │                                          │
      └──────────────(1:N)───────────────────────┘
                            │
NurseProfile ──(1:N)────────┘ (via Visit)
```

---

## Migration Plan

### Migration 1: Visit FK changes (schema)

- `AlterField` agency: `SET_NULL` → `PROTECT`
- `AlterField` nurse: `SET_NULL` → `PROTECT`
- `AddField` distance_km
- `AddField` distance_rate

### Migration 2: Transaction restructuring (schema + data)

- `RenameField` total_amount → amount_paid
- `RenameField` take_rate_percent → wateen_take_rate
- `RenameField` agency_amount → agency_payout
- `RemoveField` take_rate_amount
- `RenameField` stripe_payment_intent_id → paymob_order_id
- `AddField` paymob_transaction_id
- `AddField` agency (FK to AgencyProfile)
- `AddField` settled_at
- `AlterField` visit: `CASCADE` → `PROTECT`
- `AlterField` status choices (remove PENDING, FAILED)

### Migration 3: Data migration

- Populate `agency` on existing Transaction records from `visit.agency`
- Convert existing PENDING/FAILED transactions to ESCROWED (if any exist)
