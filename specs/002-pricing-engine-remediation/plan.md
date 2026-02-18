# Implementation Plan: Pricing Engine Remediation

**Branch**: `002-pricing-engine-remediation` | **Date**: 2026-02-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-pricing-engine-remediation/spec.md`

## Summary

Remediate 4 critical issues in the pricing engine: (1) Replace hardcoded 5.0 km distance with dynamic calculation using PostGIS spatial queries to find nearest available nurse, (2) Filter nurse candidates by `is_available=True` AND `verification_status='VERIFIED'`, (3) Use `django.utils.timezone` for timezone-aware datetime handling (Cairo timezone), (4) Wrap logging in `transaction.on_commit()` for non-blocking async execution.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Django 5.2, Django REST Framework, PostGIS (django.contrib.gis), redis, django-redis  
**Storage**: PostgreSQL with PostGIS extension  
**Testing**: pytest with pytest-django  
**Target Platform**: Linux server  
**Project Type**: Web application (Django monolith)  
**Performance Goals**: API response < 500ms (SC-002)  
**Constraints**: Logging must not block API response (SC-006)  
**Scale/Scope**: Standard Django app with geospatial queries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file is a template (not configured). No specific gates to enforce. Standard Django best practices apply:
- [x] Use existing models (NurseProfile, ServiceType, EstimateLog)
- [x] Follow existing code patterns in visits/ app
- [x] Maintain backward compatibility with existing API

## Project Structure

### Documentation (this feature)

```text
specs/002-pricing-engine-remediation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── estimate-api.yaml
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
visits/
├── utils.py             # NEW: find_nearest_available_nurse()
├── api.py               # MODIFY: Use dynamic distance
├── services/
│   ├── matching.py      # MODIFY: Add is_available filter
│   └── pricing.py       # MODIFY: Use django.utils.timezone
├── signals.py           # MODIFY: Use transaction.on_commit
├── tests/
│   └── test_pricing.py  # MODIFY: Add new test cases
└── models.py            # EXISTING: No changes needed

users/
└── models.py            # EXISTING: NurseProfile has is_available, verification_status, last_location
```

**Structure Decision**: This is a remediation task modifying existing Django app structure. No new apps or packages needed. All changes are within the existing `visits/` app.

## Complexity Tracking

No constitution violations. This is a straightforward remediation following existing patterns.

## Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `visits/utils.py` | NEW | Add `find_nearest_available_nurse(lat, lng)` function |
| `visits/api.py` | MODIFY | Replace hardcoded `distance_km = Decimal("5.0")` with dynamic calculation |
| `visits/services/matching.py` | MODIFY | Add `is_available=True` filter to queryset |
| `visits/services/pricing.py` | MODIFY | Replace `datetime.now()` with `timezone.now()` and `timezone.localtime()` |
| `visits/signals.py` | MODIFY | Wrap `EstimateLog.objects.create` in `transaction.on_commit()` |
| `visits/tests/test_pricing.py` | MODIFY | Add tests for dynamic distance, timezone awareness |
