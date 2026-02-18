# Task: Audit Remediation (Ticket 2.4 Cleanup)

**Objective**: Address critical defects and architectural debt identified in the Deep Technical Audit of the Pricing Engine and Matching Service.

## Context

The audit revealed fragility in Redis data parsing that could crash the matching service, circular imports affecting maintainability, and loose timezone handling for pricing logic. These must be fixed before production deployment.

## Requirements

### 1. Robust Redis Parsing (`visits/services/matching.py`)

- **Current Issue**: `nurse_id_str = member_str.split(":")[1]` is brittle and unsafe.
- **Action**:
  - Import `re` and `logging`.
  - Initialize a logger for the module.
  - Inside `find_candidates`, wrap the parsing logic in a `try...except` block.
  - Use Regex (e.g., `r"nurse:(\d+)"`) to extracting the ID safely.
  - If parsing fails or regex doesn't match:
    - Log an **ERROR** with the malformed string.
    - **Skip** the candidate (continue loop) instead of crashing.

### 2. Refactor Circular Imports (`visits/services/logging.py`)

- **Current Issue**: `visits/api.py` and `visits/signals.py` have inline imports to avoid circular dependency.
- **Action**:
  - Create a new file `visits/services/logging.py`.
  - Move `log_estimate_request` function and its logic (including `EstimateLog` creation and `on_commit` wrapper) into this new service.
  - Update `visits/api.py` to import `log_estimate_request` from `visits/services/logging.py`.
  - Update `visits/signals.py` to import `log_estimate_request` from `visits/services/logging.py`.
  - Remove usages of inline imports related to this.

### 3. Explicit Cairo Timezone (`visits/services/pricing.py`)

- **Current Issue**: Night shift logic relies on server time, which may not be Cairo time.
- **Action**:
  - Ensure `pytz` is available (add to requirements if needed, or use `zoneinfo` if on Python 3.9+).
  - Define a constant `CAIRO_TZ = timezone('Africa/Cairo')` (using django's timezone or pytz).
  - In `is_night_hours`:
    - Ensure `request_time` is converted to **Cairo Time** before extracting the hour.
    - Example: `cairo_time = request_time.astimezone(CAIRO_TZ)`
    - Check if `cairo_time.hour` is within the night shift window (e.g., 10 PM - 6 AM).

### 4. Pricing Factor Fallback Logging (`visits/services/pricing.py`)

- **Current Issue**: Silent fallback to hardcoded defaults obscures missing configuration.
- **Action**:
  - In `get_factor`, if the DB lookup fails (DoesNotExist) or returns None:
    - Log a **WARNING** using `logging` module: "PricingFactor key '{key}' not found in DB. Using default: {default_value}".
    - Return the default value.

## Definition of Done

- [ ] Matching service processes valid keys and logs/skips invalid ones without crashing.
- [ ] `visits/api.py` and `visits/signals.py` have clean, top-level imports for logging service.
- [ ] Pricing calculations respect Cairo time for night shifts regardless of server UTC time.
- [ ] Missing pricing factors trigger a warning log.
- [ ] All existing tests pass.

## Verification

- Run `tests/test_audit_comprehensive.py` (if environment permits) or manual verification of:
  - Malformed Redis key handling (via unit test mock).
  - Import structure (static analysis).
  - Timezone conversion (check logs/debugger).
