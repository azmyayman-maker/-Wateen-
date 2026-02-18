# Data Model: Pricing Engine

**Date**: 2026-02-18
**Feature**: 001-pricing-engine

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│   ServiceType   │       │  PricingFactor  │
├─────────────────┤       ├─────────────────┤
│ id (UUID)       │       │ key (str, PK)   │
│ name (str)      │       │ value (Decimal) │
│ base_price (Dec)│       │ description     │
│ description     │       │ created_at      │
│ is_active (bool)│       │ updated_at      │
│ created_at      │       └─────────────────┘
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N (service_type_id)
         ▼
┌─────────────────┐       ┌─────────────────┐
│      Visit      │       │   EstimateLog   │
├─────────────────┤       ├─────────────────┤
│ id (UUID, PK)   │       │ id (UUID, PK)   │
│ patient (FK)    │       │ request_time    │
│ nurse (FK)      │       │ location (Point)│
│ service_type(FK)│       │ service_type(FK)│
│ status (str)    │       │ price_components│
│ location (Point)│       │ ip_address      │
│ base_price (Dec)│◄──────│ created_at      │
│ distance_fee    │       └─────────────────┘
│ time_multiplier │
│ ai_surge_coef   │
│ final_price     │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Entity Definitions

### ServiceType

Represents a category of service with its base pricing.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, auto-generated | Unique identifier |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Service name (e.g., "Home Nursing", "Physical Therapy") |
| `base_price` | DECIMAL(10,2) | NOT NULL, >= 0 | Base price in EGP |
| `description` | TEXT | NULLABLE | Service description |
| `is_active` | BOOLEAN | DEFAULT True | Soft delete flag |
| `created_at` | DATETIME | auto_now_add | Creation timestamp |
| `updated_at` | DATETIME | auto_now | Last update timestamp |

**Validation Rules**:
- `name` must be unique
- `base_price` must be non-negative
- Inactive service types cannot be selected for new estimates

---

### PricingFactor

Configurable pricing variables that drive price calculations.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `key` | VARCHAR(50) | PK | Unique factor identifier (e.g., "per_km_rate") |
| `value` | DECIMAL(10,4) | NOT NULL | Factor value |
| `description` | VARCHAR(255) | NULLABLE | Human-readable description |
| `created_at` | DATETIME | auto_now_add | Creation timestamp |
| `updated_at` | DATETIME | auto_now | Last update timestamp |

**Predefined Factors**:
| Key | Default Value | Description |
|-----|---------------|-------------|
| `per_km_rate` | 50.00 | EGP per kilometer |
| `night_multiplier` | 1.5 | Multiplier for night hours |
| `day_multiplier` | 1.0 | Multiplier for day hours |
| `night_start_hour` | 22 | Night hours start (24h format) |
| `night_end_hour` | 6 | Night hours end (24h format) |
| `base_distance_km` | 5 | Distance included in base price |

**Validation Rules**:
- `key` must match pattern `[a-z_]+` (lowercase snake_case)
- `value` must be non-negative for rate/multiplier factors

---

### Visit (Modified)

Extended with pricing data fields.

| New Field | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `service_type` | FK → ServiceType | NULLABLE, ON_DELETE=SET_NULL | Changed from CharField |
| `base_price` | DECIMAL(10,2) | NULLABLE | Base service price |
| `distance_fee` | DECIMAL(10,2) | NULLABLE | Calculated distance fee |
| `time_multiplier` | DECIMAL(4,2) | NULLABLE | Time-based multiplier applied |
| `ai_surge_coefficient` | DECIMAL(4,2) | DEFAULT 1.0 | Future ML surge factor |
| `final_price` | DECIMAL(10,2) | NULLABLE | Final calculated price |

**State Transitions** (unchanged):
- PENDING → MATCHED → ACCEPTED → ON_WAY → ARRIVED → IN_PROGRESS → COMPLETED
- CANCELLED from any non-terminal state

---

### EstimateLog

Captures estimate request data for ML training.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, auto-generated | Unique identifier |
| `request_time` | DATETIME | NOT NULL, indexed | When estimate was requested |
| `location` | PointField | NOT NULL (SRID 4326) | Customer location |
| `service_type` | FK → ServiceType | NULLABLE, ON_DELETE=SET_NULL | Requested service |
| `price_components` | JSONField | NOT NULL | Full price breakdown |
| `ip_address` | GenericIPAddressField | NULLABLE | Client IP for analysis |
| `created_at` | DATETIME | auto_now_add | Log creation timestamp |

**Price Components JSON Schema**:
```json
{
  "base_price": 100.00,
  "distance_km": 12.5,
  "distance_fee": 625.00,
  "time_multiplier": 1.5,
  "ai_surge_coefficient": 1.0,
  "final_price": 1087.50
}
```

**Validation Rules**:
- `location` must be valid Point within Egypt bounds (approx: lat 22-32, lon 25-35)
- `price_components` must contain all required fields

**Data Retention**: 2 years (implement via periodic cleanup task)

---

## Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| ServiceType | `ix_servicetype_name` | name | Lookup by name |
| PricingFactor | (PK) | key | Primary lookup |
| Visit | `ix_visit_service_type` | service_type_id | Filter by service |
| EstimateLog | `ix_estimatelog_request_time` | request_time | Time-series queries |
| EstimateLog | `ix_estimatelog_service_type` | service_type_id | Filter by service |

## Migration Strategy

1. Create `ServiceType` model
2. Create `PricingFactor` model with initial data migration
3. Create `EstimateLog` model
4. Add pricing fields to `Visit` model (nullable for existing records)
5. Convert `Visit.service_type` from CharField to ForeignKey (data migration)
