# 🏥 Wateen (وَتِين) — B2B2C Architecture Migration Specification (PRD)

**Feature Branch**: `005-b2b2c-architecture-migration`  
**Created**: 2026-02-25  
**Origin**: `d:\projects\Wateen\docs\MIP.md` (MIP v4.0)
**Status**: IN REVIEW

---

## 1. Executive Summary and Strategic Shift

This Product Requirements Document (PRD) meticulously dictates the comprehensive system transition of the Wateen platform from a Peer-to-Peer (P2P) freelance model to a robust **Business-to-Business-to-Consumer (B2B2C) Aggregator Model**. This pivot is strategically mandated to ensure absolute and incontrovertible compliance with the Egyptian Ministry of Health (MoH) regulations.

Under the finalized B2B2C architecture, Wateen functions exclusively as a technology orchestrator and centralized marketplace. We explicitly disallow independent freelance nurses from operating directly on the platform. Instead, Wateen supplies a cutting-edge Software-as-a-Service (SaaS) Digital Dashboard to **Licensed Nursing Agencies**. These agencies act as the designated legal, clinical, and operational employers of the nursing staff. Patients interact with Wateen to request home healthcare services, and Wateen's algorithmic engine spatially and logically routes these requests to the optimal participating Agency, which then handles the fulfillment, thereby legally sheltering Wateen from clinical liabilities while maximizing care quality.

### 1.1 Objectives of this PRD

- Define the engineering blueprint for migrating existing database structures to the B2B2C schema without data loss.
- Document every acceptable User Story and User Journey across four distinct personas: Patient, Nurse, Agency Admin, and SuperAdmin.
- Specify the API signatures, PostGIS routing logic, and state machine modifications for the Visit Lifecycle.
- Establish the new financial routing model (Escrow -> Platform Take Rate -> Agency Payout).
- Serve as the absolute source of truth for all subsequent code generation and human-AI pair programming tasks.

---

## 2. User Scenarios & User Journeys (Prioritized)

### User Story 1 - Agency Onboarding & Verification (Priority: P1)

**Description**: As a Wateen SuperAdmin, I need to digitally onboard, verify, and approve Licensed Nursing Agencies through a rigorous KYC process involving Commercial Registration and MoH License verification so that they can legally operate on the platform.
**Why this priority**: Without verified agencies, the entire B2B2C model halts. This is the foundation of the legal compliance pivot.
**Acceptance Scenarios**:

1. **Given** an unverified Agency registers, **When** they upload their Tax ID, Commercial Registry, and MoH License, **Then** the status defaults to `pending`.
2. **Given** an Agency is `pending`, **When** the SuperAdmin reviews and approves the documents via the React Admin panel, **Then** the Agency status changes to `verified` and they gain access to the B2B SaaS Dashboard.

### User Story 2 - Agency Defines Coverage Geography (Priority: P1)

**Description**: As an Agency Admin (B2B user), I need to draw a geometric polygon (`coverage_polygon`) on a map dashboard representing my operational jurisdiction, so Wateen only sends me patient requests within my service area.
**Why this priority**: Geospatial routing is the core value proposition of Wateen. Agencies must control where their nurses deploy to ensure SLA compliance.
**Acceptance Scenarios**:

1. **Given** an Agency Admin is logged into the SaaS Dashboard, **When** they navigate to Settings, **Then** they see an interactive Mapbox/Leaflet widget.
2. **Given** the map widget, **When** the Admin draws a polygon and saves, **Then** the backend updates the PostGIS `AGENCY_PROFILE.coverage_polygon` field successfully.

### User Story 3 - Patient Requests a Visit (Priority: P1)

**Description**: As a Patient (B2C user), I need to request a home nursing service by dropping a pin on a map, securely prepaying, and instantly receiving an ETA from a verified agency.
**Why this priority**: This validates the revenue-generating action and the top of the fulfillment funnel.
**Acceptance Scenarios**:

1. **Given** a Patient selects a service and drops a coordinate pin, **When** they submit the request, **Then** the system utilizes a `ST_Intersects` spatial query to find all `verified` Agencies whose `coverage_polygon` contains the pin.
2. **Given** the request is paid and held in escrow, **When** multiple agencies overlap the pin, **Then** the matching engine ranks them by Rating and Network Capacity, routing the dispatch payload to the highest-ranking Agency first.

### User Story 4 - Agency Dispatch Protocol (Manual vs Auto) (Priority: P1)

**Description**: As an Agency, I need Wateen to respect my chosen dispatch mode (Auto-Dispatch to all my online nurses natively, OR Manual Dispatch where I assign the visit from my dashboard).
**Why this priority**: Agency workflows differ; larger agencies want algorithmic dispatch, while smaller ones prefer manual oversight perfectly distributing the workload.
**Acceptance Scenarios**:

1. **Given** Agency A is set to `Auto-Dispatch`, **When** a patient request is routed to Agency A, **Then** the system pushes a WebSocket notification to all online nurses associated _only_ with Agency A.
2. **Given** Agency B is set to `Manual-Dispatch`, **When** a patient request routes to Agency B, **Then** it hits a "Pending Review" queue on their dashboard, and the Agency Admin assigns a specific nurse via an API mutation.
3. **Given** the request times out (e.g., 3 minutes) at the first Agency without acceptance, **When** the timeout event fires, **Then** the system re-routes the payload to the next highest-ranking Agency in the polygon overlap list.

### User Story 5 - Escrow and Financial Settlement (Priority: P2)

**Description**: As Wateen, I need to collect the full patient payment upfront holding it in an Escrow status, deduct an automated Take Rate (e.g., 15%) upon completion, and credit the remainder to the Agency's digital wallet.
**Acceptance Scenarios**:

1. **Given** a visit is marked `completed` by the nurse, **When** the status change is registered, **Then** a background Celery task calculates the exact split, updates the `TRANSACTION` entity, and changes status from `escrow` to `settled`.

---

## 3. Database Schema Re-architecture (ERD)

Strict updates required in Django `models.py` to support multi-tenancy at the Agency level.

### 3.1 Entity: AGENCY_PROFILE (B2B Tenant)

- `id`: UUID (Primary Key)
- `manager_name`: String (Max 255)
- `commercial_registry`: String, Unique (Must be rigorously validated)
- `moh_license_number`: String, Unique
- `tax_id`: String, Unique
- `status`: Enum (`pending`, `verified`, `suspended`, `rejected`)
- `coverage_polygon`: PostGIS PolygonField (SRID 4326)
- `rating`: Float (0.0 to 5.0, Default: 5.0)
- `network_capacity`: Integer (Number of active nurses)
- `dispatch_mode`: Enum (`AUTO`, `MANUAL`)
- `wallet_balance`: DecimalField

### 3.2 Entity: NURSE_PROFILE (Employee)

- `id`: UUID (Primary Key)
- `user`: OneToOneField(User)
- `agency_id`: ForeignKey(AGENCY_PROFILE, on_delete=CASCADE). **CRITICAL MUST**: Nurses cannot exist without an Agency.
- `full_name`: String
- `national_id`: String, Unique
- `is_available`: Boolean
- `last_location`: PostGIS PointField (SRID 4326)

### 3.3 Entity: VISIT (The Core Transaction)

- `id`: UUID (Primary Key)
- `patient`: ForeignKey(User)
- `agency`: ForeignKey(AGENCY_PROFILE). _Denotes the entity legally responsible for fulfillment_.
- `nurse`: ForeignKey(NURSE_PROFILE, null=True).
- `status`: Enum (`pending_agency`, `pending_nurse`, `accepted`, `en_route`, `in_progress`, `completed`, `cancelled`)
- `patient_location`: PostGIS PointField
- `final_price`: DecimalField

### 3.4 Entity: TRANSACTION (Financials)

- `id`: UUID
- `visit`: OneToOneField(VISIT)
- `agency`: ForeignKey(AGENCY_PROFILE)
- `amount_paid`: DecimalField (Patient total)
- `wateen_take_rate`: DecimalField (The cut Wateen receives)
- `agency_payout`: DecimalField (Remainder owed to agency)
- `status`: Enum (`escrow`, `settled`, `refunded`)

---

## 4. Algorithmic Matching Logic & PostGIS

The P2P matching engine must be completely rewritten.
When `/api/visits/request/` is hit with a Point payload `(lng, lat)`, the system performs:

```python
# Django ORM Example Reference for the rewritten logic:
matched_agencies = AgencyProfile.objects.filter(
    status='verified',
    coverage_polygon__intersects=patient_point
).annotate(
    online_nurses_count=Count('nursenurseprofile', filter=Q(nursenurseprofile__is_available=True))
).filter(
    online_nurses_count__gt=0
).order_by('-rating', '-online_nurses_count')
```

If the first agency is `AUTO`, we broadcast via Channels/Redis to a specific group: `agency_{agency_id}_nurses`.
If the first agency is `MANUAL`, we broadcast to the Dashboard group: `agency_{agency_id}_admins`.
A Celery task `re_route_visit(visit_id, agency_index)` is spawned with a countdown of 180 seconds.

---

## 5. System Requirements (Functional & Non-Functional)

### 5.1 Functional Requirements (FR)

- **FR-001**: SuperAdmins MUST be able to forcefully suspend an Agency, immediately killing all active sessions for its nurses.
- **FR-002**: The System MUST strictly forbid any Nurse from operating or accepting visits if their parent Agency is suspended or drops below compliance thresholds.
- **FR-003**: Wateen MUST retain absolute control of the pricing engine. Agencies cannot set independent prices; pricing is hyper-local and dynamically set by Wateen's Yield Engine to prevent marketplace fragmentation.
- **FR-004**: The React Admin B2B SaaS dashboard MUST include a Real-Time Dispatch map utilizing WebSockets to show Agency admins exactly where their nurses are located via `last_location`.
- **FR-005**: All financial calculations MUST be performed server-side with atomic database transactions preventing race conditions during Escrow settlements.

### 5.2 Non-Functional Requirements (NFR)

- **NFR-001**: Spatial queries (PostGIS `ST_Intersects`) MUST resolve in under 50ms, requiring spatial indexing on `coverage_polygon` and `patient_location`.
- **NFR-002**: WebSocket broadcasting via Redis/Django Channels MUST support up to 5,000 concurrent Nurse connections without degrading the App Router SSR performance of Next.js.
- **NFR-003**: Data classification rules mandate that Patient medical history remains exclusively accessible to the assigned Nurse during the `in_progress` state and is subsequently masked post-completion. The Agency Admin may only see high-level metadata of the visit, not the granular clinical notes (Patient Privacy).

---

## 6. B2B2C API Specifications (Additions/Modifications)

### 6.1 B2B Agency Endpoints

`GET /api/v1/agency/{agency_id}/dashboard/overview`

- **Response**: Aggregated metrics (Revenue today, Active Nurses, Visits in progress).
- **Access**: `IsAgencyAdmin` permission class.

`POST /api/v1/agency/{agency_id}/coverage/`

- **Payload**: GeoJSON features array representing the `coverage_polygon`.
- **Action**: Updates the PostGIS geometry and invalidates geographic caches.

`POST /api/v1/agency/{agency_id}/dispatch/manual/`

- **Payload**: `{ "visit_id": "uuid", "nurse_id": "uuid" }`
- **Action**: Bypasses network push and directly alerts the specified nurse.

### 6.2 Security Paradigm Shift

- Transitioning to role-based access control (RBAC): `[SuperAdmin, AgencyAdmin, Nurse, Patient]`.
- JWT Tokens MUST now embed `agency_id` claims for Nurses and AgencyAdmins to facilitate row-level security and tenant isolation at the API layer.

---

## 7. Migration & Rollout Strategy

1. **Phase 1: Database Refactoring & Seed Scripts (Week 1)**
   - Create migrations adding `AGENCY_PROFILE` and modifying `NURSE_PROFILE`.
   - Write idempotency scripts to migrate legacy P2P nurses into a default "Wateen Internal Agency" temporarily to prevent data loss.

2. **Phase 2: Admin & B2B Dashboard Engineering (Week 2)**
   - Spin up the React Admin platform. Build the map-drawing components.

3. **Phase 3: Dispatch Engine Rewrite (Week 3)**
   - Replace the P2P spatial radius searches with Polygon Intersect searches.
   - Re-wire Celery tasks and WebSocket groups.

4. **Phase 4: Client Adjustments (Week 4)**
   - Next.js PWA: Update User Interfaces to reflect "Agency Assigned" instead of just "Nurse Assigned", adding corporate trust vectors to the UI.

---

## 8. Success Criteria

- **SC-001**: **100% Legal Compliance**: Zero technical pathways exist for a nurse to operate independently without a verified Agency.
- **SC-002**: **Routing Latency**: B2B2C matching engine completes spatial allocation in < 200ms.
- **SC-003**: **Zero Downtime Migration**: The transition from P2P schema to B2B2C schema completes via Django migrations without dropping core transactional data.
- **SC-004**: **Financial Integrity**: The escrow to settlement flow demonstrates 100% mathematical accuracy with zero floating-point discrepancies under concurrent load testing.

_Document finalized according to MIP v4.0 constraints. All subsequent development must adhere strictly to these architectural boundaries._
