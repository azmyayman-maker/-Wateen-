# Ticket 2.1: Visit Lifecycle Logic & State Machine

## 1. Ticket Metadata

- **ID:** Ticket 2.1
- **Title:** Visit Lifecycle Logic & State Machine
- **Status:** ✅ Completed (Remediated)
- **Date:** 2026-02-17

## 2. Technical Summary

This module acts as the "core engine" for the Wateen Healthcare Platform, managing the lifecycle of home-nursing visits from creation to completion.
Key technical highlights include:

- **Visit Model:** Implemented in the `visits` app, representing the central entity for service requests.
- **State Machine Logic:** A strict state transition mechanism is enforced to ensure data integrity and logical flow. The allowed transitions are defined as follows:
  - `PENDING` → `MATCHED` or `CANCELLED`
  - `MATCHED` → `ACCEPTED` or `CANCELLED`
  - `ACCEPTED` → `ON_WAY` or `CANCELLED`
  - `ON_WAY` → `ARRIVED` or `CANCELLED`
  - `ARRIVED` → `IN_PROGRESS` or `CANCELLED`
  - `IN_PROGRESS` → `COMPLETED` or `CANCELLED`
- **Geospatial Data:** Utilizes **PostGIS** (`PointField`) to accurately store and query patient locations, enabling future location-based matching features.

## 3. File Manifest (Created/Modified)

The following files were created or modified to implement this feature:

- `visits/models.py`: Defines the `Visit` model, `VisitStatus` enumeration, and the `ALLOWED_TRANSITIONS` map.
- `visits/services.py`: Contains the b2b logic for handling state transitions (e.g., `transition_to`) and visit creation.
- `visits/serializers.py`: DRF Serializers for API input/output.
- `visits/views.py`: The API ViewSet for handling requests.
- `visits/urls.py`: URL routing.
- `opencode.json`: **(Critical)** Note that this was modified to remove hardcoded credentials.

## 4. API Specification

- **Endpoint:** `POST /api/visits/request/`
- **Input (JSON):** `{"service_type": "...", "latitude": float, "longitude": float}`
- **Output:** `201 Created` with Visit ID and Status `PENDING`.

## 5. Configuration & Security

- **Environment Variables:** Document that `DATABASE_URI` is required for PostGIS connection.
- **Security Note:** Explicitly state that hardcoded credentials in `opencode.json` were removed during the QA phase and replaced with `${DATABASE_URI}` injection.

## 6. Verification Steps

Provide the exact commands to verify this feature:

1.  **Test Suite:** `pytest visits/tests.py` (Focus on state transition tests).
2.  **Manual Check:**
    ```bash
    # Verify Visit Creation via cURL
    curl -X POST http://localhost:8000/api/visits/request/ \
      -H "Content-Type: application/json" \
      -d '{"service_type": "nurse_visit", "latitude": 30.0444, "longitude": 31.2357}'
    ```

## 7. Architectural Compliance

- **Modular Monolith:** Confirm `visits` is a standalone app.
- **Separation of Concerns:** Confirm logic resides in `services.py`, not `views.py`.
- **Clean Code:** Confirm specific exception handling (e.g., `AttributeError` instead of bare `Exception`) was applied.
