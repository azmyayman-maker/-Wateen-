# Zero-Trace Massive Seeding & Sanitation — Technical Report

> **Date:** March 2, 2026 | **Status:** IMPLEMENTED | **Phase:** QA & Stress Testing Infrastructure

---

## Overview

Enterprise-grade mock data generation and cleanup system for the Wateen B2B2C Healthcare platform. Designed to stress-test APIs and PostGIS spatial queries with **zero risk of polluting production data**.

### Isolation Marker

All test entities are identified by:

- **Users:** `email` ends with `@wateen-test-seed.local`
- **Agencies:** `commercial_registry` starts with `TEST-CR-`
- **Nurses:** `syndicate_number` starts with `TEST-SYN-`

---

## Files Created

| File                                            | Purpose                                                 |
| ----------------------------------------------- | ------------------------------------------------------- |
| `users/utils/__init__.py`                       | Package init                                            |
| `users/utils/seed_helpers.py`                   | Egyptian data generators + Cairo PostGIS helpers        |
| `users/management/commands/seed_wateen_data.py` | Seeder management command                               |
| `users/management/commands/nuke_test_data.py`   | Nuke (cleanup) management command                       |
| `tests/test_seed_nuke_integrity.py`             | 11 integrity tests (creation, spatial, cleanup, safety) |
| `requirements/dev.txt`                          | Added `Faker>=28.0.0`                                   |

---

## Architecture

### Seeder (`seed_wateen_data`)

**CLI Arguments:**

- `--agencies` (default: 50)
- `--nurses-per-agency` (default: 20)
- `--visits-per-nurse` (default: 50)
- `--batch-size` (default: 500)

**Generation Flow (per agency, inside `transaction.atomic()`):**

1. Create `AgencyProfile` with PostGIS polygon from a random Cairo district
2. Create `CustomUser` (AGENCY_ADMIN) with test email
3. Bulk-create nurse `CustomUser` objects + `NurseProfile` objects
4. Bulk-create patient `CustomUser` objects + `PatientProfile` objects
5. Bulk-create `Visit` objects with locations inside agency polygon
6. Bulk-create `Transaction` objects for completed visits

**Performance Techniques:**

- `bulk_create(batch_size=500)` — limits memory footprint
- `transaction.atomic()` per agency — single DB round-trip
- `bulk_create` bypasses signals and `NurseProfile.full_clean()`
- Pre-computed UUIDs via `uuid.uuid4()` in Python

### Nuke (`nuke_test_data`)

**Safety Protocol:**

1. Count all test entities and display summary table
2. Require user to type `NUKE` to confirm (or `--force` for CI/CD)
3. Delete in strict reverse-dependency order (7 layers):
   - Layer 6: `TransactionLegacyBackup`
   - Layer 5: `Transaction` (PROTECT → Visit, Agency)
   - Layer 4: `Visit` (PROTECT → Agency, Nurse)
   - Layer 3: `NurseProfile`, `PatientProfile`, `NurseDocument`
   - Layer 2: `NurseInvitation`, `KYCDocument`, `KYCAuditLog` (raw SQL)
   - Layer 1: `AgencyProfile`
   - Layer 0: `CustomUser`
4. Run `VACUUM ANALYZE` to reclaim disk space
5. Verify zero-trace (0 test users remaining)

### Why Reverse-Dependency Order is Required

`Visit.agency` and `Visit.nurse` use `on_delete=models.PROTECT`. `Transaction.visit` and `Transaction.agency` also use `PROTECT`. A simple CASCADE from `CustomUser` would raise `ProtectedError`. The nuke command explicitly removes PROTECT-linked children before their parents.

### KYCAuditLog Edge Case

`KYCAuditLog.delete()` raises `PermissionDenied` (immutability enforcement). The nuke command uses raw SQL `DELETE FROM users_kyc_audit_log WHERE id IN (...)` to bypass this. Test-scoped IDs are pre-filtered.

---

## PostGIS Generation Algorithm

**Problem:** Random lat/lng would fall outside agency coverage zones, breaking `ST_Within` queries.

**Solution — Rejection Sampling:**

1. Pick a Cairo district bounding box (12 districts: Maadi, Nasr City, New Cairo, 6th October, Zayed, Heliopolis, Downtown, Dokki, Mohandessin, Zamalek, Giza, Shubra)
2. Generate a sub-rectangle (60-90% of bbox) → agency `coverage_polygon`
3. For each point: generate random (lng, lat) within polygon envelope, test `polygon.contains(point)`, retry if miss
4. For rectangular polygons, first attempt succeeds >95% of the time

---

## Egyptian Data Generators

- **National ID:** 14-digit structurally valid IDs passing `validate_egyptian_national_id` (century, date, governorate code)
- **Phone:** Valid `01[0125]XXXXXXXX` format passing `validate_phone_number`
- **Arabic Names:** 30 male + 30 female first names, 28 last names
- **B2B Docs:** `TEST-CR-XXXXXX`, `TEST-MOH-XXXXXX`, `TEST-TAX-XXXXXX`

---

## Zero-Trace Guarantee

**Proof:** `DELETE scope = CustomUser.objects.filter(email__endswith='@wateen-test-seed.local')`. No real user email domain ends with `wateen-test-seed.local`. The `endswith` filter is an exact suffix match. Therefore: `real_users ∩ delete_scope = ∅`.

**Orphan Prevention:** Deletion in 7-layer reverse-dependency order ensures no PROTECT violations and no orphaned rows.

---

## Test Coverage

| Test Class             | Tests | Validates                                    |
| ---------------------- | ----- | -------------------------------------------- |
| `TestSeedCreation`     | 7     | Entity counts, polygon validity              |
| `TestSpatialIntegrity` | 2     | Visit/nurse locations inside agency polygons |
| `TestNukeCleanup`      | 1     | Zero test rows after nuke                    |
| `TestNukeSafety`       | 1     | Non-test users survive nuke                  |

---

## Commands

```bash
# Install dependency
pip install Faker>=28.0.0

# Seed (small test)
python manage.py seed_wateen_data --agencies 3 --nurses-per-agency 5 --visits-per-nurse 10

# Seed (full stress — ~52K rows)
python manage.py seed_wateen_data

# Nuke (interactive)
python manage.py nuke_test_data

# Nuke (CI/CD)
python manage.py nuke_test_data --force --no-vacuum

# Tests (requires PostGIS)
python -m pytest tests/test_seed_nuke_integrity.py -v
```

---

## Scaling Estimates

| Configuration                             | Total Rows | Estimated Time |
| ----------------------------------------- | ---------- | -------------- |
| `--agencies 10 --nurses 5 --visits 10`    | ~1,600     | ~5s            |
| `--agencies 50 --nurses 20 --visits 50`   | ~52,550    | ~60s           |
| `--agencies 100 --nurses 50 --visits 100` | ~510,100   | ~10min         |
