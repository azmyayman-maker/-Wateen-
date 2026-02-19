# Quickstart: Infrastructure Verification

**Feature**: 005-infra-verification  
**Date**: 2026-02-19

## Prerequisites

- Docker Desktop running
- PostgreSQL + PostGIS container running (`wateen_db`)
- Redis container running (`wateen_redis`)
- Python 3.11+ with virtual environment activated

## Quick Commands

### Verify All Infrastructure

```bash
python scripts/verify_infra.py
```

### Verify Database Only

```bash
python scripts/verify_local_db.py
```

### Verify Cache Only

```bash
python scripts/verify_local_redis.py
```

### Run Test Suite

```bash
pytest tests/test_infra.py -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgres://...` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/1` | Redis connection string |
| `VERIFICATION_TIMEOUT` | `5` | Connection timeout in seconds |
| `VERIFICATION_OUTPUT` | `both` | Output format: `console`, `json`, `both` |
| `VERIFICATION_JSON_PATH` | `./verification-report.json` | Path for JSON output |

## Output

### Console Output

```
──────────────────────────────
Infrastructure Verification
──────────────────────────────
[✓] Database: PASS (15ms)
    PostGIS: 3.4.0
    CRUD: create ✓ read ✓ delete ✓
[✓] Cache: PASS (2ms)
    Operations: set ✓ get ✓ delete ✓
    Pub/Sub: subscribe ✓ publish ✓ receive ✓
──────────────────────────────
Overall: PASS (117ms)
Report: ./verification-report.json
```

### JSON Output (`verification-report.json`)

```json
{
  "timestamp": "2026-02-19T10:30:00Z",
  "overall_status": "pass",
  "total_duration_ms": 117,
  "components": {
    "database": {
      "component": "database",
      "status": "pass",
      "latency_ms": 15,
      "postgis_version": "3.4.0",
      "crud_status": { "create": true, "read": true, "delete": true }
    },
    "cache": {
      "component": "cache",
      "status": "pass",
      "latency_ms": 2,
      "operations": { "set": true, "get": true, "delete": true },
      "pubsub_status": { "subscribe": true, "publish": true, "receive": true }
    }
  }
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Verify Infrastructure
  run: python scripts/verify_infra.py
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    REDIS_URL: ${{ secrets.REDIS_URL }}
    VERIFICATION_OUTPUT: json
    VERIFICATION_JSON_PATH: reports/verification.json

- name: Upload Verification Report
  uses: actions/upload-artifact@v3
  with:
    name: verification-report
    path: reports/verification.json
```

## Troubleshooting

### Database Connection Failed

1. Check Docker containers: `docker ps`
2. Verify PostgreSQL is running: `docker logs wateen_db`
3. Check connection string: `echo $DATABASE_URL`

### Cache Connection Failed

1. Check Redis container: `docker ps | grep redis`
2. Test directly: `redis-cli ping`
3. Check connection string: `echo $REDIS_URL`

### PostGIS Extension Missing

```bash
docker exec -it wateen_db psql -U postgres -d wateen -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | One or more checks failed |
