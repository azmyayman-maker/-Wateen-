# Implementation Plan: Pricing Engine (AI-Ready Foundation)

**Branch**: `001-pricing-engine` | **Date**: 2026-02-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-pricing-engine/spec.md`

## Summary

Implement a modular pricing engine for the Wateen platform using the Strategy Pattern. The system supports rule-based pricing initially with infrastructure for future ML-based strategies. Key components: ServiceType model, PricingFactor model (configurable pricing variables), enhanced Visit model with price fields, EstimateLog for AI training data, estimate API endpoint, and mock payment webhook.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django 5.2, Django REST Framework, PostGIS (django.contrib.gis)
**Storage**: PostgreSQL with PostGIS extension
**Testing**: pytest, pytest-django
**Target Platform**: Linux server (Docker containerized)
**Project Type**: Web application (Django monolith with DRF API)
**Performance Goals**: Price estimates return within 2 seconds for 99% of requests
**Constraints**: IP-based rate limiting on public estimate endpoint; 2-year data retention for EstimateLog
**Scale/Scope**: Supports multiple service types, configurable pricing factors, AI-ready data collection

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file is template-only (not customized). Default gates applied:

| Gate | Status | Notes |
|------|--------|-------|
| Test coverage | ✅ Pass | pytest tests planned for all pricing logic |
| Separation of concerns | ✅ Pass | Pricing logic isolated in `services/pricing.py` |
| No hardcoded values | ✅ Pass | All pricing factors fetched from database |
| API documentation | ✅ Pass | OpenAPI contracts generated in Phase 1 |

## Project Structure

### Documentation (this feature)

```text
specs/001-pricing-engine/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.yaml     # API contract
└── tasks.md             # Phase 2 output (NOT created yet)
```

### Source Code (repository root)

```text
visits/
├── models.py            # [MODIFY] Add ServiceType, PricingFactor, EstimateLog; update Visit
├── services/
│   ├── __init__.py
│   ├── pricing.py       # [NEW] PricingStrategy pattern implementation
│   └── ...
├── signals.py           # [NEW/MODIFY] Data logging for AI training
├── api.py               # [NEW] EstimateView, MockPaymentWebhookView
├── urls.py              # [MODIFY] Register new endpoints
├── payment_mock.py      # [NEW] Mock payment webhook logic
├── admin.py             # [MODIFY] Register ServiceType, PricingFactor, EstimateLog
├── serializers.py       # [MODIFY] Add serializers for new models
└── tests/
    └── test_pricing.py  # [NEW] Unit tests for pricing logic and API
```

**Structure Decision**: Single Django app (`visits`) extension. All pricing-related code lives within the existing visits app, following Django conventions. New `services/pricing.py` module for Strategy Pattern implementation.

## Complexity Tracking

No constitution violations to justify. Design follows standard Django patterns:
- Strategy Pattern for pricing algorithms (extensible for future ML)
- Database-backed configuration (PricingFactor)
- Signal-based data collection (non-intrusive logging)
