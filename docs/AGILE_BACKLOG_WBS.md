# Wateen (وَتِين) — Master Agile Backlog & Work Breakdown Structure (WBS)

> **Project:** Wateen B2B2C Healthcare Aggregator  
> **Version:** 1.0 — February 2026  
> **Methodology:** Agile / Scrum (2-Week Sprints)  
> **Tech Stack:** Django 5, DRF, PostgreSQL/PostGIS, Redis, Django Channels, Next.js 14, React Admin, Stripe Connect  
> **Execution Model:** Hyper-Pair Programming (Solo Dev + AI)

---

## Phase 1: Database Refactoring & Multi-Tenancy (B2B2C Models & PostGIS Setup)

**Objective:** Re-architect the existing P2P database schema into a fully B2B2C-compliant data model with PostGIS spatial capabilities, establishing the foundational multi-tenant data layer for all downstream development.

---

### Ticket P1-T1: CustomUser Model Refactoring & RBAC Role System

**Context:** The existing `CustomUser` model must be extended to support the four primary roles (Patient, Agency Manager, Nurse, SuperAdmin) with a clean role-based access control layer. This is the prerequisite for all subsequent B2B2C authorization logic.

- **Task 1:** Refactor `users/models.py` — Add a `role` enum field (`PATIENT`, `AGENCY_ADMIN`, `NURSE`, `SUPERADMIN`) to `CustomUser`. Implement `@property` helpers (`is_agency_admin`, `is_nurse`, etc.) for clean permission checks throughout the codebase.
- **Task 2:** Create a DRF custom permission class `IsAgencyAdmin` in `users/permissions.py` that validates `request.user.role == AGENCY_ADMIN` and enforces that the user belongs to a `VERIFIED` agency. Apply this as the default permission for all B2B dashboard endpoints.
- **Task 3:** Write Django data migration (`users/migrations/000X_add_role_field.py`) that backfills existing user records with appropriate roles based on their current profile types. Ensure idempotency and rollback support.
- **Task 4:** Update `users/serializers.py` to expose `role` in registration and profile responses. Add validation logic that prevents role escalation (e.g., a Patient cannot self-assign `AGENCY_ADMIN`).

---

### Ticket P1-T2: AgencyProfile Entity & PostGIS Coverage Polygon

**Context:** The `AgencyProfile` is the core B2B entity. It must store KYC documents, financial metadata, and a PostGIS `coverage_polygon` with GIST indexing for sub-millisecond spatial queries.

- **Task 1:** Define `AgencyProfile` model in `users/models.py` with fields: `manager_name` (CharField), `commercial_registry` (CharField, unique), `moh_license_number` (CharField, unique), `tax_id` (CharField, unique), `status` (enum: PENDING/VERIFIED/SUSPENDED), `wallet_balance` (DecimalField, default=0.00), `stripe_account_id` (CharField, nullable), `rating` (FloatField, default=0.0), `network_capacity` (IntegerField), `dispatch_mode` (enum: AUTO/MANUAL).
- **Task 2:** Add `coverage_polygon` field as `django.contrib.gis.db.models.PolygonField(srid=4326, null=True)`. Create a GIST index via `Meta.indexes` using `GistIndex(fields=['coverage_polygon'])`. Verify PostGIS extension is enabled in the PostgreSQL instance via migration `CREATE EXTENSION IF NOT EXISTS postgis`.
- **Task 3:** Create `AgencyProfileSerializer` in `users/agency_serializers.py` using `rest_framework_gis.serializers.GeoFeatureModelSerializer` to handle GeoJSON input/output for the polygon field. Add validation that the polygon is closed and has >= 3 vertices.
- **Task 4:** Establish the `OneToOneField` relationship: `AgencyProfile.user -> CustomUser` (with `on_delete=CASCADE`). Add a Django signal in `users/signals.py` that auto-creates an empty `AgencyProfile` when a user registers with `role=AGENCY_ADMIN`.

---

### Ticket P1-T3: NurseProfile Entity & Agency Foreign Key Binding

**Context:** Under the B2B2C model, nurses are never freelancers. Every `NurseProfile` must have a mandatory `agency_id` FK, binding the nurse to their employing agency. This is a non-negotiable compliance constraint.

- **Task 1:** Define `NurseProfile` model with fields: `user` (OneToOneField -> CustomUser), `agency` (ForeignKey -> AgencyProfile, `on_delete=CASCADE`, **not nullable**), `full_name`, `national_id` (unique), `syndicate_id` (nursing syndicate number), `is_available` (BooleanField), `last_location` (PointField, srid=4326, nullable), `specializations` (JSONField for array of service type IDs).
- **Task 2:** Create `NurseProfileSerializer` with nested `AgencyProfile` read-only display. Add a custom `validate_agency` method that ensures the requesting user (Agency Admin) owns the agency they're assigning the nurse to — preventing cross-agency nurse hijacking.
- **Task 3:** Implement the nurse invitation flow: Agency Admin calls `POST /api/v1/agencies/invite-nurse/` with the nurse's email/phone. System creates a `CustomUser` with `role=NURSE` and an associated `NurseProfile` linked to the inviting agency. Generate a one-time activation token sent via SMS/email.

---

### Ticket P1-T4: Visit & Transaction Models Refactoring

**Context:** The `Visit` model is the atomic unit of value exchange. It must now carry `agency_id` as a mandatory FK and store an immutable pricing snapshot at creation time. The `Transaction` model handles the escrow/settlement ledger.

- **Task 1:** Refactor `visits/models.py` — Add `agency` (ForeignKey -> AgencyProfile, nullable until dispatch), `nurse` (ForeignKey -> NurseProfile, nullable until assignment). Implement the state machine: `PENDING_AGENCY -> PENDING_NURSE -> ACCEPTED -> EN_ROUTE -> IN_PROGRESS -> COMPLETED -> CANCELLED`. Add `ALLOWED_TRANSITIONS` dict and a `transition_to(new_status)` method with validation.
- **Task 2:** Add immutable pricing snapshot fields: `base_price`, `time_multiplier`, `distance_km`, `distance_rate`, `surge_coefficient`, `final_price` (all DecimalField). These are calculated and frozen at visit creation time and must never be mutated post-creation.
- **Task 3:** Define `Transaction` model: `visit` (OneToOneField), `agency` (FK), `amount_paid` (Decimal), `wateen_take_rate` (Decimal, default=15.00), `agency_payout` (computed: `amount_paid * (1 - take_rate/100)`), `status` (enum: ESCROWED/SETTLED/REFUNDED), `stripe_payment_intent_id`, `settled_at` (DateTimeField, nullable).
- **Task 4:** Create comprehensive Django Admin registrations for all new models with list filters, search fields, and read-only financial fields. Register `AgencyProfile` with a map widget for `coverage_polygon` using `django.contrib.gis.admin.GISModelAdmin`.

---

### Ticket P1-T5: Professional QA, Security & Validation

**Context:** Validate the entire database refactoring layer with unit tests, migration integrity checks, and security validation before any downstream development begins.

- **Task 1:** Write Pytest suite (`tests/test_models_b2b2c.py`) covering: AgencyProfile creation with valid/invalid polygons, NurseProfile mandatory agency binding (assert `IntegrityError` on null agency), Visit state machine transitions (valid and invalid), Transaction computation accuracy (verify `agency_payout = amount_paid * 0.85`).
- **Task 2:** Write migration integrity tests — verify forward and backward migration compatibility. Test that the data migration correctly backfills roles for existing users. Run `python manage.py migrate --check` in CI to ensure no missing migrations.
- **Task 3:** Security validation — Write tests confirming: a Nurse cannot access Agency Admin endpoints (403), a Patient cannot modify Visit pricing fields (read-only enforcement), role escalation is blocked at the serializer level, and `coverage_polygon` updates require `VERIFIED` agency status.
- **Task 4:** Run `ruff check .` and `mypy` for type safety across all modified files. Verify all new models appear correctly in Django Admin with proper field rendering.

---

## Phase 2: Agency KYC & Onboarding B2B Dashboard (React Admin)

**Objective:** Build the complete Agency onboarding pipeline — from document upload and KYC verification to the B2B SaaS Dashboard that Agency Managers use to manage their operations, nurses, and settings.

---

### Ticket P2-T1: Agency Registration API & Document Upload

**Context:** Agencies must submit legal documents (Commercial Registry PDF, MoH License, Tax Card) during registration. These documents are stored in S3-compatible storage and queued for SuperAdmin review.

- **Task 1:** Create `POST /api/v1/agencies/register/` endpoint in `users/agency_views.py`. Accept multipart form data with fields: `manager_name`, `commercial_registry_file` (PDF/Image), `moh_license_file`, `tax_id_file`, `phone`, `email`. Validate file types (PDF, PNG, JPG only) and max size (10MB per file).
- **Task 2:** Implement file storage backend — configure `django-storages` with S3-compatible storage (or local `MEDIA_ROOT` for dev). Files are stored under `agencies/{agency_id}/kyc/` namespace. Generate pre-signed URLs for secure document viewing by SuperAdmin.
- **Task 3:** Create `KYCDocument` model: `agency` (FK), `document_type` (enum: COMMERCIAL_REG/MOH_LICENSE/TAX_CARD), `file` (FileField), `uploaded_at`, `review_status` (PENDING/APPROVED/REJECTED), `reviewer_notes` (TextField). Track document versions for re-upload scenarios.
- **Task 4:** Implement notification trigger — upon successful document upload, create a Celery task that sends a notification to the SuperAdmin dashboard queue (Redis channel) indicating a new agency is pending KYC review.

---

### Ticket P2-T2: SuperAdmin KYC Verification Queue

**Context:** SuperAdmins need a dedicated queue to review, approve, or reject agency applications. This is a critical trust layer — no agency can operate on Wateen without passing KYC.

- **Task 1:** Create `GET /api/v1/admin/kyc-queue/` endpoint returning paginated list of agencies with `status=PENDING`, ordered by submission date. Include nested document URLs, manager contact info, and submission timestamp.
- **Task 2:** Create `PATCH /api/v1/admin/kyc-review/{agency_id}/` endpoint accepting `action` (APPROVE/REJECT) and `notes`. On APPROVE: set `AgencyProfile.status = VERIFIED`, send congratulatory email/SMS to agency manager. On REJECT: set status to `SUSPENDED`, include rejection reason.
- **Task 3:** Build a React Admin `<KYCReviewList>` component displaying the queue with columns: Agency Name, Submission Date, Document Count, Review Status. Each row expands to show document previews (PDF viewer) and APPROVE/REJECT action buttons.
- **Task 4:** Add audit trail — every KYC action (approve/reject/re-review) is logged in a `KYCAuditLog` table with `reviewer_id`, `action`, `timestamp`, and `notes`. This satisfies MoH compliance requirements for accountability.

---

### Ticket P2-T3: B2B Agency Dashboard — Core CRUD & Settings

**Context:** The Agency Dashboard is the SaaS product Wateen provides to agencies. Built with React Admin, it must support RTL layout, agency profile editing, and configuration of dispatch preferences.

- **Task 1:** Initialize the React Admin application in `frontend/admin/` with RTL support using `ra-i18n-polyglot` and Arabic language pack. Configure the `<Admin>` component with a custom dark-mode theme using Wateen brand colors (`#0066FF`, `#FFB300`).
- **Task 2:** Build `<AgencySettings>` page — allows the Agency Manager to edit: `manager_name`, `phone`, `email`, `dispatch_mode` toggle (AUTO/MANUAL), and business hours (JSON field). All changes hit `PATCH /api/v1/agencies/profile/`.
- **Task 3:** Build `<NurseManagement>` resource — CRUD interface for the agency's nurse roster. List view shows: Nurse Name, Status (Online/Offline), Current Assignment, Specializations. Create/Edit form includes: nurse details + ability to toggle `is_available`.
- **Task 4:** Implement sidebar navigation with sections: Dashboard Home, Nurse Management, Coverage Area, Visit Queue, Financial Statements, Settings. Apply glassmorphism styling with `backdrop-filter: blur()` and subtle gradient accents.

---

### Ticket P2-T4: Nurse Invitation & Onboarding Flow

**Context:** Agency Admins must be able to invite nurses to join their agency roster. The flow must be secure (token-based) and prevent a nurse from belonging to multiple agencies simultaneously.

- **Task 1:** Create `POST /api/v1/agencies/nurses/invite/` endpoint accepting `email` and `phone`. Generate a unique `invitation_token` (UUID) with 72-hour expiry stored in `NurseInvitation` model. Send SMS/email with a deep link to the Nurse PWA registration page.
- **Task 2:** Create `POST /api/v1/auth/accept-invitation/` endpoint. Validates the token, creates `CustomUser` + `NurseProfile` linked to the inviting agency. If the nurse already has an account with another agency, return `409 CONFLICT` with message "Nurse is already affiliated with another agency."
- **Task 3:** Build the invitation management UI in React Admin — `<InvitationList>` showing: Invited Email, Status (Pending/Accepted/Expired), Sent Date. Add "Resend" and "Revoke" action buttons.
- **Task 4:** Add backend validation: enforce a configurable `MAX_NURSES_PER_AGENCY` limit (default: 50). When the limit is reached, the invite endpoint returns `429` with a clear upgrade prompt.

---

### Ticket P2-T5: Professional QA, Security & Validation

**Context:** Validate the entire KYC pipeline and B2B dashboard functionality with integration tests, security audits, and UI testing.

- **Task 1:** Write Pytest integration tests for the full KYC lifecycle: register agency -> upload documents -> SuperAdmin reviews -> approve/reject -> verify agency status transition. Test edge cases: duplicate commercial registry, expired documents, re-upload after rejection.
- **Task 2:** Write security tests: verify that Agency A cannot view Agency B's documents (tenant isolation), file upload rejects executable files (.exe, .sh), pre-signed URLs expire after configured TTL, and unauthenticated users cannot access the KYC queue.
- **Task 3:** Write Jest + React Testing Library tests for React Admin components: `<KYCReviewList>` renders correctly with mock data, APPROVE/REJECT buttons trigger correct API calls, `<NurseManagement>` CRUD operations work end-to-end with MSW (Mock Service Worker).
- **Task 4:** Perform a manual security review: ensure all file uploads are scanned for malware signatures, document URLs are not guessable, and the KYC audit trail is immutable (no DELETE endpoint exposed).

---

## Phase 3: Geospatial Infrastructure & Polygon Mapping (OSM + leaflet-geoman)

**Objective:** Implement the complete OpenStreetMap-based geospatial infrastructure, enabling agencies to define coverage polygons via an interactive map editor and enabling the backend to perform high-performance spatial queries for dispatch.

---

### Ticket P3-T1: PostGIS Spatial Query Infrastructure

**Context:** PostGIS is the backbone of Wateen's geographic intelligence. All spatial queries (intersection, distance, containment) must be optimized with proper indexing and tested for performance under load.

- **Task 1:** Ensure PostGIS extension is active and properly configured in all environments (local Docker, staging, production). Create a dedicated Django management command `python manage.py verify_postgis` that checks: extension version, GIST index existence on `coverage_polygon`, and runs a benchmark `ST_Intersects` query.
- **Task 2:** Implement the core spatial query function in `visits/services/geo_service.py`: `find_agencies_covering_point(lat, lng)` — executes `AgencyProfile.objects.filter(status='VERIFIED', coverage_polygon__intersects=Point(lng, lat, srid=4326))`. Return queryset annotated with `distance` from the point to the polygon centroid.
- **Task 3:** Add Nominatim geocoding integration in `visits/services/geocoding_service.py` — `geocode_address(address_text)` calls the Nominatim API (self-hosted or public) with rate limiting (1 req/sec for public). Cache results in Redis with 24-hour TTL to minimize external calls.
- **Task 4:** Create a spatial diagnostics API endpoint `GET /api/v1/geo/diagnostics/` (SuperAdmin only) that returns: total agencies with valid polygons, polygon complexity statistics (avg vertices), GIST index status, and last Nominatim cache hit rate.

---

### Ticket P3-T2: react-leaflet Map Integration (Frontend)

**Context:** The interactive map is the primary interface for coverage polygon visualization and patient location selection. It must render OSM tiles, support RTL layout, and perform smoothly with complex polygons.

- **Task 1:** Install and configure `leaflet`, `react-leaflet`, and `@geoman-io/leaflet-geoman-free` in the Next.js frontend. Create a reusable `<WateenMap>` component that renders OpenStreetMap tiles with proper Arabic locale tile labels (where available). Set default viewport to Greater Cairo (30.0444°N, 31.2357°E).
- **Task 2:** Build `<CoveragePolygonEditor>` component — wraps `<WateenMap>` with leaflet-geoman drawing controls enabled. Supports: draw polygon, edit vertices, delete polygon, and undo. On save, exports the polygon as GeoJSON and sends it to `POST /api/v1/agencies/coverage/`.
- **Task 3:** Build `<PatientLocationPicker>` component — a simplified map view for patients to confirm their location. Supports: GPS auto-detect (with fallback prompt), manual pin drop, and address search bar (powered by Nominatim). Emits `{ latitude, longitude }` on confirmation.
- **Task 4:** Optimize map rendering for RTL — mirror zoom controls to the left side, ensure popup/tooltip text is right-aligned for Arabic content, and test with polygons that cross the Nile (complex geometry edge case).

---

### Ticket P3-T3: Coverage Polygon CRUD API

**Context:** Backend endpoints for agencies to create, read, update, and delete their coverage polygons. All spatial data must be validated and stored with GIST indexing.

- **Task 1:** Implement `POST /api/v1/agencies/coverage/` — accepts GeoJSON polygon body. Validates: polygon is closed, minimum 3 vertices, area does not exceed maximum threshold (prevent agencies from claiming all of Egypt), and polygon does not self-intersect. Store with `srid=4326`.
- **Task 2:** Implement `GET /api/v1/agencies/coverage/` — returns the calling agency's polygon as GeoJSON Feature with properties (area in km², centroid coordinates, vertex count). If no polygon exists, return `404` with a prompt to draw one.
- **Task 3:** Implement `PUT /api/v1/agencies/coverage/` — full polygon replacement. Triggers a background Celery task to re-evaluate any `PENDING_AGENCY` visits that were previously routed to this agency but now fall outside the updated polygon.
- **Task 4:** Implement `DELETE /api/v1/agencies/coverage/` — soft-delete (set polygon to null). Prevents deletion if agency has active visits (`status IN (ACCEPTED, EN_ROUTE, IN_PROGRESS)`). Return `409 CONFLICT` with active visit count.

---

### Ticket P3-T4: OSRM/ORS Routing Integration

**Context:** After spatial matching identifies eligible agencies, the system needs driving distance and ETA from the nearest nurse to the patient. This powers the pricing engine's distance component and the ranking algorithm's ETA factor.

- **Task 1:** Create `visits/services/routing_service.py` with a `RouteResult` dataclass containing: `distance_km`, `duration_minutes`, `polyline_geometry`. Implement `get_route(origin_lat, origin_lng, dest_lat, dest_lng)` calling OSRM's `/route/v1/driving/` endpoint.
- **Task 2:** Add ORS (OpenRouteService) as a fallback routing provider. Implement provider abstraction: `RoutingProvider` base class with `OSRMProvider` and `ORSProvider` subclasses. Configuration via `ROUTING_PROVIDER` Django setting with automatic failover.
- **Task 3:** Implement route caching in Redis — cache `RouteResult` objects keyed by `geohash(origin):geohash(dest)` with 15-minute TTL. This prevents redundant API calls for nearby locations during high-demand periods.
- **Task 4:** Create a nurse-to-patient ETA calculation utility: `calculate_nurse_eta(nurse_profile, patient_location)` — fetches the nurse's `last_location` (PointField), calls the routing service, and returns the `RouteResult`. Handle edge case where nurse has no `last_location` (return `None` ETA, flag for GPS update).

---

### Ticket P3-T5: Professional QA, Security & Validation

**Context:** Validate all geospatial operations for correctness, performance, and security. Spatial bugs can cause incorrect dispatch (wrong agency for wrong location) with real patient safety implications.

- **Task 1:** Write Pytest tests for spatial queries: create test polygons for Cairo, Alexandria, and Giza. Verify `ST_Intersects` returns correct agencies for points inside/outside/on-boundary of polygons. Test overlapping polygon scenarios (two agencies covering the same point).
- **Task 2:** Performance benchmark: create 500 test agencies with realistic polygons (50-100 vertices each). Measure `find_agencies_covering_point()` execution time — must be < 50ms. If exceeded, investigate query plan with `EXPLAIN ANALYZE` and optimize GIST index configuration.
- **Task 3:** Write frontend tests for map components: `<CoveragePolygonEditor>` correctly exports valid GeoJSON, `<PatientLocationPicker>` emits correct coordinates, map renders without JavaScript errors in RTL mode. Use Playwright for E2E map interaction tests.
- **Task 4:** Security validation: verify that Agency A cannot read/modify Agency B's polygon (tenant isolation), invalid GeoJSON payloads are rejected with descriptive errors (not 500), and the Nominatim integration does not leak patient addresses in server logs.

---

## Phase 4: Two-Tier Dispatch & Routing Engine (Backend PostGIS Logic)

**Objective:** Build the complete dispatch engine that matches patient requests to the optimal agency via spatial intersection, ranks candidates using the QualityScore algorithm, and supports both Manual and Auto dispatch modes with timeout-based escalation.

---

### Ticket P4-T1: Visit Request Pipeline & Pricing Snapshot

**Context:** When a patient submits a visit request, the system must capture their location, calculate the price, find eligible agencies, and create the Visit record with an immutable pricing snapshot — all within a single atomic transaction.

- **Task 1:** Implement `POST /api/v1/visits/request/` in `visits/request_views.py`. Accept: `service_type_id`, `latitude`, `longitude`, `urgency` (low/medium/high), `notes`. Wrap the entire operation in `transaction.atomic()`. If no agencies cover the patient's point, return `404` with "No agencies available in your area."
- **Task 2:** Build the pricing engine function `calculate_cognitive_price(...)` in `visits/services/pricing_service.py`. Implement the Cognitive Pricing Engine formula (`P_final`). Freeze all components into the Visit's snapshot fields at creation time.
- **Task 3:** On successful visit creation, trigger the dispatch pipeline via Celery: `dispatch_visit.delay(visit_id)`. The task calls `find_agencies_covering_point()`, ranks results, and routes to the top-ranked agency. Set visit status to `PENDING_AGENCY`.
- **Task 4:** Create `ServiceType` model: `name` (CharField), `name_ar` (CharField for Arabic), `base_price` (Decimal), `icon` (CharField for frontend icon key), `requires_prescription` (Boolean), `estimated_duration_minutes` (Integer). Seed with initial service types: General Nursing, Wound Care, IV Therapy, Post-Op Care, Elderly Care.

---

### Ticket P4-T2: Agency Ranking & QualityScore Algorithm

**Context:** When multiple agencies cover a patient's location (overlapping polygons), the system must rank them using a weighted scoring algorithm that considers rating, capacity, and historical response time.

- **Task 1:** Implement `rank_agencies(agencies_queryset, patient_location, urgency)` in `visits/services/ranking_service.py`. For each agency, compute: `Score = (W_q * Q) + (W_r * R) + (W_p * P)`. `W` = urgency weights, `Q` = clinical quality, `R` = operational reliability, `P` = spatial proximity.
- **Task 2:** Add `response_rate` computed property to `AgencyProfile` — query the last 100 visits for the agency and calculate `accepted_count / total_count`. Cache this value in Redis with 1-hour TTL to avoid repeated DB queries during high-traffic periods.
- **Task 3:** Implement the ETA-enhanced ranking variant: `M_a = (R_a × 0.5) + (1/E_a × 0.3) + (C_a × 0.2)`. When OSRM is available, ETA is used instead of raw capacity. This provides distance-aware ranking that favors agencies whose nearest nurse is physically closer.
- **Task 4:** Create an admin-facing `GET /api/v1/admin/dispatch-analytics/` endpoint that returns: average QualityScore by agency, dispatch success rate, average time-to-first-response, and re-route frequency. This powers the SuperAdmin's operational dashboard.

---

### Ticket P4-T3: Manual Dispatch Mode Implementation

**Context:** In Manual Mode, the visit request appears on the Agency Dashboard. The Agency Admin has a 300-second countdown to review available nurses and manually assign one. If the timer expires, the visit escalates to the next agency.

- **Task 1:** Create `GET /api/v1/agencies/visit-queue/` — returns all visits with `status=PENDING_AGENCY` and `agency_id=requesting_agency`. Include: patient location (masked to district level), service type, urgency, time remaining on the 300-second countdown, and estimated price.
- **Task 2:** Create `POST /api/v1/agencies/dispatch/manual/` — accepts `visit_id` and `nurse_id`. Validates: the nurse belongs to the agency, the nurse is currently `is_available=True`, and the visit is still in `PENDING_AGENCY` status. On success, transition visit to `PENDING_NURSE` and push notification to the nurse's device.
- **Task 3:** Implement the countdown timer backend: when a visit enters `PENDING_AGENCY`, schedule a Celery task `re_route_visit.apply_async(args=[visit_id], countdown=300)`. If the visit status is still `PENDING_AGENCY` when the task fires, set `agency_id` to the next-ranked agency and repeat the dispatch cycle.
- **Task 4:** Build the `<VisitQueue>` React Admin component — real-time list with countdown badges (green > 120s, amber > 60s, red < 60s). Each row has "Assign Nurse" button that opens a modal with available nurse roster, showing each nurse's current location and distance to patient.

---

### Ticket P4-T4: Auto-Dispatch Mode Implementation

**Context:** In Auto Mode, Wateen automatically pings the top 5 optimal nurses within the matched agency. The first nurse to accept claims the visit. This is the "Uber-style" dispatch experience.

- **Task 1:** Implement `auto_dispatch_to_nurses(visit_id, agency_id)` in `visits/services/dispatch_service.py`. Query the agency's online, available nurses. Rank by proximity to patient (using `last_location` PointField and `ST_Distance`). Select the top 5 candidates.
- **Task 2:** For each candidate nurse, create a `DispatchOffer` model record: `visit` (FK), `nurse` (FK), `offered_at` (DateTime), `status` (PENDING/ACCEPTED/REJECTED/EXPIRED), `expires_at` (DateTime, +60 seconds). Send a push notification (or WebSocket event) to each nurse.
- **Task 3:** Create `POST /api/v1/nurses/respond-offer/` — accepts `offer_id` and `action` (ACCEPT/REJECT). On ACCEPT: verify no other nurse has already claimed this visit (race condition guard using `select_for_update()`). Transition visit to `ACCEPTED`, mark all other offers as `EXPIRED`. On REJECT: mark offer as `REJECTED`.
- **Task 4:** Handle the "no nurses available" edge case: if all 5 offers expire or are rejected, increment the agency's `failed_dispatch_count` metric and trigger `re_route_visit` to the next-ranked agency. If no agencies remain, transition visit to `CANCELLED` with reason "No available nurses in your area" and refund any held payment.

---

### Ticket P4-T5: Professional QA, Security & Validation

**Context:** The dispatch engine is mission-critical — incorrect routing can cause patient care delays. Exhaustive testing of all dispatch paths, race conditions, and edge cases is mandatory.

- **Task 1:** Write Pytest integration tests for the complete dispatch lifecycle: patient creates visit -> system finds 3 overlapping agencies -> ranks by QualityScore -> routes to Agency #1 (Manual mode) -> times out -> re-routes to Agency #2 (Auto mode) -> Nurse #3 accepts -> visit transitions to ACCEPTED.
- **Task 2:** Write race condition tests for Auto-Dispatch: simulate two nurses accepting the same offer simultaneously using Django's `select_for_update()`. Verify only one succeeds and the other receives a `409 CONFLICT`. Use `threading` module or `pytest-asyncio` for concurrent test execution.
- **Task 3:** Write pricing engine tests: verify formula accuracy with known inputs, test surge coefficient boundaries (max 3.0x), test night shift multiplier (1.2x between 22:00-06:00), and verify price snapshot immutability (attempt to PATCH price fields and confirm 400 response).
- **Task 4:** Load testing with Locust: simulate 500 concurrent visit requests across 50 agencies with overlapping polygons. Measure: average dispatch time, `ST_Intersects` query performance, Celery task queue depth, and Redis cache hit rate. Target: < 2 seconds from request to first nurse notification.

---

## Phase 5: Real-Time Sockets & Polling System (Django Channels + Redis)

**Objective:** Implement bidirectional real-time communication between all platform actors (Patient, Nurse, Agency Admin) using Django Channels and Redis Pub/Sub, enabling live visit status updates, location tracking, and instant notifications.

---

### Ticket P5-T1: Django Channels WebSocket Infrastructure

**Context:** WebSockets are the backbone of real-time features — visit status changes, nurse location updates, and dispatch notifications must reach clients within 500ms. Django Channels with Redis as the channel layer provides this capability.

- **Task 1:** Configure Django Channels in `config/asgi.py` — define `ProtocolTypeRouter` with HTTP and WebSocket protocols. Set up `AuthMiddlewareStack` for JWT-authenticated WebSocket connections. Configure `channels_redis` as the channel layer backend pointing to the Redis instance.
- **Task 2:** Create `VisitConsumer` in `visits/consumers.py` — handles WebSocket connections for visit tracking. On connect, join the room group `visit_{visit_id}`. Broadcast status transitions, nurse location updates, and ETA refreshes to all group members (patient + nurse + agency admin).
- **Task 3:** Create `AgencyDashboardConsumer` — Agency Admins join room `agency_{agency_id}`. Receives: new visit requests entering the queue, countdown timer ticks, nurse availability changes, and financial settlement notifications.
- **Task 4:** Implement token-based WebSocket authentication — parse JWT from the WebSocket URL query string (`ws://host/ws/visits/?token=xxx`). Validate the token in the middleware and attach the user to the scope. Reject unauthenticated connections with `4401` close code.

---

### Ticket P5-T2: Visit Status Real-Time Broadcasting

**Context:** Every visit status transition must be broadcast in real-time to all stakeholders. This powers the live tracking UI for patients and the operational dashboard for agencies.

- **Task 1:** Create a Django signal handler `post_save` on Visit model — whenever `status` changes, call `channel_layer.group_send(f"visit_{visit.id}", {"type": "visit.status_update", "status": new_status, "timestamp": now})`. Ensure this signal fires within `transaction.on_commit()` to prevent broadcasting uncommitted changes.
- **Task 2:** Implement `NurseLocationConsumer` — nurses send periodic GPS updates (every 30 seconds while `EN_ROUTE` or `IN_PROGRESS`). The consumer validates the coordinates, updates `NurseProfile.last_location`, and broadcasts to the visit group for live map tracking.
- **Task 3:** Build the frontend WebSocket client hook `useVisitSocket(visitId)` in the Next.js app — returns `{ status, nurseLocation, eta, isConnected }`. Handles: automatic reconnection with exponential backoff (1s, 2s, 4s, max 30s), connection state UI indicator, and graceful degradation to polling if WebSocket fails.
- **Task 4:** Implement a REST polling fallback endpoint `GET /api/v1/visits/{id}/status/` — returns current visit status, nurse location, and last update timestamp. The frontend falls back to 10-second polling if the WebSocket connection cannot be established (e.g., corporate firewalls).

---

### Ticket P5-T3: Push Notification System

**Context:** For events that occur while the app is not in the foreground (nurse receives dispatch offer, patient's nurse arrives), push notifications via Firebase Cloud Messaging (FCM) or Web Push API are required.

- **Task 1:** Integrate FCM SDK — create `notifications/services/push_service.py` with `send_push(user_id, title, body, data_payload)`. Store device FCM tokens in a `DeviceToken` model: `user` (FK), `token` (CharField), `platform` (ANDROID/IOS/WEB), `last_active` (DateTime).
- **Task 2:** Define notification templates for key events: `NURSE_ASSIGNED` ("Your nurse {name} is on the way"), `NURSE_ARRIVED` ("Your nurse has arrived"), `VISIT_COMPLETED` ("Visit completed, rate your experience"), `DISPATCH_OFFER` ("New visit request — {service_type} in {district}"), `PAYMENT_SETTLED` ("Payment of {amount} EGP settled").
- **Task 3:** Create a Celery task `send_notification.delay(user_id, template_key, context)` — renders the template with context, resolves all device tokens for the user, and sends via FCM batch API. Log delivery status in `NotificationLog` model for debugging.
- **Task 4:** Implement notification preferences: `UserNotificationPrefs` model with toggles for each notification category (visit_updates, financial, marketing). The push service checks preferences before sending. Expose via `GET/PATCH /api/v1/users/notification-prefs/`.

---

### Ticket P5-T4: Live Dashboard Data Streams

**Context:** The Agency Dashboard and SuperAdmin Dashboard need live-updating metrics — active visit count, online nurse count, queue depth, and revenue tickers — without manual page refresh.

- **Task 1:** Create `DashboardMetricsConsumer` — Agency Admins connect to `ws://host/ws/dashboard/`. Every 10 seconds, the consumer queries and broadcasts: `active_visits_count`, `online_nurses_count`, `pending_queue_depth`, `today_revenue`, `today_completed_visits`.
- **Task 2:** Implement efficient metric aggregation — use Django's `aggregate()` and `annotate()` to compute dashboard metrics in a single query. Cache the result in Redis with 10-second TTL. The WebSocket consumer reads from cache, not DB directly, to prevent query amplification under many concurrent dashboard connections.
- **Task 3:** Build the `<LiveDashboard>` React Admin component — displays metric cards with animated number transitions (count-up effect). Cards: "Active Visits" (blue), "Online Nurses" (green), "Queue Depth" (amber if > 5), "Today's Revenue" (with EGP currency format). Use `framer-motion` for smooth value transitions.
- **Task 4:** Implement the SuperAdmin "Command Center" view — a unified dashboard showing metrics across ALL agencies. Includes: national heatmap of active visits, agency leaderboard by QualityScore, system health indicators (Redis latency, Celery queue depth, WebSocket connection count).

---

### Ticket P5-T5: Professional QA, Security & Validation

**Context:** WebSocket connections introduce new attack vectors (connection flooding, unauthorized room access, message injection). Testing must cover both functional correctness and security hardening.

- **Task 1:** Write Pytest tests using `channels.testing.WebsocketCommunicator` — verify: authenticated connection succeeds, unauthenticated connection is rejected (4401), visit status broadcasts reach all group members, and nurse location updates are persisted to the database.
- **Task 2:** Write security tests: verify a Patient cannot join an Agency's dashboard room, a Nurse from Agency A cannot receive broadcasts for Agency B's visits, WebSocket message payloads are validated (reject malformed JSON, oversized messages > 4KB), and connection rate limiting (max 5 connections per user).
- **Task 3:** Stress test WebSocket infrastructure: use Locust's WebSocket plugin to simulate 5000 concurrent connections. Measure: connection establishment time, message broadcast latency, Redis channel layer memory usage, and server CPU/RAM under load. Target: < 500ms broadcast latency at 5000 connections.
- **Task 4:** Test fallback mechanisms: disable Redis temporarily and verify the polling fallback activates, test reconnection logic with simulated network interruptions, and verify that no visit updates are lost during a brief reconnection window (messages are replayed from the last known sequence number).

---

## Phase 6: Financial Escrow & Settlement Engine (Stripe Connect)

**Objective:** Implement the complete financial lifecycle — from patient payment authorization through Stripe Connect Destination Charges, to escrow holding during visits, automatic settlement upon completion, and agency wallet management with withdrawal capabilities.

---

### Ticket P6-T1: Stripe Connect Onboarding for Agencies

**Context:** Each agency needs a Stripe Connected Account to receive payouts. The onboarding flow must collect banking details and complete Stripe's identity verification requirements.

- **Task 1:** Implement `POST /api/v1/agencies/stripe/onboard/` — calls Stripe API to create a Connected Account (`type=express`). Generates an AccountLink URL for the agency to complete Stripe's hosted onboarding. Store `stripe_account_id` on `AgencyProfile`. Redirect agency back to dashboard on completion.
- **Task 2:** Create a Stripe webhook handler at `POST /api/v1/webhooks/stripe/` — listen for `account.updated` events. When the agency's Stripe account becomes `charges_enabled=True`, update `AgencyProfile.stripe_onboarding_status = COMPLETE`. If verification fails, set status to `REQUIRES_ACTION` and notify the agency.
- **Task 3:** Build the `<StripeOnboarding>` React Admin component — shows current Stripe status (Not Started / In Progress / Complete / Action Required). Includes "Complete Setup" button that opens the Stripe AccountLink in a new tab. Display a warning badge on the dashboard header if Stripe setup is incomplete.
- **Task 4:** Add backend guardrail: agencies with `stripe_onboarding_status != COMPLETE` cannot receive visit assignments. The dispatch engine filters them out of the candidate pool. Show a clear message in the Agency Dashboard: "Complete Stripe setup to start receiving visits."

---

### Ticket P6-T2: Payment Intent & Escrow Logic

**Context:** When a patient confirms a visit request, Wateen creates a Stripe PaymentIntent using Destination Charges. Funds are authorized (not captured) on the patient's card and held in escrow until the visit completes.

- **Task 1:** Implement `create_payment_intent(visit)` in `visits/services/payment_service.py` — calls `stripe.PaymentIntent.create()` with `amount=visit.final_price`, `currency='egp'`, `capture_method='manual'` (for escrow hold), `transfer_data={'destination': agency.stripe_account_id}`, `application_fee_amount=visit.final_price * 0.15`.
- **Task 2:** Create `POST /api/v1/payments/intent/` endpoint — called by the patient frontend after confirming the visit. Returns `client_secret` for Stripe.js to render the payment form. On successful authorization, update `Transaction.status = ESCROWED` and transition visit to `PENDING_AGENCY`.
- **Task 3:** Implement escrow capture on visit completion: when visit transitions to `COMPLETED`, the `post_save` signal triggers `capture_escrowed_payment(visit)` — calls `stripe.PaymentIntent.capture()`. On success, update `Transaction.status = SETTLED`, `Transaction.settled_at = now()`, and credit `AgencyProfile.wallet_balance += agency_payout`.
- **Task 4:** Handle payment failures gracefully: if the patient's card is declined, return a user-friendly error (not raw Stripe error). If capture fails after visit completion (rare), log a critical alert, set Transaction to `SETTLEMENT_FAILED`, and enqueue for manual reconciliation by SuperAdmin.

---

### Ticket P6-T3: Agency Wallet & Transaction History

**Context:** Agencies need a clear view of their financial position — escrowed funds (in-flight visits), available balance (completed visits), and full transaction history for accounting purposes.

- **Task 1:** Implement wallet balance computation — `AgencyProfile` exposes two computed properties: `escrowed_balance` (sum of `Transaction.agency_payout` where `status=ESCROWED`), `available_balance` (sum where `status=SETTLED` minus sum of successful withdrawals). Both are computed from the ledger, not stored as mutable fields, to ensure consistency.
- **Task 2:** Create `GET /api/v1/agencies/wallet/` endpoint — returns: `escrowed_balance`, `available_balance`, `total_earned` (all-time), `pending_withdrawal` (if any). Include `last_settlement` timestamp and `next_payout_date` (based on the twice-weekly schedule).
- **Task 3:** Create `GET /api/v1/agencies/transactions/` — paginated transaction history with filters: `date_range`, `status`, `type` (visit_earning, withdrawal, refund). Each entry includes: visit reference, patient district (masked), service type, gross amount, platform fee, net payout, and status.
- **Task 4:** Build the `<FinancialDashboard>` React Admin component — top section shows wallet cards (Escrowed / Available / Total with animated counters). Below, a filterable transaction table with CSV export. Include a revenue chart (daily/weekly/monthly) using a lightweight charting library (Recharts or Chart.js).

---

### Ticket P6-T4: Withdrawal & Payout Processing

**Context:** Agencies can request withdrawal of their available balance. Payouts are processed twice weekly (Sunday and Wednesday) via Stripe Transfers to the agency's connected bank account.

- **Task 1:** Create `POST /api/v1/agencies/wallet/withdraw/` — validates: `amount <= available_balance`, `amount >= minimum_withdrawal` (100 EGP), agency's Stripe account is fully verified. Create a `Withdrawal` model record: `agency`, `amount`, `status` (PENDING/PROCESSING/COMPLETED/FAILED), `requested_at`, `processed_at`.
- **Task 2:** Implement a Celery periodic task `process_pending_withdrawals` scheduled for Sunday and Wednesday at 10:00 AM Cairo time. Queries all `Withdrawal.status=PENDING`, calls `stripe.Transfer.create()` for each, and updates status. On failure, retry up to 3 times with exponential backoff before marking as `FAILED`.
- **Task 3:** Build withdrawal UI in the Agency Dashboard — "Request Withdrawal" button on the Financial Dashboard. Shows a form with current available balance, withdrawal amount input, and estimated processing date. Display withdrawal history with status badges (Pending=amber, Completed=green, Failed=red).
- **Task 4:** Implement cancellation refund flow: if a visit is cancelled after escrow but before completion, trigger `cancel_payment_intent(visit)` — calls `stripe.PaymentIntent.cancel()`. Update `Transaction.status = REFUNDED`. If the patient's card was charged, initiate a Stripe Refund. Handle partial refunds for late cancellations (patient pays cancellation fee).

---

### Ticket P6-T5: Professional QA, Security & Validation

**Context:** Financial code requires the highest level of testing rigor. Incorrect calculations, race conditions in settlement, or webhook replay attacks can cause real monetary loss.

- **Task 1:** Write Pytest tests for the complete payment lifecycle using Stripe's test mode API keys: create PaymentIntent -> authorize -> confirm visit completion -> capture -> verify agency wallet balance. Test with various amounts, currencies, and error scenarios (insufficient funds, expired card, network timeout).
- **Task 2:** Write race condition tests for settlement: simulate two concurrent `COMPLETED` status transitions for the same visit. Verify the payment is captured exactly once (idempotency). Test using Stripe's idempotency keys and Django's `select_for_update()`.
- **Task 3:** Write webhook security tests: verify signature validation (`stripe.Webhook.construct_event`), test replay attack prevention (reject events with timestamps > 5 minutes old), verify that unrecognized event types are logged but do not cause errors, and test webhook retry handling (Stripe retries failed webhooks).
- **Task 4:** Financial reconciliation test: create 100 test visits with various outcomes (completed, cancelled, refunded). Run the reconciliation script and verify: sum of all `Transaction.agency_payout` matches sum of Stripe transfers, platform fee total matches expected 15% take rate, and no orphaned transactions exist.

---

## Phase 7: Next.js PWAs Integration (Patient & Nurse Apps)

**Objective:** Build production-grade Progressive Web Applications for Patients and Nurses using Next.js 14 App Router with full RTL Arabic support, offline capabilities, and premium Glassmorphism UI — delivering an app-like experience without native app store dependencies.

---

### Ticket P7-T1: Patient PWA — Service Request & Discovery

**Context:** The Patient PWA is the B2C entry point. Patients must be able to discover services, select their location, view pricing, and submit visit requests with a seamless mobile-first experience.

- **Task 1:** Initialize the Patient PWA in `frontend/patient/` using Next.js 14 App Router. Configure: `next-pwa` for service worker registration, `next-intl` for Arabic/English i18n, RTL layout via `dir="rtl"` on the root `<html>` element, and Tailwind CSS with custom design tokens (Wateen Blue `#0066FF`, Trust Green `#00C853`).
- **Task 2:** Build the `ServiceGrid` page — displays available service types as visually rich cards (icon, name in Arabic, starting price, estimated duration). Cards use glassmorphism styling with `backdrop-filter: blur(16px)` and subtle hover animations via `framer-motion`. Tapping a card navigates to the booking flow.
- **Task 3:** Build the `BookingFlow` — multi-step form: Step 1 (Select Service, choose urgency), Step 2 (Confirm Location via `<PatientLocationPicker>`), Step 3 (Review Price Estimate + Notes textarea), Step 4 (Payment via Stripe Elements). Use `framer-motion` `AnimatePresence` for smooth step transitions.
- **Task 4:** Implement the `ActiveVisit` tracking page — real-time view showing: visit status badge, assigned nurse profile card (photo, name, agency), live map with nurse location marker (updated via WebSocket), ETA countdown, and action buttons (Cancel, SOS). Status transitions trigger subtle haptic-like animations.

---

### Ticket P7-T2: Patient PWA — Rating, History & Profile

**Context:** After visit completion, patients must rate their experience. They also need access to visit history and profile management for a complete self-service experience.

- **Task 1:** Build the `RatingModal` component — appears after `Visit.COMPLETED`. Star rating (1-5) for the overall experience, optional text review, and a "Report Issue" link. Submits to `POST /api/v1/visits/{id}/rate/`. The rating updates the Agency's aggregate `rating` field (rolling average of last 100 ratings).
- **Task 2:** Build the `VisitHistory` page — paginated list of past visits with: date, service type, assigned agency name, nurse name, final price, and rating given. Each row is expandable to show full visit timeline (status transitions with timestamps). Filter by date range and service type.
- **Task 3:** Build the `PatientProfile` page — edit: name, phone, email, saved addresses (home, work), medical notes (allergies, chronic conditions — encrypted at rest), and notification preferences. Include "Delete My Account" flow compliant with data privacy regulations.
- **Task 4:** Implement offline-first patterns using `IndexedDB` via `idb` library — cache service types, recent visit history, and user profile for offline viewing. Queue visit rating submissions when offline and sync when connectivity returns (using Background Sync API).

---

### Ticket P7-T3: Nurse PWA — Dispatch Offers & Active Visit Management

**Context:** The Nurse PWA is the operational tool for field nurses. It must handle dispatch offer notifications, navigation to patients, and in-visit protocol documentation — all optimized for one-handed mobile use.

- **Task 1:** Build the `DispatchOfferCard` component — full-screen overlay when a new offer arrives (via WebSocket or push notification). Shows: service type, patient district (not exact address until accepted), urgency badge, estimated distance/ETA, and estimated earnings. Two large buttons: "Accept" (green, full-width) and "Decline" (smaller, text-only). 60-second auto-expire countdown ring.
- **Task 2:** Build the `ActiveVisitDashboard` for nurses — post-acceptance view showing: patient details (name, address — revealed only after acceptance), navigation button (opens OSRM route in system maps app or embedded map), visit protocol checklist (step-by-step tasks to complete), and status transition buttons (En Route → Arrived → In Progress → Completed).
- **Task 3:** Implement the visit protocol checklist — configurable per `ServiceType`. Each step has: description (Arabic), required evidence type (photo/text/vitals reading), and completion status. Nurse must complete all steps before the "Complete Visit" button becomes active. Evidence is uploaded to S3 and linked to the visit record.
- **Task 4:** Build the nurse availability toggle — prominent toggle on the home screen that sets `NurseProfile.is_available`. When toggled ON, the nurse's GPS location begins streaming to the backend (every 30s). When OFF, location tracking stops. Show daily stats: completed visits, total earnings, hours active.

---

### Ticket P7-T4: PWA Infrastructure — Offline, Caching & Install

**Context:** Both PWAs must function as installable applications with offline capabilities, meeting the PWA Lighthouse audit threshold of 90+ for Progressive Web App score.

- **Task 1:** Configure the service worker strategy — `NetworkFirst` for API calls (fall back to cached responses), `CacheFirst` for static assets (CSS, JS, images), `StaleWhileRevalidate` for map tiles. Set up background sync for queued actions (ratings, protocol uploads).
- **Task 2:** Create the PWA manifest (`manifest.json`) for both apps — configure: `name`, `short_name` (Arabic), `start_url`, `display: standalone`, `theme_color: #0066FF`, `background_color: #0A0A1A` (dark mode), icons (192x192 and 512x512 in PNG), and `screenshots` for the install prompt. Test install flow on Chrome Android and Safari iOS.
- **Task 3:** Implement responsive design breakpoints — Mobile (320-480px, primary), Tablet (481-768px), Desktop (769px+). Use CSS logical properties exclusively (`margin-inline-start` not `margin-left`) for seamless RTL support. Test with Arabic long-form text to ensure no overflow or truncation.
- **Task 4:** Run Lighthouse audits for both PWAs — target scores: Performance ≥ 85, Accessibility ≥ 95, Best Practices ≥ 90, SEO ≥ 90, PWA ≥ 90. Address any flagged issues: missing meta tags, improper heading hierarchy, contrast ratio failures, or missing ARIA labels.

---

### Ticket P7-T5: Professional QA, Security & Validation

**Context:** PWAs are patient-facing — UI bugs, accessibility failures, or security issues directly impact trust and usability. Testing must cover cross-browser compatibility, RTL edge cases, and offline resilience.

- **Task 1:** Write Playwright E2E tests for the Patient PWA: complete booking flow (select service → pick location → confirm price → mock payment → verify `PENDING_AGENCY` status). Test in both Arabic and English locales. Verify all text renders correctly in RTL mode.
- **Task 2:** Write Playwright E2E tests for the Nurse PWA: receive dispatch offer (via mock WebSocket) → accept → navigate to active visit → complete protocol steps → mark visit complete → verify status transition.
- **Task 3:** Cross-browser testing — verify both PWAs render correctly on: Chrome (Android), Safari (iOS 16+), Firefox, and Samsung Internet. Test the install prompt, offline mode (disconnect network mid-session), and background sync (queue a rating while offline, reconnect, verify sync).
- **Task 4:** Accessibility audit using `axe-core` — verify: all interactive elements have accessible names, focus order is logical in RTL, color contrast meets WCAG 2.1 AA standard, screen reader announces status changes (visit updates use `aria-live="polite"` regions), and all form inputs have associated labels.

---

## Phase 8: Blackbox System & Incident Dispute Logs

**Objective:** Implement the encrypted Blackbox logging system for high-risk visit scenarios, the SOS emergency protocol, and the structured dispute resolution framework — providing legal protection for patients, nurses, and agencies.

---

### Ticket P8-T1: Blackbox Encrypted Logging Infrastructure

**Context:** The Blackbox is a tamper-proof logging system that activates during high-risk clinical scenarios or emergencies. All data is AES-256 encrypted and stored in compliance with Egyptian data protection laws.

- **Task 1:** Create the `blackbox` Django app with `BlackboxSession` model: `visit` (FK), `triggered_by` (FK to User), `trigger_type` (enum: SOS/CLINICAL_STAGE/MANUAL), `started_at`, `ended_at`, `encryption_key_ref` (reference to the key used, never the key itself), `status` (RECORDING/SEALED/ACCESSED).
- **Task 2:** Implement AES-256 encryption service in `blackbox/services/encryption_service.py` — `encrypt_data(plaintext, key_ref)` and `decrypt_data(ciphertext, key_ref)`. Keys are derived from a two-part scheme: Agency-specific salt + Platform Master Key. Keys are stored in environment variables or a secrets manager, never in the database.
- **Task 3:** Create `BlackboxEntry` model for individual log entries within a session: `session` (FK), `entry_type` (enum: GPS_PING/AUDIO_CHUNK/METADATA/PHOTO), `encrypted_payload` (BinaryField), `timestamp`, `sequence_number` (for ordering). Implement bulk insert optimization for high-frequency GPS pings (every 5 seconds during SOS).
- **Task 4:** Build the Blackbox API: `POST /api/v1/blackbox/start/` (creates session, returns session_id), `POST /api/v1/blackbox/log/` (appends encrypted entry), `POST /api/v1/blackbox/seal/` (closes session, makes it immutable). All endpoints require active visit context and authenticated user.

---

### Ticket P8-T2: SOS Emergency Protocol

**Context:** The SOS/Panic button is a critical safety feature. When triggered by a patient or nurse, the system must immediately notify all relevant parties, activate the Blackbox, and provide emergency assistance coordinates.

- **Task 1:** Create `POST /api/v1/sos/trigger/` endpoint — accepts `visit_id` and optional `description`. Action chain: (1) Create BlackboxSession with `trigger_type=SOS`, (2) Push notification to Agency Admin + Wateen Compliance Team, (3) Set visit `urgency=CRITICAL`, (4) Begin high-frequency GPS logging (every 5 seconds).
- **Task 2:** Implement emergency location service — when SOS triggers, query the nearest hospitals, police stations, and pharmacies using Nominatim reverse geocoding + OSM Overpass API. Return the top 3 nearest of each type with names, addresses, phone numbers, and walking distance.
- **Task 3:** Build the SOS UI for both PWAs — large, accessible "SOS" button (red, pulsing animation, min 60px tap target). On press: 3-second confirmation countdown (prevent accidental triggers), then full-screen emergency mode showing: "Help is notified" message, emergency contacts, nearest facilities map, and "Call Emergency" direct-dial button.
- **Task 4:** Create the SOS dashboard view for Wateen Compliance Team — real-time feed of active SOS events. Each entry shows: visit details, triggering party, GPS coordinates (live-updating map), elapsed time since trigger, and action buttons: "Contact Nurse", "Contact Patient", "Dispatch Security", "Resolve Incident".

---

### Ticket P8-T3: Visit Protocol & Clinical Documentation

**Context:** Every visit must follow a standardized clinical protocol with mandatory documentation steps. This protects against malpractice claims and ensures care quality across all agencies on the platform.

- **Task 1:** Create `ClinicalProtocol` model: `service_type` (FK), `version`, `steps` (JSONField containing ordered list of: `step_name`, `step_name_ar`, `description`, `required_evidence_type` (PHOTO/TEXT/VITALS/SIGNATURE), `is_mandatory`). Seed protocols for the initial 5 service types aligned with MoH standards.
- **Task 2:** Create `ProtocolExecution` model: `visit` (FK), `protocol` (FK), `started_at`, `completed_at`, `status` (IN_PROGRESS/COMPLETED/INCOMPLETE). And `ProtocolStepExecution`: `execution` (FK), `step_index`, `evidence_type`, `evidence_file` (FileField, encrypted), `evidence_text` (TextField, encrypted), `completed_at`, `completed_by` (FK to Nurse).
- **Task 3:** Implement protocol enforcement — the visit cannot transition to `COMPLETED` unless all mandatory protocol steps have evidence submitted. The `transition_to('COMPLETED')` method checks `ProtocolExecution.status == COMPLETED`. If incomplete, return `400` with a list of missing steps.
- **Task 4:** Build protocol review UI for Agency Admins — view completed visit protocols with all evidence (photos, vitals, notes). Flag visits with protocol deviations (steps completed out of order, missing optional evidence). Export protocol records as PDF for MoH audit submissions.

---

### Ticket P8-T4: Dispute Resolution Framework

**Context:** Disputes between patients, nurses, and agencies must follow a structured resolution process. The framework uses visit data, protocol records, and Blackbox logs to facilitate fair resolution.

- **Task 1:** Create `Dispute` model: `visit` (FK), `opened_by` (FK to User), `respondent` (FK to User), `category` (enum: QUALITY/PUNCTUALITY/BILLING/SAFETY/OTHER), `description`, `status` (OPEN/UNDER_REVIEW/RESOLVED/ESCALATED), `resolution` (TextField), `resolved_by` (FK), `opened_at`, `resolved_at`.
- **Task 2:** Implement dispute API: `POST /api/v1/disputes/` (open dispute, attach to visit), `GET /api/v1/disputes/{id}/` (view dispute with timeline), `PATCH /api/v1/disputes/{id}/respond/` (add response message), `PATCH /api/v1/disputes/{id}/resolve/` (Agency Admin or SuperAdmin resolves). Each action appends to a `DisputeTimeline` audit log.
- **Task 3:** Build dispute evidence aggregation — when a dispute is opened, the system automatically compiles: visit status history, protocol execution record, patient/nurse ratings, GPS trace (was nurse late?), payment/refund status, and Blackbox session summary (if any). This is presented as a "Case File" to the reviewer.
- **Task 4:** Implement three-tier resolution hierarchy: (1) **Agency Level** — Agency Admin reviews and resolves minor disputes (punctuality, quality). (2) **Platform Level** — Wateen SuperAdmin handles escalated disputes or disputes involving billing. (3) **Arbitration** — for disputes involving safety or legal claims, Blackbox data is unlocked for review by authorized Compliance Officers only.

---

### Ticket P8-T5: Professional QA, Security & Validation

**Context:** The Blackbox and dispute system handle the most sensitive data on the platform. Encryption must be verified, access controls must be airtight, and data integrity must be tamper-proof.

- **Task 1:** Write Pytest tests for the encryption service: encrypt → decrypt roundtrip produces identical plaintext, different key refs produce different ciphertexts, corrupted ciphertext raises `DecryptionError`, and key derivation is deterministic (same inputs produce same key).
- **Task 2:** Write access control tests: verify only the triggering user and Compliance Officers can access Blackbox sessions, Agency Admins cannot access Blackbox data from other agencies, sealed sessions cannot be modified (append or delete), and Blackbox entries maintain correct chronological ordering.
- **Task 3:** Write dispute resolution tests: verify the full lifecycle (open → respond → escalate → resolve), ensure resolution notes are immutable after resolution, verify that reopening a dispute creates a new linked dispute (not modifies the old one), and test edge case where both parties open disputes for the same visit.
- **Task 4:** Penetration testing for data security: attempt SQL injection on encrypted fields, verify that Blackbox payloads are not exposed in server logs or error responses, test that pre-signed URLs for evidence files expire correctly, and verify that deleted user accounts do not cascade-delete Blackbox data (retained for legal compliance).

---

## Phase 9: AI Copilot Integration & CI/CD Deployment

**Objective:** Integrate the AI Copilot for clinical decision support and care standardization across agencies, and establish a production-grade CI/CD pipeline with automated testing, Blue-Green deployment, and comprehensive monitoring.

---

### Ticket P9-T1: AI Copilot — Clinical Decision Support

**Context:** The AI Copilot acts as an operational equalizer across agencies with varying nurse calibers. It provides real-time guidance on MoH-standard clinical protocols, dosage verification, and contraindication alerts.

- **Task 1:** Create the `ai_copilot` Django app. Implement `ClinicalKnowledgeBase` — a structured JSON/JSONB store of MoH-approved clinical guidelines for the 50+ common home nursing procedures. Each entry includes: procedure name, required qualifications, step-by-step protocol, contraindications, and emergency escalation criteria.
- **Task 2:** Build the copilot query API: `POST /api/v1/copilot/assist/` — accepts `procedure_id`, `patient_context` (age, weight, allergies, current medications). Returns: recommended protocol steps, dosage calculations (adjusted for patient parameters), contraindication warnings (flagged in red), and relevant MoH reference citations.
- **Task 3:** Implement real-time copilot integration in the Nurse PWA — during active visits, each protocol step shows a "Copilot Assist" button. Tapping it queries the copilot API with the current step context and displays guidance in a slide-up panel. Critical warnings (contraindications) are auto-surfaced without nurse initiation.
- **Task 4:** Build the copilot analytics dashboard for SuperAdmin — track: most-queried procedures, contraindication alert frequency by agency, copilot usage rate per nurse, and "overridden warnings" count (nurses who proceeded despite a warning — flagged for quality review).

---

### Ticket P9-T2: AI Copilot — Demand Prediction & Surge Pricing

**Context:** The AI Copilot's second function is demand prediction — forecasting high-demand periods and geographic hotspots to enable proactive nurse positioning and dynamic surge pricing.

- **Task 1:** Implement `DemandPredictionService` in `ai_copilot/services/demand_service.py` — analyze historical visit data (time-of-day, day-of-week, district, service type) to predict demand for the next 24 hours. Output: demand heatmap (GeoHash-level) with confidence scores.
- **Task 2:** Connect demand prediction to the surge pricing coefficient (`Phi_surge` in the Cognitive Pricing Engine formula). When predicted demand exceeds supply in a GeoHash cell, `Phi_surge` increases (capped at 3.0x). When supply exceeds demand, `Phi_surge` drops to 1.0x (no surge). Update the coefficient every 15 minutes via Celery periodic task.
- **Task 3:** Build the demand heatmap visualization for Agency Admins — overlay on the coverage polygon map showing predicted demand intensity by color (green → yellow → red). Agencies can use this to proactively position nurses in high-demand areas.
- **Task 4:** Implement "Smart Nudge" notifications for agencies — when predicted demand spikes in their coverage area, send a push notification: "High demand expected in {district} between {time_range}. Consider having {N} additional nurses online." Track nudge effectiveness (did the agency increase capacity?).

---

### Ticket P9-T3: CI/CD Pipeline — Automated Build & Test

**Context:** A robust CI/CD pipeline ensures that every code change is automatically tested, built, and deployable. This is critical for the Solo Dev + AI execution model where manual QA bandwidth is limited.

- **Task 1:** Configure GitHub Actions workflow (`.github/workflows/ci.yml`) with stages: (1) **Lint** — `ruff check .` + `eslint` for frontend, (2) **Unit Tests** — `pytest --cov` with PostGIS-enabled Docker service container, (3) **Frontend Tests** — `jest` + React Testing Library, (4) **Build** — Docker multi-stage build for Django and Next.js.
- **Task 2:** Implement test coverage enforcement — configure `pytest-cov` with minimum threshold of 80% for backend, `jest --coverage` with 75% threshold for frontend. CI fails if coverage drops below thresholds. Add coverage badges to `README.md`.
- **Task 3:** Configure Docker image build and push — on merge to `main`, build production Docker images for `wateen-api` (Django + Gunicorn + Uvicorn) and `wateen-web` (Next.js standalone), tag with git SHA, and push to container registry (Docker Hub or GitHub Container Registry).
- **Task 4:** Add pre-commit hooks using `pre-commit` framework — enforce: code formatting (`ruff format`), import sorting (`isort`), type checking (`mypy --strict` on critical modules), and commit message format (conventional commits for changelog generation).

---

### Ticket P9-T4: Deployment & Monitoring Infrastructure

**Context:** Production deployment must be zero-downtime using Blue-Green strategy. Monitoring must provide real-time visibility into application health, performance bottlenecks, and error rates.

- **Task 1:** Configure Blue-Green deployment — maintain two identical production environments (`blue` and `green`). New releases deploy to the inactive environment, run smoke tests (health check endpoint + basic API flow), and then switch the Nginx upstream to the new environment. Automatic rollback if smoke tests fail.
- **Task 2:** Integrate Sentry for error tracking — configure Django Sentry SDK with: automatic breadcrumb collection, PII scrubbing (strip patient names, phone numbers from error reports), performance tracing (sample rate 20%), and release tracking (tagged with git SHA). Set up alert rules: Slack notification for P0 errors (500 response rate > 1% in 5 minutes).
- **Task 3:** Set up OpenTelemetry for application performance monitoring — instrument: Django request latency (p50, p95, p99), PostGIS query execution time, Redis operation latency, Celery task duration, and WebSocket connection count. Export metrics to a Grafana dashboard with pre-configured panels for each metric.
- **Task 4:** Configure automated health checks and alerting — create `/api/v1/health/` endpoint that checks: database connectivity, Redis connectivity, Celery worker responsiveness, PostGIS extension status, and Stripe API reachability. Set up uptime monitoring (e.g., UptimeRobot or Blackbox Exporter) with 1-minute intervals and PagerDuty/Slack escalation for downtime.

---

### Ticket P9-T5: Professional QA, Security & Validation

**Context:** The final phase validates the entire system end-to-end, from infrastructure to application logic. This is the comprehensive "launch readiness" validation.

- **Task 1:** Full E2E integration test — simulate the complete Wateen lifecycle: (1) Agency registers and completes KYC, (2) Agency draws coverage polygon, (3) Agency invites and onboards nurse, (4) Patient creates visit request, (5) System dispatches to agency, (6) Nurse accepts and completes visit with protocol, (7) Payment settles to agency wallet, (8) Patient rates agency. All via API calls in a single Pytest session against a staging environment.
- **Task 2:** Security penetration test — run OWASP ZAP automated scan against all API endpoints. Manually test: JWT token replay attacks, IDOR (Insecure Direct Object Reference) on visit/agency endpoints, CSRF on state-changing operations, rate limiting effectiveness (brute-force login), and file upload vulnerability (SVG with embedded JavaScript).
- **Task 3:** Load and stress testing — use Locust to simulate production-scale traffic: 10,000 concurrent patients, 500 agencies, 2,500 nurses. Measure: API response time distribution, WebSocket connection stability under load, Celery queue depth growth, PostgreSQL connection pool utilization, and Redis memory usage. Identify and document the breaking point.
- **Task 4:** Disaster recovery validation — test: database backup and restore procedure (verify data integrity post-restore), Redis failover (switch to replica, verify no data loss), application container restart (verify session persistence), and SSL certificate renewal process. Document all procedures in a runbook stored in `docs/RUNBOOK.md`.

---

## Summary Statistics

| Metric                        | Count                          |
| :---------------------------- | :----------------------------- |
| **Total Phases**              | 9                              |
| **Total Tickets**             | 45                             |
| **Total Tasks**               | ~175                           |
| **QA Tickets**                | 9 (one per phase)              |
| **Estimated Sprint Coverage** | 18-27 Sprints (2-week cadence) |

---

**Prepared By:** Wateen Engineering (AI-Assisted Agile Planning)  
**Date:** February 2026  
**Status:** APPROVED — Ready for Sprint Planning  
**© 2026 Wateen Healthcare Technologies.**
