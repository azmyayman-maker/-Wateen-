# Quickstart: Phase 1 QA, Security & Validation

**Branch**: `011-phase1-qa-security`

## Prerequisites

- Python 3.11+ with virtual environment activated
- PostgreSQL 16 + PostGIS 3.4 running (via Docker or local)
- `DATABASE_URL` set in `.env`
- GDAL installed (Windows: OSGeo4W; Linux/Docker: `libgdal-dev`)

## Run All QA Tests

```bash
# 1. Activate venv
source .venv/bin/activate  # Linux
.venv\Scripts\activate     # Windows

# 2. Check migration integrity
python manage.py migrate --check

# 3. Run the full QA test suite
pytest users/tests/test_b2b2c_integrity.py -v
pytest users/tests/test_migrations.py -v
pytest users/tests/test_permissions.py -v
pytest visits/tests/test_security_rbac.py -v

# 4. Run all tests together
pytest -v

# 5. Static analysis
ruff check .
mypy users/ visits/ --ignore-missing-imports
```

## Expected Results

- All pytest tests: **PASS** (exit code 0)
- `migrate --check`: **exit code 0** (no unapplied migrations)
- `ruff check .`: **0 errors/warnings**
- `mypy`: Best-effort (not blocking, but target 0 errors in users/ and visits/)

## Report Location

After execution: `specs/011-phase1-qa-security/report.md`
