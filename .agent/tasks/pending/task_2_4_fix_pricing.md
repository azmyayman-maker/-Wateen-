# Task Identification

Task ID: 2.4-Fix
Task Name: Pricing Engine Remediation
Status: Pending
Assigned Execution Agent: OpenCode
Assigned Review Authority: Kilo Code

## 1) Context & Objective

**Objective:** Fix critical logic gaps identified in the Pricing Engine audit. The current implementation relies on hardcoded values and lacks necessary availability checks. We must make the pricing dynamic, timezone-aware, and performant.

**Context:**
The initial implementation of the pricing engine has several flaws:

1. Distance is hardcoded (5.0 km).
2. Nurse availability is not checked during candidate lookup.
3. Pricing calculations use naive datetime (ignoring timezones).
4. Logging is synchronous, slowing down the API.

## 2) Technical Specifications

### Target Files

- `visits/utils.py`: [MODIFY/NEW] Add `find_nearest_available_nurse`.
- `visits/api.py`: [MODIFY] Use dynamic distance calculation.
- `visits/services/matching.py`: [MODIFY] Filter for `is_available=True`.
- `visits/services/pricing.py`: [MODIFY] Use `django.utils.timezone`.
- `visits/signals.py`: [MODIFY] Use `transaction.on_commit` for logging.

### Architecture Rules

- **Performance**: Distance calculation should be efficient. Logging must not block the main request thread.
- **Accuracy**: Pricing must be based on the _actual_ nearest available nurse, not a hardcoded value.
- **Timezones**: All time-based logic must respect the server's timezone configuration.

## 3) Implementation Steps

1.  **Dynamic Distance Calculation (`visits/utils.py`)**:
    - Implement `find_nearest_available_nurse(lat, lng)`:
      - Query `NurseProfile` where `is_available=True` AND `is_verified=True`.
      - Calculate distance from the user's location to each nurse.
      - Return the nearest nurse (or `None`).
    - _Note_: Ensure this uses spatial queries if possible, or efficient filtering.

2.  **Update API (`visits/api.py`)**:
    - In `EstimateView` (or equivalent), remove hardcoded `distance_km = 5.0`.
    - Call `find_nearest_available_nurse`.
    - If a nurse is found, calculate the actual distance.
    - If no nurse is found, decide on a fallback (e.g., 0 distance or error, but preferably a base distance for estimation purposes if business logic allows, otherwise 0). _For this task, default to 0 if no nurse found._

3.  **Availability Filter (`visits/services/matching.py`)**:
    - In `find_candidates` (or the relevant matching function), ensure the queryset includes `.filter(is_available=True)`. Redis might return an ID, but the DB fetch must verify availability.

4.  **Timezone Awareness (`visits/services/pricing.py`)**:
    - Replace all calls to `datetime.now()` or `datetime.now().time()` with `django.utils.timezone.now()` and `timezone.localtime()`.
    - Ensure Night Shift logic checks the time in the correct timezone (Cairo).

5.  **Async Logging (`visits/signals.py`)**:
    - Wrap `EstimateLog.objects.create` (or the logging logic) in `transaction.on_commit(lambda: ...)` or use Celery if available (stick to `on_commit` for now to keep it simple but non-blocking for the transaction duration).

6.  **Verification**:
    - Ensure `tests/test_pricing.py` covers these scenarios (dynamic distance, different times of day).

## 4) Definition of Done (DoD)

- [ ] No `5.0` hardcoded distance in `visits/api.py` or related files.
- [ ] Pricing logic uses `find_nearest_available_nurse`.
- [ ] `is_available=True` is properly checked in matching.
- [ ] Timezone-aware datetime objects are used throughout pricing.
- [ ] Logging happens on transaction commit.
- [ ] Tests pass.

## 5) Acceptance Authority

- **Reviewer**: Kilo Code
- **Criteria**: Code must resolve the audit findings completely.
