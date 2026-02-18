# Ticket 2.4: Pricing Engine (AI-Ready Foundation)

| Metadata Key | Value                                |
| :----------- | :----------------------------------- |
| **ID**       | 2.4                                  |
| **Title**    | Pricing Engine (AI-Ready Foundation) |
| **Status**   | Completed & Audited (Green)          |
| **Type**     | Core Feature / Backend               |

## Executive Summary

The Pricing Engine module implements a robust, modular strategy pattern to calculate visit costs dynamically. This architecture decouples pricing logic from the core application flow, ensuring scalability for future AI-driven models (Phase 15). Crucially, the system logs request data (Time, Location, Service) asynchronously to build a high-quality dataset for ML training, while securing the public estimation endpoint with strict rate limiting to prevent abuse.

## File Manifest

The following files were created or modified to implement this feature:

- `visits/models.py`: Added `ServiceType` (Catalog) and `PricingFactor` (Dynamic Config) models.
- `visits/api.py`: Implemented the `POST /api/visits/estimate/` endpoint.
- `visits/services/pricing.py`: Core logic implementing the `PricingStrategy` interface and `RuleBasedPricingStrategy`.
- `visits/services/matching.py`: Enhanced Redis parsing for defensive coding against malformed data.
- `visits/services/logging.py`: New decoupled logging service to handle async data logging and resolve circular imports.
- `visits/signals.py`: Signal handlers for asynchronous tasks.

## Configuration Guide

Pricing parameters are configured dynamically via the `PricingFactor` model in the Django Admin interface. System behavior relies on these keys:

- **`night_shift_fee`**: Surcharge applied to visits during night hours.
- **`per_km_fee`**: Cost multiplier per kilometer of distance.
- **`night_start_hour`**: The hour (0-23) when night pricing logic takes effect.

_Note:_ `DEFAULT_FACTORS` defined in `visits/services/pricing.py` serve as hardcoded fallbacks if database configuration is missing or inaccessible. All time-based calculations (e.g., "Night Shift") strictly use the **Africa/Cairo** timezone.

## API Specification

### Estimate Visit Price

**Endpoint:** `POST /api/visits/estimate/`

**Request Body:**

```json
{
  "lat": 30.0444,
  "lng": 31.2357,
  "service_id": 1
}
```

**Response:**

```json
{
  "price_breakdown": {
    "base_price": 50.0,
    "distance_fee": 10.0,
    "night_fee": 0.0,
    "total": 60.0
  }
}
```

## Verification & Testing

This module has passed a **Level 5 Deep Technical Audit**.

To verify the pricing logic and integration manually, run the specific test suite:

```bash
pytest visits/tests/test_pricing.py
```

## Architectural Notes

1.  **Decoupled Logging:** The `visits/services/logging.py` module was introduced to break circular dependencies and ensure that logging for AI training is handled asynchronously. This prevents logging operations from blocking the main request-response cycle.
2.  **Timezone Strictness:** To ensure consistency across distributed server environments, all logic related to "Night Shift" fees explicitly enforces the **Africa/Cairo** timezone, mitigating potential issues with UTC mismatches.
