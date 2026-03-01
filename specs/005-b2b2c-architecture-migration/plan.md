# Implementation Plan: B2B2C Architecture Migration

**Branch**: `005-b2b2c-architecture-migration` | **Date**: 2026-02-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-b2b2c-architecture-migration/spec.md`

**Note**: This template has been filled in by the `/speckit.plan` command.

## Summary

The goal of this migration is to transition the Wateen platform from a Peer-to-Peer (P2P) freelance model to a Business-to-Business-to-Consumer (B2B2C) Aggregator Model for absolute compliance with the Egyptian Ministry of Health. Wateen will provide a SaaS dashboard to Licensed Nursing Agencies (`AGENCY_PROFILE`), who then employ and manage Nurses (`NURSE_PROFILE`) to fulfill patient visit requests via spatial routing. Payments are held in Escrow and automatically split between Wateen and the Agency upon completion.

## Technical Context

**Language/Version**: Python 3.11+, TypeScript  
**Primary Dependencies**: Django, Next.js, PostGIS, Celery, Redis, Django Channels, Stripe, Mapbox GL JS  
**Storage**: PostgreSQL (with PostGIS extensions)  
**Testing**: Pytest (backend), Locust (load testing WS), Jest/React Testing Library (frontend)  
**Target Platform**: Linux Server (Dockerized), Web Browser (PWA)  
**Project Type**: Multi-tenant Web App & Backend API  
**Performance Goals**: Spatial queries < 50ms, Dispatch matching < 200ms  
**Constraints**: Support up to 5,000 concurrent Nurse WS connections, strict row-level security for multi-tenant isolation  
**Scale/Scope**: Transition existing data via idempotency scripts. Support nationwide coverage natively.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Check Status**: PASSED.
The current master constitution is an organizational structural template (`[PROJECT_NAME] Constitution`). No violations were detected against standard software engineering principles or AI pair programming operational procedures.

## Project Structure

### Documentation (this feature)

```text
specs/005-b2b2c-architecture-migration/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (api.md)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/ (Django)
├── src/
│   ├── users/
│   │   ├── models.py (AGENCY_PROFILE, NURSE_PROFILE)
│   ├── visits/
│   │   ├── models.py (VISIT)
│   │   ├── api.py (B2B endpoints, dispatch logic)
│   ├── financials/
│   │   ├── models.py (TRANSACTION)
│   │   ├── tasks.py (Celery escrow settlements)

*Note: docker-compose orchestration was refactored outside of the backend module.*

frontend/ (Next.js)
├── src/
│   ├── app/ (App Router)
│   │   ├── (b2b)/agency/[id]/ (SaaS Dashboard)
│   ├── components/
│   │   ├── map/ (Mapbox coverage polygon drawing)
```

**Structure Decision**: The project is a standard Web Application (Option 2). The backend uses Django with PostGIS and Celery. The frontend uses Next.js app router. Spatial logic resides securely in the backend, while the frontend provides the interactive B2B SaaS dashboard focusing on Mapbox components and management screens.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| _None_    | N/A        | N/A                                  |
