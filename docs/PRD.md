# 🏥 Wateen (وَتِين) — Master Product Requirements Document (PRD) v5.0

## Edition: B2B2C Healthcare Aggregator (SaaS + Marketplace)

> **Primary Domain:** wateen.live  
> **Version:** 5.0 (Cumulative Master)  
> **Date:** February 2026  
> **Status:** APPROVED / IN-DEVELOPMENT  
> **Execution Model:** Hyper-Pair Programming (Solo Dev + AI

---

## 🏗️ 1. EXECUTIVE SUMMARY & STRATEGIC VISION

### 1.1 Document Purpose

This document serves as the comprehensive "Source of Truth" for the Wateen platform. It outlines the architectural shift from a P2P (Peer-to-Peer) model to a B2B2C (Business-to-Business-to-Consumer) Aggregator model, designed for maximum scalability, legal compliance with Egyptian Ministry of Health (MoH) regulations, and technical excellence.

### 1.2 The Wateen Vision

To become the "Nerve System" (the literal meaning of _Wateen_) of home-based healthcare in the MENA region. By empowering Licensed Nursing Agencies with enterprise-grade SaaS tools and connecting them to a high-trust consumer marketplace, Wateen aims to standardize home care quality.

### 1.3 Problem Statement

The current home care market in Egypt is fragmented:

- **For Patients:** High risk of unverified freelancers, inconsistent pricing, and lack of medical accountability.
- **For Agencies:** Lack of digital visibility, manual dispatching inefficiencies, and complex financial settlements.
- **For Regulators (MoH):** Difficulty in monitoring clinical standards and ensuring liability coverage.

### 1.4 The Solution (B2B2C Pivot)

Wateen solves these by acting as a **Licensed Aggregator**. We do not hire nurses; we onboard **Agencies**.

1.  **Agencies** gain a SaaS dashboard to manage their fleet, geography, and earnings.
2.  **Patients** request through Wateen, receiving guaranteed care from professional entities.
3.  **Wateen** manages the "Trust Layer" (Escrow, Routing, Ratings, AI Governance).

---

## 🗺️ 2. TARGET MARKET & USER PERSONAS

### 2.1 Geographic Focus

- **Primary Tier:** Greater Cairo, Alexandria, Giza.
- **Secondary Tier:** Delta Region, Suez Canal Zone.
- **RTL Optimization:** The entire platform is built with Arabic-First UX, ensuring seamless RTL (Right-to-Left) interaction.

### 2.2 Persona 1: The Wateen SuperAdmin (Platform Operator)

- **Goals:** Maintain ecosystem health, verify agency document integrity, resolve high-level disputes.
- **Pain Points:** Regulatory overhead, manually reviewing thousands of PDF licenses.
- **Technical Entry Point:** SuperAdmin Dashboard (Django Admin + Custom React Views).

### 2.3 Persona 2: The Agency Manager (B2B Customer)

- **Goals:** Optimize nurse utilization, expand coverage, maximize revenue per shift.
- **Pain Points:** "Uber-style" competition from freelancers, manual scheduling errors.
- **Technical Entry Point:** B2B Agency Dashboard (React/Next.js).

### 2.4 Persona 3: The Licensed Nurse (Service Provider)

- **Goals:** Reliable income, clear work instructions, safe environment.
- **Pain Points:** Travel distance, payment delays, safety during night shifts.
- **Technical Entry Point:** Nurse PWA / Mobile App.

### 2.5 Persona 4: The Patient/Family Member (B2C Customer)

- **Goals:** Immediate relief, verified professional, transparent pricing.
- **Pain Points:** Searching social media for nurse numbers, hidden fees.
- **Technical Entry Point:** Patient PWA / Consumer Portal.

---

## ⛓️ 3. CORE ARCHITECTURE & DATA MODELS

### 3.1 Technological Pillar

- **Frameworks:** Django 5 (Backend), Next.js 14 (Frontend).
- **Protocol:** Geo-Distributed Modular Monolith.
- **Real-time Engine:** Django Channels + Redis Pub/Sub.
- **Spatial Engine:** PostGIS (Geometry logic for coverage polygons).

### 3.2 The Primary Entities (Database Schema)

#### `AgencyProfile`

The core business entity.

- **Fields:** `manager_name`, `commercial_registry`, `moh_license`, `tax_id`.
- **Spatial:** `coverage_polygon` (GIST indexed).
- **Financials:** `wallet_balance`, `stripe_account_id`.

#### `Visit`

The transaction unit of value.

- **States:** `PENDING_AGENCY` -> `PENDING_NURSE` -> `ACCEPTED` -> `EN_ROUTE` -> `IN_PROGRESS` -> `COMPLETED`.
- **Logic:** Stores immutable snapshot of pricing (base, surge, distance) at the time of request.

#### `Transaction`

The ledger entry.

- **Split:** 15% Platform Take Rate (Wateen), 85% Provider Revenue (Agency).
- **Status:** `ESCROWED` (Funds held), `SETTLED` (Visit finished).

---

---

## 🗺️ 4. GEOSPATIAL & MAPPING INFRASTRUCTURE (OSM PIVOT)

To ensure extreme cost-efficiency and avoid vendor lock-in, Wateen utilizes a strictly open-source geospatial stack based on the **OpenStreetMap (OSM)** ecosystem.

### 4.1 The Technical Stack (OSM Stack)

| Component            | Technology       | Role                                                  |
| :------------------- | :--------------- | :---------------------------------------------------- |
| **Frontend Map**     | `react-leaflet`  | Core map rendering for Patient & Agency dashboards.   |
| **Polygon Drawing**  | `leaflet-geoman` | UI tool for Agencies to define coverage zones.        |
| **Geocoding**        | `Nominatim`      | Converting text addresses to Lat/Long coordinates.    |
| **Routing Engine**   | `OSRM` / `ORS`   | Calculating driving distance, ETA, and routing paths. |
| **Spatial Database** | `PostGIS`        | Backend storage and geometric intersection logic.     |

### 4.2 Architectural Workflow

1.  **Agency Onboarding:** The Agency Admin uses `leaflet-geoman` controls within a `react-leaflet` container to draw the service area. The resulting **GeoJSON** is sent to the Django backend.
2.  **Storage & Indexing:** Django stores the GeoJSON in a PostGIS `PolygonField` with a GIST index for sub-millisecond spatial queries.
3.  **Dispatch Engine:** When a patient requests a visit:
    - **Nominatim** resolves the patient's address to coordinates if GPS is unavailable.
    - **PostGIS** identifies eligible agencies using `ST_Intersects`.
    - **OSRM/ORS** provides the precise driving distance ($D$) and ETA ($E_a$) between assigned nurses and the patient for pricing ($P$) and ranking ($M_a$).

### 4.3 Required Packages

- **Frontend (NPM):** `leaflet`, `react-leaflet`, `@geoman-io/leaflet-geoman-free`
- **Backend (Python):** `geopy` (for Nominatim), `django-geos`, `psycopg2-binary`, `django-rest-framework-gis`

---

## 🚀 5. THE DISPATCH & ROUTING ENGINE (The "Secret Sauce")

### 5.1 Two-Tier Spatial Matching

1.  **Stage 1 (Polygon Check):** System executes `ST_Intersects(patient_location, agency_coverage_polygon)`.
2.  **Stage 2 (Ranking):** Eligible agencies are ranked using a `Score = (W_q * Clinical_Quality) + (W_r * Operational_Reliability) + (W_p * Spatial_Proximity)`. Weights dynamically adjust based on Visit Urgency.

### 5.2 Dispatch Modes

- **Manual Mode:** Agency Admin sees the request and has a 300-second window to drag/drop a nurse onto the file.
- **Auto Mode:** Wateen pings the TOP 5 optimal nurses of that agency. First to swipe claims the task.

### 5.3 Reliability & Timeouts

If an agency fails to respond to a `PENDING_AGENCY` request within the defined threshold, a **Celery Worker** triggers the `re_route_visit` task, moving the request to the next ranked neighbor.

---

## 💰 6. FINTECH & ESCROW PROTOCOL

### 6.1 Stripe Connect Integration

- Using **Destination Charges** to handle multi-party payouts.
- Wateen creates the `PaymentIntent`. Funds are authorized on the patient's card.
- Upon `Visit.COMPLETED`, Wateen captures the payment.
- Split happens instantly via Stripe API, sending the Agency's share to their connected account minus Wateen’s 15%.

### 6.2 Wallet & Withdrawal

Agencies track their "Escrowed Balance" and "Available Balance". Withdrawals are processed twice weekly to the Agency's registered corporate bank account.

---

## 🛡️ 7. THE BLACKBOX & SHIELD SYSTEM (Safety & Protection)

### 7.1 Clinical Integrity

Every visit includes a mandatory **Step-by-Step Protocol** (e.g., "Check ID", "Verify Prescription", "Measure BP"). The visit cannot be closed until a photo/signature/data point is uploaded for each.

### 7.2 The Blackbox (Encrypted Logs)

In high-risk scenarios or upon patient/nurse distress signal, the system begins encrypted audio/meta-logging.

- **Encryption:** AES-256 for storage.
- **Access:** Only accessible by Wateen Compliance Officers in the event of a "Critical Incident Report".

---

## 📈 8. 20-PHASE ROADMAP (E2E EXECUTION)

### Phases 1-5: The Foundation

1.  **B2B Infra:** Docker, Django 5 setup, PostGIS enablement.
2.  **Agency Onboarding:** KYC UI, Document upload, OCR verification.
3.  **Geo-Grid:** OpenStreetMap integration with `react-leaflet` and `leaflet-geoman` for polygon drawing.
4.  **Visit Request v1:** Patient flow + Spatial matching logic.
5.  **Role RBAC:** Nurse/Agency/Admin permission layers.

### Phases 6-10: Intelligence & Flow

6.  **Socket Engine:** Real-time bi-directional status updates.
7.  **Auto-Dispatch:** Uber-style nurse polling within agency bounds.
8.  **Stripe Core:** Financial escrow and take-rate logic.
9.  **AI Estimator:** ML-driven pricing based on historical Egyptian traffic/demand data.
10. **Admin Command Center:** Unified view of the entire Egyptian grid.

### Phases 11-20: Advanced Scale & IoT (Future)

- Wearable integration for real-time vitals monitoring.
- AI Epidemic heatmaps for MoH reporting.
- Fully automated settlement & invoicing.
- Regional expansion (MENA).

---

## 🔧 9. NON-FUNCTIONAL REQUIREMENTS (NFRs)

### 9.1 Performance

- **Concurrency:** Support 10k+ active visits simultaneously.
- **Latency:** API response < 300ms.
- **Map Load:** Smooth interaction for complex polygons with 100+ vertices.

### 8.2 Security

- **Data Residency:** Compliant with Egyptian Data Privacy laws.
- **PII Masking:** Patient phone numbers only visible to the assigned nurse after acceptance.

### 8.3 Aesthetics

- **Vibe:** Dark mode by default, Glassmorphism, Premium high-fidelity UI.
- **i18n:** Full RTL support with Inter and Amiri fonts for Arabic typography.

---

## 👨‍💻 10. EXECUTION RULES (FOR AI AGENTS)

When modifying this repository, adherence to these principles is non-negotiable:

1.  **GIS Perfection:** Always use `ST_DWithin` or `ST_Intersects` for location logic.
2.  **Atomic Transactions:** Financial updates must be wrapped in `transaction.atomic()`.
3.  **No Hallucinations:** Reference `models.py` before creating serializer fields.
4.  **Premium UX:** If creating a UI, it must WOW the user. Use `framer-motion` for micro-interactions.

---

## 🛡️ 11. DETAILED USER STORIES & ACCEPTANCE CRITERIA

### 11.1 US.01: Agency Onboarding (B2B)

**Description:** As an Agency Manager, I want to register my agency on Wateen so that I can provide services through the platform.

- **AC 1.1:** Agency can upload PDF/Image for Commercial Registry and MoH License.
- **AC 1.2:** System flags missing documents before submission.
- **AC 1.3:** Agency enters "Management Profile" (Name, Phone, Email).
- **AC 1.4:** Verification status is shown as "Pending Review" until SuperAdmin approves.

### 11.2 US.02: Coverage Polygon Definition

**Description:** As an Agency Manager, I want to draw my coverage area on a map so that I only receive relevant local requests.

- **AC 2.1:** User can draw a polygon using `leaflet-geoman` integrated into the Agency Dashboard.
- **AC 2.2:** System validates that the polygon is closed and valid.
- **AC 2.3:** Agency can update coverage area (updates trigger re-indexing in PostGIS).

### 11.3 US.03: Patient Service Request (B2C)

**Description:** As a Patient, I want to select a service and provide my location so I can see which agencies can help me.

- **AC 3.1:** Patient selects from a grid of services (e.g., General Nursing, Wound Care).
- **AC 3.2:** Patient's GPS coordinates are captured (with RTL-optimized map picker).
- **AC 3.3:** Price estimate is shown before "Confirm Request".

### 11.4 US.04: Two-Tier Dispatching (Manual/Auto)

**Description:** As an Agency Admin, I want to choose how to assign my nurses to incoming requests.

- **AC 4.1:** Admin can toggle "Auto-Dispatch" (Uber style) vs "Manual Dispatch" (Manager assigns).
- **AC 4.2:** In Manual Mode, a "Visit Queue" shows pending requests with a countdown timer (300s).
- **AC 4.3:** If timer hits zero, the visit is automatically re-routed to the next Agency.

### 11.5 US.05: Financial Settlement (Stripe)

**Description:** As an Agency Manager, I want my share of visit fees to be deposited in my wallet automatically.

- **AC 5.1:** Upon `Visit.COMPLETED`, the transaction moves from `Escrowed` to `Settled`.
- **AC 5.2:** Wateen's 15% is deducted from the total before it hits the Agency's balance.
- **AC 5.3:** Agency can see a "Financial Statement" with a breakdown of daily earnings.

---

## 📡 12. API DESIGN SPECIFICATIONS (SYSTEM BLUEPRINT)

### 12.1 Authentication Module (`/api/v1/auth/`)

- `POST /register/`: Multi-step registration for Patient/Agency.
- `POST /login/`: JWT-based login (Access + Refresh tokens).
- `GET /me/`: Returns profile data based on role claims.

### 12.2 Agency Module (`/api/v1/agencies/`)

- `POST /coverage/`: Update PostGIS `coverage_polygon`.
- `GET /nurses/`: List nurses associated with the calling agency.
- `POST /dispatch/manual/`: Endpoint for agency admins to assign a specific nurse ID to a visit ID.

### 12.3 Visit Module (`/api/v1/visits/`)

- `POST /request/`: Initiation point for patient requests.
- `GET /active/`: Real-time view of current active visits for that user/agency.
- `PATCH /status/`: Transition endpoint (restricted by `ALLOWED_TRANSITIONS` state machine).

### 12.4 Financials Module (`/api/v1/payments/`)

- `POST /intent/`: Initialize Stripe PaymentIntent.
- `GET /balance/`: View internal wallet balance and transaction history.

---

## 🗄️ 13. DATA DICTIONARY (DETAILED SCHEMA)

### 13.1 `users_agency_profile` Table

| Field Name         | Type     | Description                        | Constraints      |
| :----------------- | :------- | :--------------------------------- | :--------------- |
| `id`               | UUID     | Primary Key                        | Required         |
| `manager_name`     | String   | Name of the primary agency manager | Required         |
| `commercial_reg`   | String   | Legal business ID                  | Unique           |
| `coverage_polygon` | Geometry | PostGIS Polygon of service area    | GIST Index       |
| `wallet_balance`   | Decimal  | Current settled revenue            | Default: 0.00    |
| `status`           | Enum     | [PENDING, VERIFIED, SUSPENDED]     | Default: PENDING |

### 13.2 `visits_visit` Table

| Field Name    | Type    | Description                           | Constraints               |
| :------------ | :------ | :------------------------------------ | :------------------------ |
| `id`          | UUID    | Primary Key                           | Required                  |
| `patient_id`  | FK      | Link to PatientProfile                | Required                  |
| `agency_id`   | FK      | Link to AgencyProfile                 | Required                  |
| `nurse_id`    | FK      | Link to NurseProfile                  | Nullable (until assigned) |
| `status`      | Enum    | [PENDING_AGENCY, PENDING_NURSE, etc.] | Indexed                   |
| `final_price` | Decimal | Total cost to patient                 | Required                  |

---

## 🛡️ 14. SAFETY, CRISIS & DISPUTE PROTOCOLS (THE "SHIELD")

### 14.1 Critical Incident Workflow

In the event of a medical emergency or physical threat:

1.  **Panic Trigger:** Nurse or Patient presses the SOS button in the app.
2.  **Notification:** Immediate push notification to Agency Admin and Wateen Compliance Team.
3.  **Data Capture:** Blackbox starts high-fidelity logging (audio + GPS high-freq ping).
4.  **Assistance:** System presents nearest Hospital/Police station coordinates and provides "Direct Line" button.

### 14.2 Dispute Resolution Framework

- **Minor Disputes (e.g., punctuality):** Handled via Agency Rating system.
- **Major Disputes (e.g., clinical error):** Agency Admin investigates using the Visit Log.
- **Arbitration:** Wateen SuperAdmin acts as final arbitrator, reviewing Blackbox data if necessary.

---

## 📜 15. COMPLIANCE & REGULATORY MATRIX (EGYPT MOH)

### 15.1 Legal Entities

All agencies must be verified against the Egyptian General Authority for Investment (GAFI) registry.

- **Requirement:** Valid Commercial Registry (Sijil Tijari).
- **Requirement:** MoH Operational License for Home Care.

### 15.2 Clinical Standards

- **Protocols:** AI Copilot enforces MoH standard of care for 50+ common home nursing procedures.
- **Consent:** Digital Patient Consent (Iqrar) is mandatory before any invasive procedure (e.g., IV insertion).

---

## 🧪 16. QUALITY ASSURANCE & TESTING STRATEGY

### 16.1 Backend Testing (Pytest)

- **Unit Tests:** Coverage for pricing calculation algorithms.
- **Integration Tests:** End-to-end flow of Visit creation to Stripe settlement.
- **Contract Tests:** Verification of Stripe Webhook handlers.

### 16.2 Frontend Testing (Jest / RTL)

- **Component Tests:** Ensuring RTL layout does not break significantly on small screens.
- **Interaction Tests:** Tracking accuracy of the `leaflet-geoman` polygon drawing tool and GeoJSON export.

### 16.3 Performance & Stress Testing

- **Locust:** Simulating 5000 concurrent WebSocket connections to ensure Redis scalability.
- **Geo-Fencing Stress:** Testing `ST_Intersects` efficiency with 10,000+ complex overlaps.

---

## 🎨 17. UI/UX DESIGN SYSTEM (THE "VISUAL PROTOCOL")

### 17.1 Design Principles

- **Trust First:** Use clean typography (Inter/Amiri) and a harmonious color palette (Primary: #0066FF, Accent: #FFB300).
- **Accessibility:** WCAG 2.1 compliance for healthcare inclusivity.
- **Clarity:** Information-dense dashboards for Agencies, but simple, big-button PWAs for Patients and Nurses.

### 17.2 Atomic Components

1.  **Atoms:** Buttons, Inputs, Avatars, Status Badges (Online/Offline).
2.  **Molecules:** Detail Cards (Nurse snippet, Visit summary), Search Bars.
3.  **Organisms:** Live Tracking Map, Financial Ledger Table, Interactive Coverage Editor.
4.  **Templates:** Dashboard Layout (Sidebar + Header + Content), Mobile PWA Shell.

---

## 🏗️ 18. INFRASTRUCTURE & CI/CD PIPELINE

### 18.1 Environment Strategy

- **Local:** Docker Desktop + Dev Containers for a unified developer experience.
- **Staging:** Identical to production, used for final E2E manual verification and performance benchmarks.
- **Production:** Auto-scaling cluster (e.g., DigitalOcean Kubernetes or AWS EKS).

### 18.2 Deployment Protocol

1.  **Build:** Dockerize Next.js (SSR optimized) and Django.
2.  **Test:** Automated Pytest/Jest execution.
3.  **Deploy:** Blue-Green deployment to ensure zero downtime for active visits.
4.  **Monitor:** OpenTelemetry (Sentry/Datadog) for real-time error tracking and performance bottlenecks.

---

## 🧮 20. PRICING ENGINE & ALGORITHMIC MATCHING

### 20.1 The Price Equation (Cognitive Pricing Engine)

The Wateen Cognitive Pricing Engine implements the following MoH-compliant formula to calculate the final price ($P_{final}$):

$$P_{final} = [ (B \times M_{time} \times M_{urgency}) + (D_{osrm} \times R_{zone} \times (1 + E_{traffic})) ] \times \Phi_{surge} + (B \times \Gamma \times (\frac{R_a}{5.0}))$$

Where:

- $B$: Base Price of the service (`service_type.base_price`).
- $M_{time}$: Time Multiplier (1.2 for night hours 22:00 - 06:00 Cairo Time / holidays, else 1.0).
- $M_{urgency}$: Urgency Multiplier (1.0 for low, 1.2 for high, 1.5 for SOS/critical).
- $D_{osrm}$: Routing distance in km via internal OSRM/ORS wrapper.
- $R_{zone}$: Zone base rate (fallback 5.00 EGP).
- $E_{traffic}$: Traffic extreme penalty (0.1 if traffic delays are high, else 0.0).
- $\Phi_{surge}$: Dynamic surge multiplier fetched via `DemandPredictionService` (max 3.0).
- $\Gamma$: Premium quality cap (10% max tier premium).
- $R_a$: Agency rating (1.0 to 5.0).

> **Architectural Note:** All financial calculations strictly use `decimal.Decimal` and `ROUND_HALF_UP` to prevent floating-point loss.

### 20.2 The "Uber-Style" Matching Score ($M$)

For any given visit $V$, agencies in the coverage zone are scored:
$$M_a = (R_a \cdot 0.5) + (\frac{1}{E_a} \cdot 0.3) + (C_a \cdot 0.2)$$

Where:

- $R_a$: Agency Rating (1-5).
- $E_a$: Estimated Time of Arrival (ETA).
- $C_a$: Normalized Agency Capacity (% of online nurses available).

---

## 📡 21. EXHAUSTIVE API DOCUMENTATION (MOCKED)

### 21.1 POST `/api/v1/visits/request/`

- **Purpose:** Initiate a visit request.
- **Request Body (JSON):**
  ```json
  {
    "service_type_id": "uuid-v4",
    "latitude": 30.0444,
    "longitude": 31.2357,
    "urgency": "high",
    "notes": "Patient requires IV drip change."
  }
  ```
- **Success Response (201 Created):**
  ```json
  {
    "visit_id": "uuid-v4",
    "status": "PENDING_AGENCY",
    "assigned_agency": {
      "id": "uuid-v4",
      "name": "Cairo Care Nursing",
      "eta_minutes": 15
    },
    "estimated_price": 350.0
  }
  ```

### 21.2 PATCH `/api/v1/agency/{id}/dispatch/manual/`

- **Purpose:** Manually assign a nurse to a visit.
- **Request Body (JSON):**
  ```json
  {
    "visit_id": "uuid-v4",
    "nurse_id": "uuid-v4"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "status": "PENDING_NURSE",
    "detail": "Nurse has been notified."
  }
  ```

---

## 🛠️ 22. MAINTENANCE, OPERATIONS & SUPPORT (SOPS)

### 22.1 Technical Maintenance

- **Database Cleanup:** Weekly pruning of expired Redis keys and old Celery task logs.
- **Security Audits:** Monthly vulnerability scans of all Docker images.
- **Optimization:** Quarterly review of PostGIS query performance and GIST index efficiency.

### 22.2 Operational Support

1.  **Level 1 Support:** Handling common user queries (e.g., "Where is my nurse?").
2.  **Level 2 Support:** Investigating technical bugs or payment failures.
3.  **Crisis Level:** High-priority incidents involving medical or safety disputes.

---

## ⚠️ 23. RISK & MITIGATION MATRIX

| Risk Category | Potential Impact         | Mitigation Strategy                                                                           |
| :------------ | :----------------------- | :-------------------------------------------------------------------------------------------- |
| **Legal**     | MoH License revocation   | Automated license expiry tracking and preemptive warnings to Agencies.                        |
| **Financial** | Stripe payout delays     | Maintaining a liquidity buffer and providing transparent status messages in Agency Dashboard. |
| **Geo**       | PostGIS performance lag  | Implementing multi-level caching (Redis) for frequently queried polygon intersections.        |
| **Safety**    | Physical threat to nurse | Mandatory "Check-in/Check-out" via GPS and the Shield/Blackbox emergency protocol.            |

---

## 📅 24. EXPANDED 24-MONTH ROADMAP

### Year 1: Building the Core (Phases 1-10)

- **Months 1-3:** Focus on B2B Onboarding and OSM-based Geo-Polygon drawing tools.
- **Months 4-6:** Launch Dispatch Engine v1 and Stripe Escrow logic.
- **Months 7-12:** Scale to 3 major cities, implement AI Copilot v1.

### Year 2: Ecosystem Intelligence (Phases 11-20)

- **Months 13-18:** IoT Wearable integration for remote vitals monitoring.
- **Months 19-24:** Advanced AI for epidemic heatmapping and automatic agency performance gamification.

---

## 📖 25. GLOSSARY OF TERMS

- **Aggregator Model (B2B2C):** A business structure where Wateen aggregates independent licensed entities (Agencies) rather than individual freelancers.
- **Blackbox:** A high-security encrypted logging module for medical and legal incident resolution.
- **Coverage Polygon:** A geo-spatial boundary (PostGIS Polygon) defining an Agency's operational territory.
- **Destination Charge:** A Stripe Connect transaction type where the platform takes a fee and the remainder goes to a connected account.
- **Dispatch Mode:** The operational setting determining how a visit is assigned (Manual Assignment vs. Automatic Polling).
- **Escrow:** The temporary holding of patient funds by Wateen until a visit is verified as completed.
- **PostGIS:** A spatial database extender for PostgreSQL used for high-performance geography calculations.
- **RTL (Right-to-Left):** The technical and design adaptation for languages like Arabic where the layout is mirrored.

---

## 🌍 26. i18n & LOCALIZATION STRATEGY (ARABIC FOCUS)

### 26.1 RTL Design Philosophy

- **Mirroring:** All UI layouts (sidebar, icons, text alignment) mirror automatically based on the detected locale.
- **Typography:** Dual-font system using `Inter` for English/Technical terms and `Amiri` or `Outfit` for professional Arabic display.
- **Logical Properties:** Strictly using CSS logical properties (e.g., `margin-inline-start`) instead of physical properties (`margin-left`).

### 26.2 Translation Management

- **System:** Using `i18next` or Next.js built-in internationalization.
- **Quality:** All medical terms are reviewed by local health professionals to ensuring clinical accuracy in the Arabic dialect.

---

## 🔒 27. DATA GOVERNANCE & PRIVACY (EGYPTIAN LAW)

### 27.1 Data Sovereignty

In compliance with the Egyptian Data Protection Law, all PII (Personally Identifiable Information) regarding Egyptian citizens is stored in repositories that allow for regional data residency audits.

### 27.2 Access Control

- **Least Privilege:** Nurses only see patient medical history for the duration of an active visit.
- **Audit Logs:** Every access to a patient record is logged with timestamp, user ID, and IP address.

---

## 🛠️ 28. SERVICE IMPLEMENTATION SPECIFICATIONS (TECHNICAL)

### 28.1 `DispatchEngine` Implementation Logic

- **Trigger:** Triggered by `Visit.created`.
- **Step 1:** Spatial Query - Fetch `AgencyProfile` where `coverage_polygon__intersects`.
- **Step 2:** Scoring - Apply weights: `Rating(0.5) + Capacity(0.3) + HistoricalResponse(0.2)`.
- **Step 3:** Execution - If `Agency.dispatch_mode == AUTO`, broadcast to all online nurses. If `MANUAL`, notify Agency Admin.
- **Fallback:** Set Celery timeout for 5 minutes. If no response, repeat with the next best-scored agency.

### 28.2 `Blackbox` Data Security

- **Event:** Triggered by SOS or Critical Stage (e.g., Medication Admin).
- **Processing:** Audio stream is partitioned and encrypted using Agency’s unique key + Platform Master key.
- **Storage:** Stored in S3-compatible encrypted buckets. Metadata stored in `blackbox_log` table.

---

## ⚠️ 29. EXHAUSTIVE EDGE CASE SCENARIOS

### 29.1 The "Overlapping Polygons" Dilemma

- **Scenario:** Two agencies cover the same patient coordinates.
- **Resolution:** System prioritizes the one with higher relative capacity and rating.

### 29.2 The "Nurse Connection Drop" during Visit

- **Scenario:** Nurse loses internet while uploading vital signs.
- **Resolution:** App uses `IndexedDB` (for PWA) or Local Storage to cache data packets. Mapped to a "Pending Sync" status in the UI.

### 29.3 The "In-Transit Cancellation"

- **Scenario:** Patient cancels after the nurse has traveled 50% of the distance.
- **Resolution:** Fixed cancellation fee + distance fee (calculated via GPS travel history) is charged to the patient and settled to the Agency.

### 29.4 The "Multiple SOS" Scenario

- **Scenario:** Both Patient and Nurse trigger Panic button simultaneously.
- **Resolution:** Criticality score set to 11/10. System auto-dials the emergency contact of both parties and sends location to the nearest security hub.

---

## 📅 30. DETAILED MONTHLY ROADMAP (YEAR 1)

### Month 1: Project Genesis

- **W1:** Env setup, Docker orchestration, Django 5 core initialization.
- **W2:** CustomUser identity model with RBAC (Patient, Agency, Nurse, Admin).
- **W3:** JWT Authentication & Refresh token rotation implementation.
- **W4:** Basic UI scaffolding with Next.js and Tailwind design tokens.

### Month 2: B2B Onboarding

- **W5:** Agency Registration API & Document Upload (S3 integration).
- **W6:** SuperAdmin KYC Verification Queue (Backend + Dashboard).
- **W7:** Agency SaaS Dashboard - Basic CRUD for Agency settings.
- **W8:** Nurse Invitation System (Email/SMS verification).

### Month 3: Geospatial Mastery

- **W9:** OpenStreetMap & `react-leaflet` setup with `leaflet-geoman` drawing tools.
- **W10:** Spatial Query optimization (GIST Indexes, ST_Intersects logic).
- **W11:** Patient-facing "Find Agency" results page.
- **W12:** Map layout optimization for RTL display.

### Month 4: The Dispatch Engine

- **W13:** Visit Request protocol v1 (Creation, Pricing Snapshot).
- **W14:** Real-time sockets (Django Channels + Redis).
- **W15:** Manual Dispatching interaction for Agency Admins.
- **W16:** Auto-dispatch polling logic for High-Priority visits.

### Month 5: Fintech & Escrow

- **W17:** Stripe Connect Destination Charges integration.
- **W18:** Escrow logic handlers (Auth -> Capture lifecycle).
- **W19:** Agency Internal Wallet & Transaction history.
- **W20:** Withdrawal request flow & automation.

### Month 6: Scalability & Polish

- **W21:** Blackbox encrypted logging prototype.
- **W22:** AI Copilot Clinical Standard checks v1.
- **W23:** Performance benchmarking with 5000 concurrent Nurse connections.
- **W24:** Final UI/UX glassmorphism pass and micro-animations.

---

## 🛠️ 31. EXHAUSTIVE MAINTENANCE & OPS CHECKLIST

### 31.1 Weekly SOPs

| Task                        | Frequency | Priority |
| :-------------------------- | :-------- | :------- |
| Prune Redis Keys            | Weekly    | Medium   |
| Review Sentry Error Spikes  | Daily     | High     |
| Database Vacuum (Analyze)   | Weekly    | Low      |
| Rotate Dev Environment Keys | Weekly    | Low      |

### 31.2 Monthly SOPs

| Task                          | Frequency | Priority |
| :---------------------------- | :-------- | :------- |
| Security Image Scan (Docker)  | Monthly   | High     |
| Review Agency Payout Accuracy | Monthly   | High     |
| Update i18n Medical Terms     | Monthly   | Medium   |
| Penetration Test (Basic)      | Monthly   | Medium   |

---

## 📡 32. EXHAUSTIVE API STATUS CODE REFERENCE

| Status Code | Code Name         | Description                                                             | Recommended Client Action                      |
| :---------- | :---------------- | :---------------------------------------------------------------------- | :--------------------------------------------- |
| `200`       | OK                | Request succeeded.                                                      | Proceed to next UI state.                      |
| `201`       | Created           | Resource (Visit/Agency) established.                                    | Show success toast + Redirect.                 |
| `400`       | Bad Request       | Validation failure (Missing fields/Invalid Bio).                        | Highlight relevant input fields.               |
| `401`       | Unauthorized      | Valid token missing or expired.                                         | Trigger Refresh token / Force Logout.          |
| `403`       | Forbidden         | User lacks Role permissions (e.g. Patient trying to access Agency API). | Show Access Denied UI.                         |
| `404`       | Not Found         | Resource or Geo-Polygon not available in area.                          | Show "Service Not Available" state.            |
| `429`       | Too Many Requests | Rate limit exceeded.                                                    | Exponential backoff on client side.            |
| `500`       | Server Error      | Critical failure in Dispatch or Payment logic.                          | Show "Medical Services Down" emergency screen. |

---

## 🎨 33. DESIGN TOKENS & VISUAL SPECIFICATION

### 33.1 Primary Color Palette

- **Wateen Blue:** `#0066FF` (HSL 214, 100%, 50%) - Primary brand color.
- **Trust Green:** `#00C853` (HSL 145, 100%, 39%) - Success/Completed states.
- **Urgent Amber:** `#FFB300` (HSL 42, 100%, 50%) - Pending/Warning states.
- **Danger Red:** `#D50000` (HSL 0, 100%, 42%) - SOS/Canceled states.

### 33.2 Typography Scaffolding

- **Heading 1:** 40px / Semi-Bold / Letter Spacing: -0.02em.
- **Heading 2:** 32px / Semi-Bold / Letter Spacing: -0.01em.
- **Body Copy:** 16px / Regular / Line Height: 1.6.

---

## 🏗️ 34. INFRASTRUCTURE & ORCHESTRATION (CONCEPTUAL)

### 34.1 Kubernetes Architecture

- **Deployment:** `wateen-api` (Django), `wateen-web` (Next.js SSR).
- **StatefulSet:** `wateen-postgres-postgis`, `wateen-redis-cluster`.
- **CronJobs:** `daily-agency-settlement`, `weekly-backup-pruning`.

### 34.2 Security Hardening (WAF Rules)

- **Rule 1:** Block IPs with >100 registration attempts per hour.
- **Rule 2:** SQL Injection & XSS payload scrubbing via Nginx/Cloudflare.
- **Rule 3:** Geo-blocking IPs outside of authorized MENA territories (optional).

---

## 📄 35. REVISION HISTORY & CHANGELOG

| Version | Date     | Author   | Description                              |
| :------ | :------- | :------- | :--------------------------------------- |
| 1.0     | Jan 2026 | Dev Team | Initial P2P architecture.                |
| 2.0     | Jan 2026 | Dev Team | Added Basic Payments.                    |
| 3.0     | Feb 2026 | Dev Team | PostGIS integration for coverage.        |
| 4.0     | Feb 2026 | Dev Team | Pivot to B2B2C Aggregator Model.         |
| 5.0     | Feb 2026 | Dev Team | Exhaustive Master PRD for AI-Native Dev. |

---

## 📑 36. CONCLUSION

Wateen is not just an app; it is the **digital protocol** for Egyptian healthcare. By combining the rigid compliance of a B2B SaaS with the dynamic speed of a B2C Marketplace, we create a sustainable, high-trust ecosystem for agencies, patients, and the state.

---

**Prepared By:** Wateen Engineering Team  
**Review Status:** ACTIVE  
**© 2026 Wateen Healthcare Technologies.**
