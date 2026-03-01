# B2B2C Migration Quickstart

## 1. Environment Setup

_Prerequisites:_ Ensure Docker and Docker Compose are installed and running.

1. **Clone & Branch:**

   ```bash
   git fetch origin
   git checkout 005-b2b2c-architecture-migration
   ```

2. **Environment Variables:**
   Copy `.env.example` to `.env` and configure stripe/mapbox keys if you have sandbox keys (not strictly required for initial local dev mocked services).
   ```bash
   cp .env.example .env
   ```

## 2. Database Migrations & Seed

Because this pivots the schema from P2P to B2B2C, you must run migrations to instantiate the new `AGENCY_PROFILE` and adapt the `NURSE_PROFILE`.

1. **Start infrastructure (Postgres + Redis):**

   ```bash
   docker-compose up -d db redis
   ```

2. **Run Migrations:**

   ```bash
   docker-compose run --rm backend python manage.py makemigrations
   docker-compose run --rm backend python manage.py migrate
   ```

3. **Seed Data (Optional but recommended):**
   Run the idempotency script to port legacy nurses to the "Wateen Internal Agency".
   ```bash
   # Command to be determined once script is written, typically:
   # docker-compose run --rm backend python manage.py seed_b2b2c
   ```

## 3. Running the Stack

To spin up the full stack (Next.js Frontend, Django Backend, Celery Workers, Redis):

```bash
docker-compose up --build
```

- **Backend API**: `http://localhost:8000`
- **Frontend App/Dashboard**: `http://localhost:3000`
- **Mailpit (Mock Emails)**: `http://localhost:8025`

## 4. Development Guides

- Reference `data-model.md` for the ORM classes.
- Reference `contracts/api.md` for B2B API endpoints.
- Read `research.md` if you are confused as to why Mapbox or Stripe were chosen.
