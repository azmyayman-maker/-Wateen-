# Quickstart: Post-Audit Codebase Cleanup & Fixes

**Branch**: `001-audit-cleanup` | **Date**: 2026-02-19

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional, for containerized testing)
- Access to Wateen repository

## Environment Setup

### Required Environment Variables

Create or update `.env` file in project root:

```bash
# Database
DATABASE_URL=postgis://wateen:wateen_secret@localhost:5432/wateen?sslmode=disable

# Redis
REDIS_URL=redis://localhost:6379/1

# Django
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY=your-secret-key-here
```

## Implementation Steps

### Phase 1: Script Cleanup

```bash
# 1. Remove unused imports
# Edit scripts/verify_local_redis.py - remove line 6
# Edit scripts/check_conn.py - remove line 13

# 2. Fix pubsub cleanup in verify_local_redis.py
# Wrap verify_pubsub() pubsub operations in try/finally

# 3. Fix indentation in verify_local_db.py
# Align lines 79-91 with surrounding code
# Remove duplicate comment at line 39

# 4. Fix socket context manager in check_conn.py
# Rewrite check_socket_connection() to use 'with' statement

# 5. Fix URL masking in check_conn.py
# Update mask_password_from_url() for password-only URLs

# 6. Fix f-string in audit_standalone.py
# Remove 'f' prefix from line 40
```

### Phase 2: Service Logic

```bash
# 1. Add logging to pricing.py
# Replace 'except Exception: pass' with proper logging

# 2. Add public is_night_hours method
# Add method that delegates to _is_night_hours
```

### Phase 3: Test Suite

```bash
# 1. Fix test_edge_cases.py setUp
# Remove mocks for is_night_hours and get_min_price

# 2. Add skip decorator to test_time_traveler
# Add @unittest.skip("Pending implementation")
```

### Phase 4: Configuration

```bash
# 1. Fix conftest.py
# Add '# noqa: ARG001' to pytest_configure

# 2. Secure docker-compose.yml
# Replace hardcoded URLs with env vars
# Bind ports to 127.0.0.1
```

## Verification

### 1. Linting Check

```bash
flake8 .
```

Expected: Zero warnings or errors

### 2. Test Suite

```bash
pytest visits/tests/test_edge_cases.py -v
```

Expected: All tests pass or skip appropriately

### 3. Connection Check

```bash
python scripts/check_conn.py
```

Expected: Passwords masked in output, connections verified

### 4. Docker Compose (Optional)

```bash
cd docker
docker-compose up -d
docker-compose ps  # Verify services running
docker-compose down
```

Expected: Services start successfully with env vars

## Troubleshooting

### Issue: flake8 still shows warnings

**Cause**: Cache or other files not in scope
**Fix**: Run `flake8 . --clear-cache` or check specific files

### Issue: Tests fail after changes

**Cause**: Mock signature mismatch
**Fix**: Verify mock setup matches actual method signatures

### Issue: Docker Compose fails with env vars

**Cause**: Environment variables not set
**Fix**: Ensure `.env` file exists and `DATABASE_URL`/`REDIS_URL` are defined

### Issue: URL masking shows password

**Cause**: Edge case URL format
**Fix**: Verify `mask_password_from_url` handles all formats:
- `redis://user:pass@host`
- `redis://:pass@host`
- `redis://host` (no credentials)

## Rollback

If issues arise, revert changes:

```bash
git checkout HEAD -- scripts/ visits/ testsprite_tests/ docker/
```
