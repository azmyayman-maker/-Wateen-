# B2B SaaS Dashboard API Contracts

This document defines the interface contracts for the Agency-facing B2B API.

## 1. Get Agency Overview

Retrieves aggregated metrics for the B2B dashboard.

- **Method**: `GET`
- **Path**: `/api/v1/agency/{agency_id}/dashboard/overview`
- **Auth**: Bearer Token (JWT). Token must have `agency_id` claim matching the path, and user role must be `AgencyAdmin` or `SuperAdmin`.
- **Response**:

```json
{
  "total_revenue_today": 12500.5,
  "active_nurses_count": 14,
  "visits_in_progress": 3,
  "visits_pending": 1
}
```

## 2. Update Coverage Polygon

Updates the spatial jurisdiction of an agency.

- **Method**: `POST`
- **Path**: `/api/v1/agency/{agency_id}/coverage/`
- **Auth**: Bearer Token (JWT).
- **Payload**:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [31.233334, 30.033333],
            [31.25, 30.05],
            [31.21, 30.03],
            [31.233334, 30.033333]
          ]
        ]
      }
    }
  ]
}
```

- **Response**: `200 OK`

```json
{
  "status": "success",
  "message": "Coverage updated and caches invalidated."
}
```

## 3. Manual Dispatch Assignment

Allows an Admin to manually override or assign a nurse to a pending visit.

- **Method**: `POST`
- **Path**: `/api/v1/agency/{agency_id}/dispatch/manual/`
- **Auth**: Bearer Token (JWT).
- **Payload**:

```json
{
  "visit_id": "uuid-of-visit",
  "nurse_id": "uuid-of-nurse"
}
```

- **Response**: `200 OK`

```json
{
  "status": "success",
  "detail": "Nurse effectively dispatched.",
  "visit_status": "PENDING_NURSE"
}
```

- **Errors**:
  - `400 Bad Request`: "Nurse is not available"
  - `403 Forbidden`: "Nurse does not belong to your agency"
  - `404 Not Found`: "Visit or Nurse not found"
