# Data Model: Infrastructure Verification

**Feature**: 005-infra-verification  
**Date**: 2026-02-19

## Entities

### VerificationResult

Base structure for all verification checks.

| Field | Type | Description |
|-------|------|-------------|
| component | string | Component name (database, cache) |
| status | enum | `pass`, `fail`, `warning` |
| latency_ms | number | Operation latency in milliseconds |
| timestamp | datetime | ISO 8601 timestamp of check |
| details | string | Human-readable details |
| error | string? | Error message if failed |

### DatabaseVerificationResult

Extends VerificationResult for database checks.

| Field | Type | Description |
|-------|------|-------------|
| component | string | Always "database" |
| status | enum | `pass`, `fail`, `warning` |
| latency_ms | number | Connection + query latency |
| timestamp | datetime | ISO 8601 timestamp |
| details | string | Summary of checks performed |
| error | string? | Error message if failed |
| postgis_version | string? | PostGIS version if available |
| crud_status | object? | CRUD operation results |

#### CRUD Status Object

| Field | Type | Description |
|-------|------|-------------|
| create | boolean | Create operation succeeded |
| read | boolean | Read operation succeeded |
| delete | boolean | Delete operation succeeded |

### CacheVerificationResult

Extends VerificationResult for cache checks.

| Field | Type | Description |
|-------|------|-------------|
| component | string | Always "cache" |
| status | enum | `pass`, `fail`, `warning` |
| latency_ms | number | Cache operation latency |
| timestamp | datetime | ISO 8601 timestamp |
| details | string | Summary of checks performed |
| error | string? | Error message if failed |
| operations | object? | Individual operation results |
| pubsub_status | object? | Pub/Sub test results |

#### Operations Object

| Field | Type | Description |
|-------|------|-------------|
| set | boolean | Set operation succeeded |
| get | boolean | Get operation succeeded |
| delete | boolean | Delete operation succeeded |

#### PubSub Status Object

| Field | Type | Description |
|-------|------|-------------|
| subscribe | boolean | Subscription succeeded |
| publish | boolean | Message published |
| receive | boolean | Message received |

### InfrastructureTestReport

Aggregates all verification results.

| Field | Type | Description |
|-------|------|-------------|
| timestamp | datetime | ISO 8601 timestamp |
| overall_status | enum | `pass`, `fail` |
| total_duration_ms | number | Total verification time |
| components | object | Map of component name to VerificationResult |
| summary | string | Human-readable summary |

## State Transitions

Not applicable - verification checks are stateless operations.

## Validation Rules

### Latency Thresholds

| Component | Threshold | Status |
|-----------|-----------|--------|
| Cache ops | < 100ms | pass |
| Cache ops | 100-200ms | warning |
| Cache ops | > 200ms | fail |
| Database connection | < 1000ms | pass |
| Database connection | 1000-5000ms | warning |
| Database connection | > 5000ms | timeout/fail |

### Exit Codes

| Condition | Exit Code |
|-----------|-----------|
| All checks pass | 0 |
| Any check fails | 1 |
| Any warning (no failures) | 0 |
