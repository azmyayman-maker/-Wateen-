# API Contracts: Redis Cloud Integration

**Feature**: 003-redis-cloud-integration  
**Date**: 2026-02-18

## Overview

This feature does not introduce new API endpoints. It is an infrastructure configuration change that affects:

- Cache backend configuration
- Channel layer configuration
- Docker orchestration

## Existing Endpoints Affected

No changes to existing API endpoint contracts. The following endpoints will continue to work as before, with improved performance from Redis Cloud caching:

| Endpoint          | Change                                                 |
| ----------------- | ------------------------------------------------------ |
| All API endpoints | No contract changes - cache backend transparent to API |

## Management Command

### test_redis

A new management command for verifying Redis Cloud connectivity.

**Command**:

```bash
python manage.py test_redis
```

**Output on Success**:

```
Testing Redis Cloud connectivity...
Cache: OK
Channel Layer: OK
Redis Connected Successfully
```

**Output on Failure**:

```
Testing Redis Cloud connectivity...
Cache: FAILED - Connection refused
Channel Layer: SKIPPED (cache failed)
Redis connection failed: Connection refused
```

**Exit Codes**:

- 0: All tests passed
- 1: One or more tests failed

## WebSocket Events

No changes to WebSocket event contracts. Channel layer communication remains transparent to consumers.

## No OpenAPI Changes Required

Since no new API endpoints are introduced, no OpenAPI specification updates are needed.
