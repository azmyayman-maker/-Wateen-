# Implementation Plan: Post-Audit Codebase Cleanup & Fixes

**Branch**: `001-audit-cleanup` | **Date**: 2026-02-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-audit-cleanup/spec.md`

## Summary

Remediate 8 identified issues from TestSprite Audit Report across scripts, docker configuration, and test suite to achieve zero linting warnings, secure configuration, and passing tests.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django 5.2, Django REST Framework, redis-py, psycopg2, pytest, flake8
**Storage**: PostgreSQL with PostGIS
**Testing**: pytest, unittest
**Target Platform**: Linux server (Docker containers)
**Project Type**: Single Django web application
**Performance Goals**: N/A (remediation task)
**Constraints**: Must pass `flake8 .` with zero warnings; all tests must pass or skip appropriately
**Scale/Scope**: 8 files across 4 categories (scripts, services, tests, docker)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file contains template placeholders only. No project-specific constitution exists yet.

**Gate Status**: PASS - No violations to check against.

## Project Structure

### Documentation (this feature)

```text
specs/001-audit-cleanup/
├── plan.md              # This file
├── research.md          # Phase 0 output (minimal - remediation task)
├── data-model.md        # Phase 1 output (N/A - no data model changes)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (empty - no API changes)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
scripts/
├── verify_local_redis.py   # Remove unused import, add try/finally
├── verify_local_db.py      # Fix indentation, remove duplicate comment
├── check_conn.py           # Remove unused import, socket context manager, fix URL masking
└── audit_standalone.py     # Remove unnecessary f-string prefix

visits/
├── services/
│   └── pricing.py          # Add logging, add public is_night_hours method
└── tests/
    └── test_edge_cases.py  # Fix mocks, add skip decorator

testsprite_tests/
└── conftest.py             # Add noqa comment for unused config param

docker/
└── docker-compose.yml      # Use env vars, bind to localhost
```

**Structure Decision**: Existing Django project structure preserved. Changes are isolated to specific files without structural modifications.

## Complexity Tracking

No constitution violations to justify.

## Implementation Details

### A. Scripts Cleanup (4 files)

#### 1. `scripts/verify_local_redis.py`
| Issue | Fix | Line(s) |
|-------|-----|---------|
| Unused import `urlparse` | Remove line 6 | 6 |
| No pubsub cleanup | Wrap pubsub logic in `try...finally` with `pubsub.unsubscribe()` and `pubsub.close()` | 25-69 |

#### 2. `scripts/verify_local_db.py`
| Issue | Fix | Line(s) |
|-------|-----|---------|
| Duplicate comment | Remove duplicate line 39 | 39 |
| Inconsistent indentation | Align lines 79-91 with surrounding code | 79-91 |

#### 3. `scripts/check_conn.py`
| Issue | Fix | Line(s) |
|-------|-----|---------|
| Unused import `os` | Remove line 13 | 13 |
| No socket context manager | Rewrite lines 61-65 using `with socket.socket(...) as sock:` | 61-65 |
| Password masking edge case | Update `mask_password_from_url` to handle `redis://:pass@host` | 19-35 |

#### 4. `scripts/audit_standalone.py`
| Issue | Fix | Line(s) |
|-------|-----|---------|
| Unnecessary f-string | Remove `f` prefix from line 40 | 40 |

### B. Core Service Logic (1 file)

#### 5. `visits/services/pricing.py`
| Issue | Fix | Line(s) |
|-------|-----|---------|
| Silent exception | Replace `except Exception: pass` with logging | 112-113 |
| No public is_night_hours | Add public method `is_night_hours(self, request_time)` | After line 146 |

### C. Test Suite Fixes (2 files)

#### 6. `visits/tests/test_edge_cases.py`
| Issue | Fix | Line(s) |
|-------|-----|---------|
| Mocking non-existent method | Remove `get_min_price` mock from setUp | 75 |
| Mocking now-public method | Remove `is_night_hours` mock from setUp | 74 |
| Placeholder test | Add `@unittest.skip("Pending implementation")` to `test_time_traveler` | 103 |

#### 7. `testsprite_tests/conftest.py`
| Issue | Fix | Line(s) |
|-------|-----|---------|
| Unused config parameter | Add `# noqa: ARG001` comment | 13 |

### D. Infrastructure Security (1 file)

#### 8. `docker/docker-compose.yml`
| Issue | Fix | Line(s) |
|-------|-----|---------|
| Hardcoded REDIS_URL | Change to `${REDIS_URL}` environment variable | 41 |
| Hardcoded DATABASE_URL | Change to `${DATABASE_URL}` environment variable | 42 |
| External port binding | Change `"6379:6379"` to `"127.0.0.1:6379:6379"` | 91 |
| External port binding | Change `"5432:5432"` to `"127.0.0.1:5432:5432"` | 117 |

## Verification Commands

1. **Linting**: `flake8 .` (expect: 0 warnings/errors)
2. **Tests**: `pytest visits/tests/test_edge_cases.py` (expect: pass or skip)
3. **Connection**: `python scripts/check_conn.py` (expect: passwords masked correctly)
4. **Redis**: `python scripts/verify_local_redis.py` (expect: pass with proper cleanup)
5. **Database**: `python scripts/verify_local_db.py` (expect: pass)

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Environment variables not set for docker-compose | Document requirement in quickstart.md; validate at startup |
| Breaking existing behavior | All changes are additive or corrective; no logic changes |
| Flaky tests | Tests already designed to be isolated; verify before/after |
