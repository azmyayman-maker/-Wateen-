# Quickstart: Pricing Engine Implementation

**Feature**: 001-pricing-engine
**Date**: 2026-02-18

## Prerequisites

- Python 3.11+
- PostgreSQL with PostGIS extension
- Redis (for caching/channels)
- Docker (recommended for local development)

## Quick Setup

### 1. Start Development Environment

```bash
# Start Docker containers (if using Docker)
docker-compose up -d

# Or activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.\.venv\Scripts\activate  # Windows
```

### 2. Run Migrations

```bash
# Create migrations for new models
python manage.py makemigrations visits --name add_pricing_engine

# Apply migrations
python manage.py migrate
```

### 3. Create Initial Data

```bash
# Create default pricing factors
python manage.py shell
```

```python
from visits.models import ServiceType, PricingFactor

# Create sample service types
ServiceType.objects.create(
    name="Home Nursing",
    base_price=150.00,
    description="General home nursing care"
)
ServiceType.objects.create(
    name="Physical Therapy",
    base_price=200.00,
    description="Physical therapy session at home"
)

# Create pricing factors (or use data migration)
PricingFactor.objects.create(key="per_km_rate", value=50.00, description="EGP per kilometer")
PricingFactor.objects.create(key="night_multiplier", value=1.5, description="Night hours multiplier")
PricingFactor.objects.create(key="day_multiplier", value=1.0, description="Day hours multiplier")
PricingFactor.objects.create(key="night_start_hour", value=22, description="Night hours start (24h)")
PricingFactor.objects.create(key="night_end_hour", value=6, description="Night hours end (24h)")
```

### 4. Run Tests

```bash
# Run pricing engine tests
pytest visits/tests/test_pricing.py -v

# Run with coverage
pytest visits/tests/test_pricing.py --cov=visits.services.pricing -v
```

### 5. Test the API

```bash
# Get CSRF token (if needed)
curl -X GET http://localhost:8000/api/v1/visits/estimate/

# Request estimate
curl -X POST http://localhost:8000/api/v1/visits/estimate/ \
  -H "Content-Type: application/json" \
  -d '{
    "service_type_id": "<service-type-uuid>",
    "latitude": 30.0444,
    "longitude": 31.2357
  }'

# Request estimate for night hours
curl -X POST http://localhost:8000/api/v1/visits/estimate/ \
  -H "Content-Type: application/json" \
  -d '{
    "service_type_id": "<service-type-uuid>",
    "latitude": 30.0444,
    "longitude": 31.2357,
    "request_time": "2026-02-18T23:00:00Z"
  }'
```

## API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/visits/estimate/` | POST | Request price estimate | Public (rate-limited) |
| `/api/v1/payments/webhook/mock/` | POST | Mock payment callback | Token (dev only) |

## Key Files

| File | Purpose |
|------|---------|
| `visits/models.py` | ServiceType, PricingFactor, EstimateLog models |
| `visits/services/pricing.py` | PricingStrategy pattern implementation |
| `visits/api.py` | EstimateView, MockPaymentWebhookView |
| `visits/signals.py` | AI training data logging |
| `visits/admin.py` | Admin configuration for pricing models |
| `visits/tests/test_pricing.py` | Unit and integration tests |

## Pricing Formula

```
final_price = (base_price + (distance_km × per_km_rate)) × time_multiplier × ai_surge_coefficient
```

Where:
- `base_price`: From ServiceType
- `distance_km`: Haversine distance to nearest provider
- `per_km_rate`: From PricingFactor (default: 50 EGP)
- `time_multiplier`: 1.5 for night hours (22:00-06:00), 1.0 otherwise
- `ai_surge_coefficient`: Currently 1.0 (reserved for ML)

## Troubleshooting

### Migration Errors

```bash
# Reset migrations (development only!)
python manage.py migrate visits zero
python manage.py migrate visits
```

### Rate Limiting

If hitting rate limits during testing:
```python
# In settings.py, temporarily increase:
REST_FRAMEWORK = {
    ...
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/hour",  # Increased for testing
        ...
    },
}
```

### PostGIS Issues

```bash
# Ensure PostGIS extension is enabled
psql -d wateen -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

## Next Steps

1. Review the [data model](./data-model.md) for entity details
2. Review the [API contract](./contracts/openapi.yaml) for request/response formats
3. Run `/speckit.tasks` to generate implementation tasks
