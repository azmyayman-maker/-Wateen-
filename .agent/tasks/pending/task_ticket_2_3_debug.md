# Task Identification

- **Task ID:** TASK-009
- **Task Name:** Ticket 2.3 — Fix Redis Encoding in GeoMatchingService
- **Status:** Pending
- **Assigned Execution Agent:** OpenCode
- **Assigned Review Authority:** Kilo Code

---

## 1) Context & Objective

The `GeoMatchingService` is failing integration smoke tests. When retrieving candidates from Redis, the service receives data as **bytes** (e.g., `b'nurse:101'`) but attempts to process it directly as a string, causing crashes or incorrect logic.

The goal is to robustly handle Redis responses by ensuring all member data is decoded to strings before processing, and that the `nurse:` prefix is correctly stripped to extract the numeric ID.

---

## 2) Technical Specifications

### Target Files

| File                              | Action | Responsibility                       |
| --------------------------------- | ------ | ------------------------------------ |
| `visits/services/matching.py`     | MODIFY | Fix `find_candidates` decoding logic |
| `visits/test_matching_service.py` | NEW    | Add reproduction test case           |

### Architecture Rules

- **Defensive Coding:** Must handle both `bytes` and `str` types (Redis client behavior can vary by version/mocking).
- **Error Handling:** Invalid formats should be logged and skipped, not crash the entire search.
- **Type Safety:** `nurse_id` must be returned as an `int`.

---

## 3) Implementation Steps

### Step 1 — Create Reproduction Test

Create `visits/test_matching_service.py` with a test case that mocks Redis returning **bytes**.

```python
from unittest.mock import MagicMock, patch
from django.test import TestCase
from visits.services.matching import GeoMatchingService

class TestGeoMatchingDecoding(TestCase):
    @patch('visits.services.matching.get_redis_connection')
    def test_find_candidates_handles_bytes_and_prefix(self, mock_get_conn):
        # Setup
        mock_redis = MagicMock()
        mock_get_conn.return_value = mock_redis
        service = GeoMatchingService()

        # Simulate Redis returning bytes with prefix
        # (member, distance) tuples
        mock_redis.geosearch.return_value = [
            (b'nurse:999', 0.123)
        ]

        # Execute
        results = service.find_candidates(30.0, 31.0)

        # Verify
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['nurse_id'], 999)
        self.assertIsInstance(results[0]['nurse_id'], int)
```

### Step 2 — Fix `visits/services/matching.py`

Modify the loop in `find_candidates` (lines ~145-160):

```python
            for member, distance in results:
                # FIX 1: Decode bytes to string
                member_str = member.decode('utf-8') if isinstance(member, bytes) else member

                # FIX 2: Robust ID extraction
                try:
                    # Strip 'nurse:' prefix if present
                    if member_str.startswith("nurse:"):
                        nurse_id_str = member_str.split(":")[1]
                    else:
                        nurse_id_str = member_str

                    nurse_id = int(nurse_id_str)
                except (IndexError, ValueError):
                    logger.warning("Invalid geo member format: %s", member_str)
                    continue

                candidates.append(
                    {
                        "nurse_id": nurse_id,
                        "distance_km": round(float(distance), 3),
                    }
                )
```

---

## 4) Definition of Done (DoD)

- [ ] `visits/services/matching.py` explicitly checks for `bytes` and decodes `.decode('utf-8')`.
- [ ] Code handles `nurse:` prefix removal correctly.
- [ ] New test `visits/test_matching_service.py` passes with `pytest`.
- [ ] No regression in existing functionality.

---

## Final Directive

The execution agent must not deviate from this specification.
