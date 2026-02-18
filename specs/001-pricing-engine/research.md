# Research: Pricing Engine (AI-Ready Foundation)

**Date**: 2026-02-18
**Feature**: 001-pricing-engine

## Research Questions

### 1. Strategy Pattern Implementation in Django

**Decision**: Use abstract base class with `ABC` for `PricingStrategy` interface

**Rationale**: 
- Python's `abc.ABC` provides clear interface contracts
- Easy to add new strategies (e.g., `MLPricingStrategy`) without modifying existing code
- Django services layer is the appropriate place for business logic

**Alternatives Considered**:
- Django settings-based strategy selection: Rejected - less flexible, requires settings changes
- Database-stored strategy classes: Rejected - over-engineering for current needs
- Simple factory function: Rejected - doesn't enforce interface contract

**Implementation**:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class PriceBreakdown:
    base_price: Decimal
    distance_fee: Decimal
    time_multiplier: Decimal
    ai_surge_coefficient: Decimal
    final_price: Decimal

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, visit_data: dict) -> PriceBreakdown:
        pass

class RuleBasedPricingStrategy(PricingStrategy):
    def calculate_price(self, visit_data: dict) -> PriceBreakdown:
        # Implementation
        pass
```

---

### 2. PricingFactor Default Values

**Decision**: Use hardcoded defaults in strategy, documented in code comments

**Rationale**:
- Sensible defaults ensure system works even with empty database
- Clear documentation of what values are used as fallbacks
- Avoids complex migration or fixture requirements

**Default Values**:
| Factor Key | Default Value | Description |
|------------|---------------|-------------|
| `per_km_rate` | 50.00 EGP | Charge per kilometer |
| `night_multiplier` | 1.5 | Night hours (22:00-06:00) multiplier |
| `day_multiplier` | 1.0 | Day hours multiplier |
| `base_distance_km` | 5 | Distance included in base price |

**Alternatives Considered**:
- Migration with initial data: Rejected - adds deployment complexity
- Settings-based defaults: Rejected - mixes configuration with code
- No defaults (error on missing): Rejected - poor user experience

---

### 3. Night Hours Detection

**Decision**: Use configurable PricingFactor for night hours window

**Rationale**:
- Business may want to adjust night hours seasonally
- Different regions may have different conventions
- Stores as `night_start_hour` and `night_end_hour` factors

**Implementation**:
- Default: 22:00 to 06:00 (10 PM to 6 AM)
- Check if request time falls within night window
- Apply `night_multiplier` if in night hours

---

### 4. Distance Calculation Method

**Decision**: Haversine formula for straight-line distance

**Rationale**:
- Already using PostGIS with PointField
- PostGIS `ST_Distance` with geography type returns meters
- Fast calculation, no external API calls needed
- Spec explicitly states haversine is acceptable

**Implementation**:
```python
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

customer_point = Point(longitude, latitude, srid=4326)
# provider_point from nearest available nurse location
distance_km = customer_point.distance(provider_point) * 100  # Convert to km
```

**Alternatives Considered**:
- Google Distance Matrix API: Rejected - adds cost, latency, external dependency
- OSRM (routing): Rejected - adds infrastructure complexity
- PostGIS routing: Rejected - over-engineering for current phase

---

### 5. EstimateLog Data Model

**Decision**: Separate model with JSON field for price components

**Rationale**:
- Clean separation from Visit (estimate may not lead to booking)
- JSON field allows flexible schema for ML features
- Timestamp enables time-series analysis
- Location enables geographic analysis

**Fields**:
- `id`: UUID primary key
- `request_time`: DateTime (indexed)
- `location`: PointField
- `service_type_id`: ForeignKey to ServiceType (nullable for deleted types)
- `price_components`: JSONField (base, distance_fee, time_multiplier, final_price)
- `ip_address`: GenericIPAddressField (for rate limiting analysis)
- `created_at`: DateTime (auto)

---

### 6. Rate Limiting for Public Endpoint

**Decision**: Use DRF's built-in `AnonRateThrottle`

**Rationale**:
- Already configured in settings (`anon: 100/hour`)
- No additional infrastructure needed
- Works per-IP address

**Implementation**:
```python
from rest_framework.throttling import AnonRateThrottle

class EstimateRateThrottle(AnonRateThrottle):
    rate = '30/hour'  # More restrictive for estimate endpoint
```

---

### 7. Mock Payment Webhook Security

**Decision**: Simple token-based validation, disabled in production

**Rationale**:
- Only for testing, not production use
- Token prevents casual abuse
- Check `DEBUG` setting to disable in production

**Implementation**:
```python
MOCK_WEBHOOK_TOKEN = os.environ.get('MOCK_WEBHOOK_TOKEN', 'dev-only-token')

def validate_mock_token(request):
    if not settings.DEBUG:
        return False  # Disabled in production
    token = request.headers.get('X-Mock-Token')
    return token == MOCK_WEBHOOK_TOKEN
```

---

## Resolved Clarifications

All technical clarifications from the spec have been addressed:

1. **Endpoint security**: Rate-limited public endpoint with IP-based throttling
2. **Distance reference**: From customer location to nearest available provider
3. **Data retention**: 2 years for EstimateLog

## Dependencies Summary

| Dependency | Purpose | Already in Project |
|------------|---------|-------------------|
| Django 5.2 | Web framework | ✅ Yes |
| DRF | REST API | ✅ Yes |
| PostGIS | Geospatial DB | ✅ Yes |
| pytest | Testing | ✅ Yes |
| Redis | Caching | ✅ Yes |

No new dependencies required.
