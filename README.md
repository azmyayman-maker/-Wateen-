# Wateen (وَتِين) — The Nerve System of Home Healthcare

<p align="center">
  <img src="[docs/assets/wateen-logo.png](https://github.com/azmyayman-maker/-Wateen-/blob/main/icon.ico)" alt="Wateen Logo" width="200" />
</p>

[![Build Passing](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat&logo=github-actions)](https://github.com/wateen/wateen/actions)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Django 5.2](https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django)](https://www.djangoproject.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-000000?style=flat&logo=next.js)](https://nextjs.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-336791?style=flat&logo=postgresql)](https://postgis.net/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![RTL Native](https://img.shields.io/badge/RTL-Native%20for%20Arabic-FF6B35?style=flat)](https://github.com/wateen/wateen)

---

## Elevator Pitch

**Wateen (وَتِين)** is an Enterprise-Grade B2B2C HealthTech SaaS & Aggregator Platform architected specifically for the Egyptian healthcare market. Built to solve the fragmentation, legal compliance chaos, and dispatching inefficiencies that plague home healthcare in Egypt, Wateen operates on a **Multi-Tenant SaaS model sold to Licensed Nursing Agencies** to strictly comply with Egyptian Ministry of Health (MoH) Law 151/2020.

Through our platform, **licensed nursing agencies** manage their employed nurses, while **patients** request verified medical services directly from these vetted agencies. The result is a fully compliant, geo-spatially intelligent ecosystem that transforms how home healthcare is delivered across Egypt — from Cairo to Alexandria to Luxor.

---

## Architectural Highlights

### Multi-Tenant Row-Level Security

Wateen implements **strict multi-tenancy** at the database level using row-level isolation. Every core entity — `Patient`, `Nurse`, `Visit` — is tied to an `agency_id` foreign key. The Django ORM leverages custom querysets and tenant-scoped managers to guarantee that agency A never sees agency B's patient records, nurse credentials, or financial transactions.

```python
class VisitQuerySet(models.QuerySet):
    def for_agency(self, agency):
        return self.filter(agency=agency)
```

### Geo-Spatial Dispatch Engine

The heart of Wateen's operational logic is a **dual-layer geo-spatial dispatch engine**:

1. **PostGIS Polygon Matching**: When a patient submits a request, the system queries `ST_Intersects(coverage_polygon, patient_location)` to identify all agencies with geographic coverage in the patient's area.
2. **Redis Geo-Indexing**: For Tier-2 nurse-to-patient dispatch, we use Redis `GEOSEARCH` commands for sub-millisecond proximity lookups, finding the nearest available nurses within a configurable radius.

### 100% Open-Source Mapping Stack

Wateen made a deliberate strategic pivot away from proprietary mapping providers to eliminate vendor lock-in and reduce operational expenditure to zero:

| Layer         | Technology                                                  |
| ------------- | ----------------------------------------------------------- |
| Base Maps     | **OpenStreetMap (OSM)** tiles via Leaflet                   |
| Frontend Maps | **react-leaflet** with **leaflet-geoman** for draw controls |
| Geocoding     | **Nominatim** (OSM-based)                                   |
| Routing       | **OSRM (Open Source Routing Machine)** for ETA calculations |
| Spatial DB    | **PostGIS 3.4** on PostgreSQL 16                            |

No Mapbox. No Google Maps. No licensing fees. Ever.

---

## Tech Stack

### Backend Core

| Component      | Technology                                |
| -------------- | ----------------------------------------- |
| Language       | **Python 3.11+**                          |
| Framework      | **Django 5.2** (ASGI-ready with Daphne)   |
| API Layer      | **Django REST Framework 3.15**            |
| Authentication | **SimpleJWT** with refresh token rotation |
| Task Queue     | **Celery** with Redis broker              |
| Validation     | **django-decouple** for 12-factor config  |

### Database & Spatial

| Component      | Technology                                      |
| -------------- | ----------------------------------------------- |
| Primary DB     | **PostgreSQL 16** with **PostGIS 3.4**          |
| Caching        | **Redis 7** (hybrid in-memory fallback for dev) |
| Channel Layers | **channels_redis** for WebSocket real-time      |
| GIS Fields     | `PointField`, `PolygonField` (SRID 4326)        |

### Frontend & PWA

| Component | Technology                                     |
| --------- | ---------------------------------------------- |
| Framework | **Next.js 14** (App Router)                    |
| Language  | **TypeScript 5.x**                             |
| Styling   | **Tailwind CSS 3.4**                           |
| Animation | **Framer Motion 11.0.0**                       |
| Maps      | **react-leaflet 4**, **Leaflet Geoman**        |
| Icons     | **Lucide React**                               |
| RTL       | Native Arabic support with `next/font` (Cairo) |

### Infrastructure & DevOps

| Component        | Technology                      |
| ---------------- | ------------------------------- |
| Containerization | **Docker** + **Docker Compose** |
| Reverse Proxy    | **Nginx 1.25** (Alpine)         |
| ASGI Server      | **Daphne**                      |
| Linting          | **Ruff**                        |
| Testing          | **pytest** with pytest-django   |
| Code Quality     | **flake8**                      |

---

## System Architecture Diagram

```mermaid
graph TD
    subgraph "Patient Layer"
        P[Patient App PWA] -->|HTTPS/JSON| LB[Load Balancer]
        P -->|WebSocket| WS[Redis Channel Layer]
    end

    subgraph "API Gateway"
        LB -->|Django| API[Django REST Framework]
        API -->|JWT Auth| AUTH[SimpleJWT]
    end

    subgraph "Core Services"
        API -->|Visit Request| MATCH[Geo-Matching Service]
        MATCH -->|ST_Intersects| PG[(PostGIS)]
        MATCH -->|GEOSEARCH| REDIS[(Redis Geo-Index)]

        API -->|Pricing| PRICE[Rule-Based Pricing Engine]
        PRICE -->|Distance Fee| OSRM[OSRM API]

        API -->|Payment| PAY[Stripe Connect]
        PAY -->|Escrow| TRANS[Transaction Split]
    end

    subgraph "Dispatch Engine"
        MATCH -->|Eligible Agencies| DISPATCH[Dispatch Engine]
        DISPATCH -->|Auto/Manual| AGENCY[Agency Dashboard]
        DISPATCH -->|Push Notification| NURSE[Nurse PWA]
    end

    subgraph "Real-Time Layer"
        WS -->|Channel Group| REDIS
        REDIS -->|visit_request| NURSE
        REDIS -->|agency_alert| AGENCY
    end

    subgraph "Background Tasks"
        API -->|Celery Task| CELERY[Celery Worker]
        CELERY -->|Settlement| TRANS
        CELERY -->|Audit Log| LOG[Safety Blackbox]
    end

    subgraph "Agency Layer"
        AGENCY -->|Manage| NURSE
        AGENCY -->|View| PATIENT_DB[Patient Records]
    end
```

---

## Deep-Tech Features

### The Shield: Encrypted Audio/Metadata Blackbox

Wateen implements a **Safety Blackbox** system for every visit — an encrypted, immutable audit log that captures:

- **Audio metadata**: Call start/end timestamps, duration, parties involved (no actual audio storage to protect privacy)
- **Geospatial Trajectory**: Nurse route from dispatch to patient location
- **Visit state transitions**: Every status change with millisecond timestamps
- **Dispute resolution**: Tamper-proof evidence for MoH compliance audits

This system serves as both **physical safety assurance** for nurses and **legal evidence** for dispute resolution.

### Fintech Escrow: Stripe Connect Destination Charges

Financial flows are handled via **Stripe Connect with Destination Charges**:

```
Total Payment (EGP)
       │
       ├──► 15% Platform Take-Rate → Wateen Revenue
       │
       └──► 85% Agency Revenue → Agency Stripe Connect Account
```

The `PaymentService` (`visits/services/payment.py:14`) creates payment intents that automatically split funds at the point of capture, eliminating manual reconciliation and ensuring legal compliance for healthcare billing in Egypt.

### AI Copilot: Clinical Standards Enforcement

Wateen's pricing and dispatch engines are **AI-ready** by design:

- **Pricing Factor**: `ai_surge_coefficient` field in the `Visit` model — placeholder for ML-driven demand pricing
- **Estimate Logging**: `EstimateLog` model captures every price query for future model training
- **Clinical Rules Engine**: Future integration point for enforcing MoH-mandated clinical protocols algorithmically

---

## Project Structure

```
wateen/
├── config/                          # Django project configuration
│   ├── asgi.py                     # ASGI application entry
│   ├── settings.py                  # All settings with PostGIS/Redis
│   ├── urls.py                     # Root URL routing
│   └── redis_utils.py              # Hybrid Redis/InMemory fallback
│
├── users/                          # Multi-tenant user profiles
│   ├── models.py                   # Agency, Nurse, Patient profiles
│   ├── services/
│   │   └── kyc_service.py          # KYC document verification
│   └── migrations/
│
├── visits/                         # Core domain: visits, pricing, dispatch
│   ├── models.py                   # Visit, ServiceType, Transaction
│   ├── services/
│   │   ├── dispatch.py            # Tier-2 nurse dispatch logic
│   │   ├── matching.py             # Redis geo-matching engine
│   │   ├── pricing.py              # Rule-based + ML-ready pricing
│   │   └── payment.py              # Stripe Connect escrow
│   ├── consumers.py                # WebSocket consumers
│   ├── serializers.py              # DRF serializers
│   └── views.py                    # API endpoints
│
├── frontend/                       # Next.js 14 App Router
│   ├── src/
│   │   ├── app/                    # Pages (dashboard, public, auth)
│   │   ├── components/
│   │   │   ├── map/                # Leaflet + Geoman components
│   │   │   ├── dashboard/         # Agency & Admin dashboards
│   │   │   └── ui/                 # shadcn/ui-style components
│   │   └── lib/                    # i18n, utilities
│   └── package.json
│
├── docker/                         # Docker configuration
│   ├── docker-compose.yml          # Production stack
│   ├── Dockerfile                  # Python/Django image
│   ├── Dockerfile.frontend        # Next.js standalone build
│   ├── nginx.conf                  # Reverse proxy config
│   └── init-db.sql                 # PostGIS extension init
│
├── tests/                          # Integration & infrastructure tests
│   ├── unit/                       # Unit tests
│   └── integration/                # Full-stack tests
│
├── manage.py                       # Django management CLI
├── docker-compose.yml              # Root-level compose (Hostinger deploy)
├── pytest.ini                      # Test configuration
└── README.md                       # This file
```

---

## Quick Start & Local Development

### Prerequisites

- **Docker 24+** with Docker Compose
- **Python 3.11+** (for local development without Docker)
- **PostgreSQL 16** with PostGIS extension (or use Docker)
- **Redis 7** (or use Docker)

### Clone & Environment Setup

```bash
# Clone the repository
git clone https://github.com/wateen/wateen.git
cd wateen

# Create environment file from template
cp .env.example .env
```

### Configure Environment Variables

```bash
# .env — Development Configuration
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Database (PostGIS)
DATABASE_URL=postgis://wateen_dev:devpassword@localhost:5432/wateen_dev

# Redis
REDIS_URL=redis://localhost:6379/1

# Stripe (Use test keys)
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Spin Up with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# View logs
docker-compose logs -f web

# Run migrations inside the container
docker-compose exec web python manage.py migrate

# Create a superuser
docker-compose exec web python manage.py createsuperuser

# Seed initial data (optional)
docker-compose exec web python manage.py loaddata fixtures/initial.json
```

### Access the Application

| Service            | URL                                  |
| ------------------ | ------------------------------------ |
| Frontend (Next.js) | http://localhost:3000                |
| Backend API        | http://localhost:8000/api/v1         |
| Admin Panel        | http://localhost:8000/admin          |
| Health Check       | http://localhost:8000/api/v1/health/ |

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run linting
ruff check .

# Run specific test suite
pytest visits/tests/test_visit_lifecycle.py -v
```

---

## Legal & Security Compliance

### Egyptian Law 151/2020 (Data Privacy)

Wateen is architected for full compliance with Egypt's data protection legislation:

| Requirement                  | Implementation                                                                            |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| **Explicit Consent**         | Consent logs captured at patient registration, encrypted and stored in `ConsentLog` model |
| **Local Data Residency**     | All PostgreSQL data stored on servers within Egypt (configurable region)                  |
| **PII Masking**              | National ID, phone numbers masked in API responses unless explicitly required             |
| **Right to Erasure**         | Soft-delete + hard-delete pipeline for patient data upon request                          |
| **Data Breach Notification** | Automated alerting to DPO and affected parties within 72-hour mandate                     |

### Security Hardening

- **Argon2 Password Hashing** (primary) with PBKDF2 fallback
- **HTTPS Only** in production with HSTS preload
- **CSRF/AUTH Cookie Flags**: `Secure`, `HttpOnly`, `SameSite=Strict`
- **JWT Token Rotation**: Short-lived access tokens (60 min), long-lived refresh tokens (7 days) with blacklist support

---

## Community & Support

- **Documentation**: [docs.wateen.live](https://docs.wateen.live)
- **Issue Tracker**: [github.com/wateen/wateen/issues](https://github.com/wateen/wateen/issues)
- **Discussion Forum**: [community.wateen.live](https://community.wateen.live)

---

## License

**MIT License** — See [LICENSE](LICENSE) for full text.

```
MIT License

Copyright (c) 2024 Wateen Health Technologies

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  <strong>Wateen (وَتِين)</strong> — Building the nervous system of home healthcare in Egypt.<br />
  <em>Licensed. Compliant. Local.</em>
</p>
