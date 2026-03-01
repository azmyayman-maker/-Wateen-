# Wateen B2B2C — AI Agent Development Contract

> **Version:** 2.0 | **Updated:** March 1, 2026 | **Status:** ACTIVE

---

## CRITICAL CONTEXT — READ FIRST

Wateen is a **B2B2C Healthcare Aggregator** — NOT a P2P marketplace.
We connect **Patients** with **MoH-Licensed Nursing Agencies** (not freelancers).
The platform onboards **Agencies** (B2B), and Agencies manage their own nurses.
Patients never interact with nurses directly outside of assigned visits.

**If any code you write treats nurses as freelancers or bypasses the Agency layer, it is WRONG.**

---

## Architecture

| Layer             | Technology                                                              |
| :---------------- | :---------------------------------------------------------------------- |
| **Backend**       | Python 3.11+, Django 5.2, Django REST Framework                         |
| **Database**      | PostgreSQL 16 + PostGIS 3.4 (spatial queries)                           |
| **Cache/PubSub**  | Redis 7 (django-redis, channels_redis)                                  |
| **WebSockets**    | Django Channels + Redis Channel Layer                                   |
| **Async Tasks**   | Celery 5 + Redis Broker                                                 |
| **Frontend**      | Next.js 14 (App Router), TypeScript 5, Tailwind CSS                     |
| **B2B Dashboard** | React Admin (Agency SaaS Dashboard)                                     |
| **Maps**          | OpenStreetMap stack: react-leaflet, leaflet-geoman, Nominatim, OSRM/ORS |
| **Payments**      | Stripe Connect (Destination Charges)                                    |
| **Language**      | Arabic-first (RTL mandatory), i18n via next-intl                        |

---

## Project Structure

```text
config/          → Django settings, ASGI, Celery, middleware, Redis utils
users/           → CustomUser, AgencyProfile, NurseProfile, PatientProfile, KYC
  services/      → kyc_service.py (OpenCV + Tesseract OCR)
visits/          → Visit, ServiceType, Transaction, PricingFactor, EstimateLog
  services/      → pricing.py, matching.py, dispatch.py, payment.py, settlement.py
  consumers.py   → WebSocket consumers (Patient, Nurse, Agency, Test)
frontend/        → Next.js 14 Patient PWA
tests/           → Pytest suite (matching, websockets, infrastructure, audit)
docs/            → PRD.md, MIP.md, AGILE_BACKLOG_WBS.md
```

---

## Core Data Model — NEVER VIOLATE

```
CustomUser (national_id PK)
  ├── role: PATIENT | NURSE | ADMIN | AGENCY_ADMIN
  ├── AgencyProfile (1:1 for AGENCY_ADMIN)
  │     ├── coverage_polygon (PostGIS MultiPolygon)
  │     ├── dispatch_mode: AUTO | MANUAL
  │     ├── stripe_account_id
  │     └── wallet_balance
  ├── NurseProfile (1:1 for NURSE)
  │     ├── agency (FK → AgencyProfile) ← MANDATORY, never null
  │     ├── is_available (bool)
  │     └── last_location (PostGIS Point)
  └── PatientProfile (1:1 for PATIENT)

Visit
  ├── patient (FK → PatientProfile)
  ├── agency (FK → AgencyProfile) ← dispatched TO agency, not nurse
  ├── nurse (FK → NurseProfile) ← assigned BY agency after dispatch
  ├── status: PENDING_AGENCY → PENDING_NURSE → ACCEPTED → EN_ROUTE → IN_PROGRESS → COMPLETED
  ├── location (PostGIS Point)
  └── final_price, pricing_snapshot (JSONField — immutable at creation)

Transaction
  ├── visit (FK → Visit)
  ├── platform_fee (Wateen 15% take rate)
  ├── agency_payout (85%)
  └── status: PENDING → ESCROWED → SETTLED | REFUNDED
```

**Hard Rules:**

1. `NurseProfile.agency` is NEVER null — nurses belong to agencies
2. Dispatch goes Patient → Agency (via ST_Intersects) → Agency assigns Nurse
3. `Visit.pricing_snapshot` is frozen at creation — never recalculated
4. All financial amounts use `Decimal`, never `float`
5. State transitions follow `ALLOWED_TRANSITIONS` map — no shortcuts

---

## Development Roadmap (WBS) — 9 Phases

Every phase has **5 tickets** (4 feature + 1 mandatory QA). Total: 45 tickets, ~175 tasks.

### Phase 1: Database Refactoring & Multi-Tenancy ← **~80% DONE**

- RBAC enum + permission classes
- AgencyProfile (coverage_polygon, dispatch_mode, wallet)
- NurseProfile (mandatory agency FK, availability)
- Visit state machine + Transaction with calculate_split()
- **Status:** Models exist, need GIST index + SUPERADMIN role + permission classes

### Phase 2: Agency KYC & Onboarding

- Agency document upload (Commercial Registry, MoH License)
- KYC verification pipeline (SuperAdmin review queue)
- React Admin B2B Dashboard initialization
- Nurse invitation system (token-based onboarding)
- **Status:** Nurse KYC exists (OCR), Agency KYC NOT started, React Admin NOT initialized

### Phase 3: Geospatial Infrastructure ← **PARTIAL**

- PostGIS ST_Intersects for agency-patient matching
- react-leaflet + leaflet-geoman for polygon editing
- Coverage CRUD API
- OSRM/ORS routing integration
- **Status:** PatientLocationPicker exists, Redis GeoSearch exists, OSRM NOT started

### Phase 4: Two-Tier Dispatch Engine ← **PARTIAL**

- Visit request pipeline with pricing snapshot
- QualityScore agency ranking algorithm
- Manual dispatch (Agency Admin assigns nurse)
- Auto-dispatch (broadcast to nurses, first-accept-wins)
- **Status:** DispatchEngine exists with auto/manual, QualityScore ranking NOT built

### Phase 5: Real-Time Sockets ← **PARTIAL**

- Django Channels infrastructure (ASGI, Redis layer)
- Visit status broadcasting via consumers
- FCM Push notifications
- Live agency dashboard metric streams
- **Status:** All 4 consumers exist, signal→broadcast wiring incomplete, FCM NOT started

### Phase 6: Financial Escrow & Settlement

- Stripe Connect agency onboarding
- PaymentIntent with manual capture (escrow)
- Agency wallet + transaction history
- Withdrawal processing
- **Status:** PaymentService exists, onboarding NOT built, wallet API NOT built

### Phase 7: Next.js PWAs (Patient & Nurse Apps)

- Patient PWA: service discovery, booking, tracking, rating
- Nurse PWA: dispatch offers, active visit, protocol checklist
- PWA infrastructure: offline, caching, install
- **Status:** Frontend skeleton exists, NOT structured as PWAs

### Phase 8: Blackbox System & Incident Disputes

- AES-256 encrypted Blackbox logging
- SOS emergency protocol
- Clinical protocol enforcement
- Three-tier dispute resolution
- **Status:** NOT started

### Phase 9: AI Copilot & CI/CD

- Clinical decision support API
- Demand prediction + surge pricing
- GitHub Actions CI/CD pipeline
- Blue-Green deployment + monitoring
- **Status:** MLPricingStrategy placeholder exists, rest NOT started

---

## Development Constraints

| Rule                   | Detail                                                      |
| :--------------------- | :---------------------------------------------------------- |
| **Execution Model**    | Solo Dev + AI (Hyper-Pair Programming)                      |
| **Sequential Phases**  | Complete Phase N before starting Phase N+1                  |
| **QA is Mandatory**    | Every phase ends with Ticket X-5: QA, Security & Validation |
| **B2B2C Enforcement**  | Every feature must route through the Agency layer           |
| **Arabic-First**       | All user-facing text in Arabic, all UI in RTL               |
| **Open Source Maps**   | OSM only — no Google Maps, no Mapbox                        |
| **Test Coverage**      | Backend ≥ 80%, Frontend ≥ 75%                               |
| **No float for money** | Use `Decimal` everywhere for financial calculations         |
| **State machine**      | Visit status changes ONLY via `transition_to()` method      |

---

## Commands

```bash
# Backend
pytest                              # Run all tests
pytest tests/test_matching_service.py -v  # Specific test
ruff check .                        # Lint
python manage.py makemigrations     # After model changes
python manage.py migrate            # Apply migrations

# Frontend
cd frontend && npm run dev          # Dev server (port 3000)
cd frontend && npm run build        # Production build
cd frontend && npm run lint         # ESLint
```

---

## Code Style

- **Python:** PEP 8 via `ruff`, type hints on all public functions
- **TypeScript:** Strict mode, no `any` types
- **Django:** Fat models, thin views, services layer for business logic
- **Naming:** Arabic verbose_name on all model fields, English code identifiers
- **Imports:** stdlib → Django → third-party → local (enforced by `isort`)

---

## Reference Documents

| Document                   | Path                        | Purpose                                 |
| :------------------------- | :-------------------------- | :-------------------------------------- |
| Master PRD                 | `docs/PRD.md`               | Full product requirements (774 lines)   |
| Master Implementation Plan | `docs/MIP.md`               | Technical architecture + data flow      |
| Agile Backlog WBS          | `docs/AGILE_BACKLOG_WBS.md` | 9-phase development roadmap (575 lines) |

**When in doubt, the WBS is the source of truth for what to build next.**

<!-- gitnexus:start -->

# GitNexus MCP

This project is indexed by GitNexus as **Wateen** (1692 symbols, 3480 relationships, 123 execution flows).

GitNexus provides a knowledge graph over this codebase — call chains, blast radius, execution flows, and semantic search.

## Always Start Here

For any task involving code understanding, debugging, impact analysis, or refactoring, you must:

1. **Read `gitnexus://repo/{name}/context`** — codebase overview + check index freshness
2. **Match your task to a skill below** and **read that skill file**
3. **Follow the skill's workflow and checklist**

> If step 1 warns the index is stale, run `npx gitnexus analyze` in the terminal first.

## Skills

| Task                                         | Read this skill file                               |
| -------------------------------------------- | -------------------------------------------------- |
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/exploring/SKILL.md`       |
| Blast radius / "What breaks if I change X?"  | `.claude/skills/gitnexus/impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?"             | `.claude/skills/gitnexus/debugging/SKILL.md`       |
| Rename / extract / split / refactor          | `.claude/skills/gitnexus/refactoring/SKILL.md`     |

## Tools Reference

| Tool             | What it gives you                                                        |
| ---------------- | ------------------------------------------------------------------------ |
| `query`          | Process-grouped code intelligence — execution flows related to a concept |
| `context`        | 360-degree symbol view — categorized refs, processes it participates in  |
| `impact`         | Symbol blast radius — what breaks at depth 1/2/3 with confidence         |
| `detect_changes` | Git-diff impact — what do your current changes affect                    |
| `rename`         | Multi-file coordinated rename with confidence-tagged edits               |
| `cypher`         | Raw graph queries (read `gitnexus://repo/{name}/schema` first)           |
| `list_repos`     | Discover indexed repos                                                   |

## Resources Reference

Lightweight reads (~100-500 tokens) for navigation:

| Resource                                       | Content                                   |
| ---------------------------------------------- | ----------------------------------------- |
| `gitnexus://repo/{name}/context`               | Stats, staleness check                    |
| `gitnexus://repo/{name}/clusters`              | All functional areas with cohesion scores |
| `gitnexus://repo/{name}/cluster/{clusterName}` | Area members                              |
| `gitnexus://repo/{name}/processes`             | All execution flows                       |
| `gitnexus://repo/{name}/process/{processName}` | Step-by-step trace                        |
| `gitnexus://repo/{name}/schema`                | Graph schema for Cypher                   |

## Graph Schema

**Nodes:** File, Function, Class, Interface, Method, Community, Process
**Edges (via CodeRelation.type):** CALLS, IMPORTS, EXTENDS, IMPLEMENTS, DEFINES, MEMBER_OF, STEP_IN_PROCESS

```cypher
MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: "myFunc"})
RETURN caller.name, caller.filePath
```

<!-- gitnexus:end -->
